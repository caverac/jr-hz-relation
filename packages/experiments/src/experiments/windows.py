r"""Summarize the orbits of the tracked particles over one time window of an extraction.

For every tracked particle the window gives the time averages of the angular momentum
$L_z = x v_y - y v_x$, the cylindrical radius, $v_R^2$, $v_z^2$, $|z|$ and $z^2$, two vertical
form factors on a grid of wavenumbers $k$, and the two actions as loop integrals over whole
oscillations: $J_z = \frac{1}{2\pi}\oint v_z\,dz$ between the first and the last upward
crossing of $z = 0$, and $J_R = \frac{1}{2\pi}\oint v_R\,dR$ between the first and the last
upward crossing of $R - \langle R\rangle$ (one per radial period), each divided by the number
of oscillations in between, with the periods $T_z$ and $T_R$ from the same crossings. Along
an orbit $\oint p\,dq = \int p^2\,dt$, so the loop integrals are time integrals of $v_z^2$ and
$v_R^2$ by the trapezoidal rule, with the partial intervals at the crossings integrated on
the linear interpolant. A particle without two crossings in the window gets NaN for that
action and period.

The razor-thin form factor is $F_k = \langle e^{-k|z(t)|}\rangle$, the response of a star at
height $z$ to a perturbation confined to the plane. The layer form factor replaces
$e^{-k|z|}$ by $\phi_k(z)/\phi_k(0)$ with
$\phi_k(z) \propto \int \mathrm{sech}^2(z'/z_a)\,e^{-k|z - z'|}\,dz'$, the in-plane Fourier
component of the potential of an arm whose density follows a $\mathrm{sech}^2$ layer of
scale $z_a$; it is flat for $|z| \lesssim z_a$ and decays as $e^{-k|z|}$ outside. The default
scale, :data:`ARM_SCALE`, is the measured scale of the m = 5 to 8 arms of the LD disk
inside 9 kpc between t = 0.5 and 0.8 (0.8 of the disk's 0.313 kpc).

Positions and velocities are relative to the ``center`` and ``bulk`` stored with the ring
sums of each snapshot. The output ``npz`` holds one array per quantity in the tracked order
of ``meta/tracked_ids.npy``, the number of leading rows that are disk particles, the snapshot
times, the $k$ grid and the arm scale. Units are those of the run: kpc, km/s and kpc/(km/s)
for time.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt

F32 = npt.NDArray[np.float32]
F64 = npt.NDArray[np.float64]
I64 = npt.NDArray[np.int64]

#: Default sech^2 scale of the arms (kpc).
ARM_SCALE = 0.25
#: Default wavenumber grid of the form factors, as ``start:stop:step``.
K_GRID_SPEC = "0.5:4.01:0.25"
#: Height beyond which the layer profile is held at its last value (kpc), and the grid steps.
HEIGHT_MAX = 6.0
HEIGHT_STEP = 0.005
SOURCE_STEP = 0.002


@dataclass(frozen=True)
class Window:
    """Positions and velocities of the tracked particles at the snapshots of a window."""

    times: F64  # (snapshots,)
    positions: F32  # (snapshots, particles, 3), relative to the center
    velocities: F32  # (snapshots, particles, 3), relative to the bulk velocity


@dataclass(frozen=True)
class Crossings:
    """The first and the last upward zero crossing of a (time, particle) series."""

    count: I64  # upward crossings in the window
    first: I64  # index of the interval holding the first crossing
    last: I64  # index of the interval holding the last crossing
    first_fraction: F64  # position of the crossing inside its interval, in [0, 1)
    last_fraction: F64


@dataclass(frozen=True)
class Integrand:
    """A (time, particle) series with its cumulative trapezoidal integral."""

    values: F32
    steps: F64  # (snapshots - 1,)
    cumulative: F64  # (snapshots, particles), integral from the first time to each sample

    @classmethod
    def build(cls, times: F64, values: F32) -> Integrand:
        """Integrate the series from the first time with the trapezoidal rule."""
        steps = np.diff(times)
        cumulative = np.zeros(values.shape, dtype=np.float64)
        cumulative[1:] = np.cumsum(0.5 * (values[1:] + values[:-1]) * steps[:, None], axis=0)
        return cls(values, steps, cumulative)

    def up_to(self, interval: I64, fraction: F64) -> F64:
        """Integrate from the first time to a point inside an interval, on the linear interpolant."""
        columns = np.arange(self.values.shape[1])
        before = self.values[interval, columns].astype(np.float64)
        after = self.values[interval + 1, columns].astype(np.float64)
        partial = self.steps[interval] * (fraction * before + 0.5 * fraction**2 * (after - before))
        return np.asarray(self.cumulative[interval, columns] + partial)


@dataclass(frozen=True)
class Loop:
    """Action, period and number of crossings of one oscillation, per particle."""

    action: F64
    period: F64
    count: I64


@dataclass(frozen=True)
class Averages:
    """Per-particle time averages over the window."""

    lz: F64
    lz_std: F64
    r_mean: F64
    vr2: F64
    vz2: F64
    abs_z: F64
    z2: F64


@dataclass(frozen=True)
class Summary:
    """Per-particle window averages, actions and form factors."""

    averages: Averages
    vertical: Loop
    radial: Loop
    form: F32  # (particles, wavenumbers), razor-thin
    form_layer: F32  # (particles, wavenumbers), sech^2 layer of scale arm_scale
    arm_scale: float


def snapshot_times(data: Path) -> list[tuple[int, float]]:
    """List the (number, time) of every snapshot with both products, in time order."""
    table = []
    for path in sorted((data / "rings").glob("snap_*.npz")):
        number = int(path.stem.split("_")[1])
        if (data / "tracks" / f"snap_{number:04d}.npy").exists():
            table.append((number, float(np.load(path)["time"][0])))
    return sorted(table, key=lambda item: item[1])


def load_window(data: Path, start: float, length: float) -> Window:
    """Load the tracks of the snapshots with ``start <= t < start + length`` in the disk frame."""
    chosen = [(n, t) for n, t in snapshot_times(data) if start <= t < start + length]
    if len(chosen) < 3:
        raise ValueError(f"only {len(chosen)} snapshots in [{start}, {start + length})")
    positions = []
    velocities = []
    for number, _ in chosen:
        tracks = np.load(data / "tracks" / f"snap_{number:04d}.npy")
        frame = np.load(data / "rings" / f"snap_{number:04d}.npz")
        positions.append(tracks[:, :3] - frame["center"].astype(np.float32))
        velocities.append(tracks[:, 3:] - frame["bulk"].astype(np.float32))
    return Window(np.array([t for _, t in chosen]), np.stack(positions), np.stack(velocities))


def crossing_fraction(series: F32, interval: I64) -> F64:
    """Return the fraction of the interval before the series crosses zero, by linear interpolation."""
    columns = np.arange(series.shape[1])
    before = series[interval, columns].astype(np.float64)
    after = series[interval + 1, columns].astype(np.float64)
    return np.asarray(-before / np.where(after > before, after - before, 1.0))


def upward_crossings(series: F32) -> Crossings:
    """Locate the first and the last upward zero crossing of each particle's series."""
    upward = (series[:-1] < 0.0) & (series[1:] >= 0.0)
    count = upward.sum(axis=0).astype(np.int64)
    first = np.argmax(upward, axis=0).astype(np.int64)
    last = (len(series) - 2 - np.argmax(upward[::-1], axis=0)).astype(np.int64)
    return Crossings(count, first, last, crossing_fraction(series, first), crossing_fraction(series, last))


def loop_action(times: F64, squared: F32, crossings: Crossings) -> Loop:
    """Return the action (loop integral over 2 pi, per oscillation) and the period, NaN below two crossings."""
    integrand = Integrand.build(times, squared)
    total = integrand.up_to(crossings.last, crossings.last_fraction)
    total -= integrand.up_to(crossings.first, crossings.first_fraction)
    elapsed = times[crossings.last] + crossings.last_fraction * integrand.steps[crossings.last]
    elapsed -= times[crossings.first] + crossings.first_fraction * integrand.steps[crossings.first]
    valid = crossings.count >= 2
    loops = np.where(valid, crossings.count - 1, 1).astype(np.float64)
    action = np.where(valid, total / (2.0 * np.pi * loops), np.nan)
    period = np.where(valid, elapsed / loops, np.nan)
    return Loop(np.asarray(action), np.asarray(period), crossings.count)


def layer_profile(k: float, arm_scale: float) -> tuple[F64, F64]:
    r"""Return a $|z|$ grid and $\phi_k(z)/\phi_k(0)$ for a $\mathrm{sech}^2$ layer of scale ``arm_scale``.

    $\phi_k(z) \propto \int \mathrm{sech}^2(z'/z_a)\,e^{-k|z - z'|}\,dz'$ is evaluated by direct
    summation over the sources on a grid of step :data:`SOURCE_STEP`.
    """
    heights = np.arange(0.0, HEIGHT_MAX + HEIGHT_STEP, HEIGHT_STEP)
    sources = np.arange(-HEIGHT_MAX, HEIGHT_MAX + SOURCE_STEP, SOURCE_STEP)
    weights = 1.0 / np.cosh(sources / arm_scale) ** 2
    profile = np.exp(-k * np.abs(heights[:, None] - sources[None, :])) @ weights
    return heights, np.asarray(profile / profile[0], dtype=np.float64)


def form_factors(abs_z: F32, k_grid: F64, arm_scale: float) -> tuple[F32, F32]:
    """Average exp(-k|z|) and the layer profile at |z| over time, for every particle and wavenumber."""
    thin = np.empty((abs_z.shape[1], len(k_grid)), dtype=np.float32)
    layer = np.empty((abs_z.shape[1], len(k_grid)), dtype=np.float32)
    for index, k in enumerate(k_grid):
        thin[:, index] = np.mean(np.exp(-np.float32(k) * abs_z), axis=0)
        heights, profile = layer_profile(float(k), arm_scale)
        total = np.zeros(abs_z.shape[1], dtype=np.float64)
        for sample in abs_z:
            total += np.interp(sample, heights, profile)
        layer[:, index] = total / len(abs_z)
    return thin, layer


def parse_grid(spec: str) -> F64:
    """Expand ``start:stop:step`` into a float grid."""
    start, stop, step = (float(x) for x in spec.split(":"))
    return np.arange(start, stop, step)


def in_plane(window: Window) -> tuple[F32, F32, F32]:
    """Return the cylindrical radius, the radial velocity and the angular momentum at every snapshot."""
    x, y = window.positions[:, :, 0], window.positions[:, :, 1]
    v_x, v_y = window.velocities[:, :, 0], window.velocities[:, :, 1]
    radius = np.asarray(np.hypot(x, y), dtype=np.float32)
    v_r = np.asarray((x * v_x + y * v_y) / np.maximum(radius, np.float32(1e-12)), dtype=np.float32)
    return radius, v_r, np.asarray(x * v_y - y * v_x, dtype=np.float32)


def summarize(window: Window, k_grid: F64, arm_scale: float) -> Summary:
    """Compute the per-particle window summaries."""
    radius, v_r, lz = in_plane(window)
    z, v_z = window.positions[:, :, 2], window.velocities[:, :, 2]
    abs_z = np.asarray(np.abs(z), dtype=np.float32)
    averages = Averages(
        lz=lz.mean(axis=0, dtype=np.float64),
        lz_std=lz.std(axis=0, dtype=np.float64),
        r_mean=radius.mean(axis=0, dtype=np.float64),
        vr2=(v_r * v_r).mean(axis=0, dtype=np.float64),
        vz2=(v_z * v_z).mean(axis=0, dtype=np.float64),
        abs_z=abs_z.mean(axis=0, dtype=np.float64),
        z2=(z * z).mean(axis=0, dtype=np.float64),
    )
    vertical = loop_action(window.times, v_z * v_z, upward_crossings(z))
    radial = loop_action(window.times, v_r * v_r, upward_crossings(radius - radius.mean(axis=0)))
    thin, layer = form_factors(abs_z, k_grid, arm_scale)
    return Summary(averages, vertical, radial, thin, layer, arm_scale)


def save_summary(path: Path, window: Window, summary: Summary, k_grid: F64, disk_rows: int) -> None:
    """Write the summary arrays with the window metadata."""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        times=window.times,
        disk_rows=np.array(disk_rows),
        k_grid=k_grid,
        lz=summary.averages.lz,
        lz_std=summary.averages.lz_std,
        r_mean=summary.averages.r_mean,
        vr2=summary.averages.vr2,
        vz2=summary.averages.vz2,
        abs_z=summary.averages.abs_z,
        z2=summary.averages.z2,
        j_z=summary.vertical.action,
        t_z=summary.vertical.period,
        n_z=summary.vertical.count,
        j_r=summary.radial.action,
        t_r=summary.radial.period,
        n_r=summary.radial.count,
        form=summary.form,
        form_layer=summary.form_layer,
        arm_scale=np.array(summary.arm_scale),
    )


def report(window: Window, summary: Summary, disk_rows: int) -> list[str]:
    """Describe the window coverage and the medians of the disk summaries."""
    disk = slice(0, disk_rows)
    with_jz = int(np.isfinite(summary.vertical.action[disk]).sum())
    with_jr = int(np.isfinite(summary.radial.action[disk]).sum())
    lines = [f"{len(window.times)} snapshots, t = {window.times[0]:.4f} to {window.times[-1]:.4f}"]
    lines.append(f"disk rows {disk_rows}, with J_z: {with_jz}, with J_R: {with_jr}")
    for name in ("lz", "r_mean", "vz2", "abs_z"):
        lines.append(f"median {name}: {np.median(getattr(summary.averages, name)[disk]):.4f}")
    for name, loop in (("z", summary.vertical), ("R", summary.radial)):
        action, period = np.nanmedian(loop.action[disk]), np.nanmedian(loop.period[disk])
        lines.append(f"median J_{name}: {action:.4f}, median T_{name}: {period:.4f}")
    return lines
