r"""Measure the vertical profile of the spiral arms from the tracked disk particles.

In rings of the instantaneous radius, for each of the harmonics, the Fourier amplitude of the
particles in fixed bins of $|z|$ is projected on the phase of the whole ring and accumulated
over the snapshots of a window. The relative amplitude of the arm at height,
$a_m(|z|) = 2\,\mathrm{Re}\,C/N$ with $C$ the projected sum and $N$ the particles in the bin,
falls from its midplane value to zero where the arm ends, and the phase of $C$ is the lag
of the arm at height behind the midplane arm. The implied scale of a $\mathrm{sech}^2$ layer
with the arm's second moment is $z_a = \sqrt{12\langle z^2\rangle_{\rm arm}}/\pi$, where the
average weights each bin by its excess particles $\max(a_m, 0)\,N$; the same expression on
all particles gives the disk's scale for comparison. Units are those of the run.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt

F64 = npt.NDArray[np.float64]
C128 = npt.NDArray[np.complex128]
Row = dict[str, float | int | str]

#: Edges of the |z| bins (kpc) and their number.
Z_EDGES: F64 = np.array([0.0, 0.1, 0.2, 0.3, 0.45, 0.65, 1.0, 2.0])
N_BINS = len(Z_EDGES) - 1
#: Rings of the instantaneous radius (kpc).
RINGS: tuple[tuple[float, float], ...] = tuple((float(a), float(a) + 1.0) for a in range(3, 12))


@dataclass(frozen=True)
class ArmSetup:
    """Which snapshots of an extraction enter the measurement and which rows are disk particles."""

    start: float
    length: float
    every: int = 5
    disk_rows: int = 1_000_000


@dataclass
class ArmSums:
    """Accumulated projected amplitudes, counts and second moments per ring, harmonic and |z| bin."""

    harmonics: tuple[int, ...]
    coef: dict[tuple[int, int], C128]
    count: dict[int, F64]
    z2sum: dict[int, F64]

    @classmethod
    def empty(cls, harmonics: tuple[int, ...]) -> ArmSums:
        """Create zero sums for every ring and harmonic."""
        coef = {(r, m): np.zeros(N_BINS, dtype=np.complex128) for r in range(len(RINGS)) for m in harmonics}
        return cls(
            harmonics,
            coef,
            {r: np.zeros(N_BINS) for r in range(len(RINGS))},
            {r: np.zeros(N_BINS) for r in range(len(RINGS))},
        )

    def add(self, positions: F64) -> None:
        """Accumulate one snapshot's disk particles, given relative to the disk center."""
        radius = np.hypot(positions[:, 0], positions[:, 1])
        phi = np.arctan2(positions[:, 1], positions[:, 0])
        abs_z = np.abs(positions[:, 2])
        z_bin = np.clip(np.searchsorted(Z_EDGES, abs_z, side="right") - 1, 0, N_BINS - 1)
        for r, (low, high) in enumerate(RINGS):
            inside = (radius >= low) & (radius < high) & (abs_z < Z_EDGES[-1])
            bins = z_bin[inside]
            self.count[r] += np.bincount(bins, minlength=N_BINS)
            self.z2sum[r] += np.bincount(bins, weights=abs_z[inside] ** 2, minlength=N_BINS)
            for m in self.harmonics:
                phase = np.exp(1j * m * phi[inside])
                self.coef[(r, m)] += projected_sums(bins, phase * np.exp(-1j * np.angle(phase.sum())))


def projected_sums(bins: npt.NDArray[np.int64], aligned: C128) -> C128:
    """Sum the aligned phases per |z| bin."""
    real = np.bincount(bins, weights=aligned.real, minlength=N_BINS)
    imag = np.bincount(bins, weights=aligned.imag, minlength=N_BINS)
    return np.asarray(real + 1j * imag, dtype=np.complex128)


def window_numbers(data: Path, setup: ArmSetup) -> list[int]:
    """List every ``every``-th snapshot with ``start < t <= start + length``, in time order."""
    numbers = []
    for path in sorted((data / "rings").glob("snap_*.npz")):
        t = float(np.load(path)["time"][0])
        if setup.start < t <= setup.start + setup.length + 1e-9:
            numbers.append(int(path.stem.split("_")[1]))
    return numbers[:: setup.every]


def accumulate(data: Path, setup: ArmSetup, harmonics: tuple[int, ...]) -> tuple[ArmSums, list[int]]:
    """Accumulate the projected amplitudes over the chosen snapshots of an extraction."""
    numbers = window_numbers(data, setup)
    sums = ArmSums.empty(harmonics)
    for number in numbers:
        rings = np.load(data / "rings" / f"snap_{number:04d}.npz")
        tracks = np.load(data / "tracks" / f"snap_{number:04d}.npy")[: setup.disk_rows].astype(np.float64)
        positions = tracks[:, :3] - rings["center"]
        sums.add(positions[np.isfinite(positions[:, 0])])
    return sums, numbers


def layer_scale(z2sum: F64, count: F64, weights: F64) -> float:
    """Return the sech^2 scale whose second moment matches the weighted mean of ``z2sum / count``."""
    z2 = float(np.sum(weights * z2sum / np.maximum(count, 1.0)) / np.sum(weights))
    return float(np.sqrt(12.0 * z2) / np.pi)


def profile_rows(sums: ArmSums) -> list[Row]:
    """Return one row per ring and harmonic: amplitude and lag per |z| bin, total, arm and disk scales."""
    rows: list[Row] = []
    for r, (low, high) in enumerate(RINGS):
        count = sums.count[r]
        z_disk = layer_scale(sums.z2sum[r], count, count)
        for m in sums.harmonics:
            coef = sums.coef[(r, m)]
            projected = 2.0 * coef.real / np.maximum(count, 1.0)
            z_arm = layer_scale(sums.z2sum[r], count, np.maximum(projected, 0.0) * count)
            row: Row = {"ring": f"{low:g} to {high:g}", "m": m}
            for index, (amplitude, lag) in enumerate(zip(projected, np.degrees(np.angle(coef)))):
                row[f"a_{index}"] = 100.0 * float(amplitude)
                row[f"lag_{index}"] = float(lag)
            row["a_all"] = 100.0 * float(2.0 * coef.real.sum() / max(count.sum(), 1.0))
            row["z_arm"] = z_arm
            row["z_disk"] = z_disk
            row["ratio"] = z_arm / z_disk
            rows.append(row)
    return rows


def profile_table(rows: list[Row], numbers: list[int]) -> list[str]:
    """Format the profile rows as a markdown table with the |z| bins in the header."""
    bins = ", ".join(f"{a:g} to {b:g}" for a, b in zip(Z_EDGES[:-1], Z_EDGES[1:]))
    lines = [f"{len(numbers)} snapshots: {numbers[0]} to {numbers[-1]}", f"|z| bins (kpc): {bins}"]
    lines.append("\n### Projected arm amplitude (percent) per |z| bin, phase lag (deg) in brackets\n")
    header = " | ".join(f"bin {i}" for i in range(N_BINS))
    lines.append(f"| ring | m | {header} | all | z_arm (kpc) | z_disk (kpc) | z_arm/z_disk |")
    lines.append("|" + "---|" * (N_BINS + 6))
    for row in rows:
        cells = " | ".join(f"{row[f'a_{i}']:.1f} [{row[f'lag_{i}']:+.0f}]" for i in range(N_BINS))
        lines.append(
            f"| {row['ring']} | {row['m']} | {cells} | {row['a_all']:.1f} | {row['z_arm']:.3f} | "
            f"{row['z_disk']:.3f} | {row['ratio']:.2f} |"
        )
    return lines
