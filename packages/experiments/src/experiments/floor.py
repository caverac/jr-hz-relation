r"""Compare the angular-momentum changes of a run with those of its control between two times.

Both runs must have been extracted with :mod:`experiments.tracks` so that the rows of their
tracks are the same particles. For each run the module takes the snapshots nearest to the
two times, computes $L_z = x v_y - y v_x$ of every tracked disk particle in the frame of the
ring sums, and $\Delta L_z$ between the two snapshots. In rings of the cylindrical radius at
the first time it reports the variance of $\Delta L_z$ in the control and in the run, their
ratio, and the exponent of the power law of the variance against $\langle|z|\rangle$ in
quantile bins of $|z|$ at the first time (bins defined on the run and applied to both). The
control's variance is the floor of the run's: what the disk does to itself without the
perturbers, plus the numerical noise. Units are those of the runs: kpc, km/s and kpc/(km/s)
for time.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt

F64 = npt.NDArray[np.float64]
Row = dict[str, float | int | str]
#: Largest gap between a requested time and the nearest extracted snapshot (run units).
TIME_TOLERANCE = 0.003


@dataclass(frozen=True)
class Frame:
    """Angular momentum, radius and height of the tracked disk particles at one time."""

    time: float
    lz: F64
    radius: F64
    abs_z: F64


@dataclass(frozen=True)
class Run:
    """The first frame of a run and the change of L_z of every particle to the second."""

    first: Frame
    delta: F64


def snapshot_near(data: Path, time: float) -> int:
    """Find the extracted snapshot nearest to the time, within the tolerance."""
    candidates = []
    for path in sorted((data / "rings").glob("snap_*.npz")):
        number = int(path.stem.split("_")[1])
        candidates.append((abs(float(np.load(path)["time"][0]) - time), number))
    if not candidates:
        raise ValueError(f"no ring sums in {data}")
    gap, number = min(candidates)
    if gap > TIME_TOLERANCE:
        raise ValueError(f"no snapshot within {TIME_TOLERANCE} of t = {time} in {data}")
    return number


def load_frame(data: Path, number: int, disk_rows: int) -> Frame:
    """Load one snapshot's tracked disk particles in the frame of its ring sums."""
    tracks = np.asarray(np.load(data / "tracks" / f"snap_{number:04d}.npy")[:disk_rows], dtype=np.float64)
    rings = np.load(data / "rings" / f"snap_{number:04d}.npz")
    positions = tracks[:, :3] - rings["center"]
    velocities = tracks[:, 3:] - rings["bulk"]
    lz = positions[:, 0] * velocities[:, 1] - positions[:, 1] * velocities[:, 0]
    return Frame(float(rings["time"][0]), lz, np.hypot(positions[:, 0], positions[:, 1]), np.abs(positions[:, 2]))


def load_run(data: Path, times: tuple[float, float], disk_rows: int) -> Run:
    """Load the first frame of a run and the change of L_z to the second."""
    first = load_frame(data, snapshot_near(data, times[0]), disk_rows)
    second = load_frame(data, snapshot_near(data, times[1]), disk_rows)
    return Run(first, np.asarray(second.lz - first.lz))


def binned_variance(key: F64, values: F64, edges: F64) -> tuple[F64, F64]:
    """Return the mean of the key and the variance of the values in the bins of the key."""
    index = np.clip(np.searchsorted(edges, key, side="right") - 1, 0, len(edges) - 2)
    count = np.maximum(np.bincount(index, minlength=len(edges) - 1), 1).astype(np.float64)
    mean_key = np.bincount(index, weights=key, minlength=len(edges) - 1) / count
    mean = np.bincount(index, weights=values, minlength=len(edges) - 1) / count
    second = np.bincount(index, weights=values**2, minlength=len(edges) - 1) / count
    return mean_key, second - mean**2


def exponent(key: F64, variance: F64) -> float:
    """Return the slope of log variance against log key by least squares."""
    good = (variance > 0.0) & (key > 0.0)
    return float(np.polyfit(np.log(key[good]), np.log(variance[good]), 1)[0])


def ring_row(control: Run, run: Run, bounds: tuple[float, float], z_bins: int) -> Row:
    """Return one row: the two variances, their ratio and the two exponents against |z|."""
    radius = run.first.radius
    inside = (radius >= bounds[0]) & (radius < bounds[1]) & np.isfinite(control.delta) & np.isfinite(run.delta)
    z_edges = np.quantile(run.first.abs_z[inside], np.linspace(0.0, 1.0, z_bins + 1))
    slopes = []
    totals = []
    for member in (control, run):
        mean_z, variance = binned_variance(member.first.abs_z[inside], member.delta[inside], z_edges)
        slopes.append(exponent(mean_z, variance))
        totals.append(float(np.var(member.delta[inside])))
    return {
        "ring": f"{bounds[0]:g} to {bounds[1]:g}",
        "n": int(inside.sum()),
        "var_control": totals[0],
        "var_run": totals[1],
        "ratio": totals[0] / totals[1],
        "exponent_z_control": slopes[0],
        "exponent_z_run": slopes[1],
    }


def parse_rings(spec: str) -> list[tuple[float, float]]:
    """Expand ``inner:outer:width`` into ring bounds."""
    inner, outer, width = (float(x) for x in spec.split(":"))
    edges = np.arange(inner, outer + 0.5 * width, width)
    return [(float(a), float(b)) for a, b in zip(edges[:-1], edges[1:])]
