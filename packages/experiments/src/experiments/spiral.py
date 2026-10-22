r"""Measure the spiral patterns of a run from the ring sums written by :mod:`experiments.tracks`.

For each harmonic $m$ the ring sums give $A_m(R, t) = N^{-1}\sum_j e^{i m \phi_j}$ over the
disk particles of a ring. Its modulus is half the relative density amplitude
$a_m = \delta\Sigma_m/\Sigma$, and its phase winds with radius at the rate
$k = |\partial \arg A_m/\partial R|$, the radial wavenumber, so that the pitch angle is
$\tan i = m/(kR)$. The potential of a perturbation with the $\mathrm{sech}^2$ profile of the
disk has the midplane amplitude $|\Phi_m| = 2\pi G\Sigma a_m T(k)/k$ with
$T(k) = \langle e^{-k|z|}\rangle = 1 - (kz_0/2)[\psi(1 + kz_0/4) - \psi(1/2 + kz_0/4)]$, and
the strength is $\epsilon = |\Phi_m|/V_c^2$. Pattern speeds come from the spectrogram
$P_m(R, \Omega_p) = |\sum_t w(t) A_m(R, t) e^{-i m \Omega_p t}|^2 / (\sum_t w)^2$ with a Hann
window $w$, so that a steady pattern of amplitude $|A_m|$ gives a peak of height $|A_m|^2$.

The circular speed is that of the model: the exponential disk of the initial conditions
(:data:`M_DISK`, :data:`R_DISK`, :data:`Z_DISK`) and the rigid Hernquist halo, with the disk
term from the Bessel integral of a razor-thin exponential disk averaged over the layer. It
is checked against the mean azimuthal speed of the ring sums corrected for the asymmetric
drift. Units are those of the run: kpc, km/s, $10^{10}$ M$_\odot$ and kpc/(km/s) for time,
so that frequencies are in km/s/kpc.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path

import numpy as np
import numpy.typing as npt
from scipy import special

#: Gravitational constant in kpc (km/s)^2 per 10^10 Msun.
G = 43007.1
#: Disk mass (10^10 Msun), scale length and sech^2 scale (kpc) of the initial conditions.
M_DISK, R_DISK, Z_DISK = 1.81, 3.13, 0.313
#: Hernquist halo mass (10^10 Msun) and scale radius (kpc).
M_HALO, A_HALO = 95.0, 29.8
#: Mass of one disk particle in a run of 10^8 of them.
PARTICLE_MASS = M_DISK / 1.0e8
#: Harmonics stored in the ring sums.
HARMONICS = 8
#: Harmonics combined into the test's wavenumber (the arms of the LD disk are m = 5 to 8).
ARM_HARMONICS: tuple[int, ...] = (5, 6, 7, 8)
CURVE_RADII: npt.NDArray[np.float64] = np.arange(0.05, 30.0001, 0.05)
BESSEL_K: npt.NDArray[np.float64] = np.arange(0.0, 100.0, 0.0025)
OMEGA_GRID: npt.NDArray[np.float64] = np.arange(0.0, 100.001, 0.5)
REPORT_RADII: tuple[float, ...] = (3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0)
PEAK_FRACTION = 0.1
MAX_PEAKS = 8

F64 = npt.NDArray[np.float64]
C128 = npt.NDArray[np.complex128]
Mask = npt.NDArray[np.bool_]


@dataclass(frozen=True)
class Rings:
    """The ring sums of every snapshot, stacked in time."""

    times: F64  # (snapshots,)
    edges: F64  # (rings + 1,)
    names: list[str]
    values: F64  # (snapshots, names, rings)
    coef: C128  # (harmonics, snapshots, rings), A_m = (sum cos + i sum sin) / count

    @property
    def centers(self) -> F64:
        """Ring centers."""
        return 0.5 * (self.edges[:-1] + self.edges[1:])

    @property
    def areas(self) -> F64:
        """Ring areas."""
        return np.pi * (self.edges[1:] ** 2 - self.edges[:-1] ** 2)

    def mean(self, name: str, mask: Mask) -> F64:
        """Average over the selected snapshots a ring sum divided by the count; NaN for empty rings."""
        count = self.values[mask, self.names.index("count"), :]
        return np.asarray(np.mean(per_particle(self.values[mask, self.names.index(name), :], count), axis=0))

    def surface_density(self, mask: Mask) -> F64:
        """Average over the selected snapshots the surface density of each ring."""
        count = np.mean(self.values[mask, self.names.index("count"), :], axis=0)
        return np.asarray(PARTICLE_MASS * count / self.areas)

    def ring_index(self, radius: float) -> int:
        """Return the index of the ring whose center is nearest to the radius."""
        return int(np.argmin(np.abs(self.centers - radius)))


@dataclass(frozen=True)
class RotationCurve:
    """Circular speed and epicyclic frequencies of the model on a fine radial grid."""

    radius: F64
    v_circ: F64
    omega: F64
    kappa: F64

    def at(self, name: str, radius: F64) -> F64:
        """Interpolate one of the curves at the given radii."""
        return np.asarray(np.interp(radius, self.radius, getattr(self, name)))


@dataclass(frozen=True)
class WindowModes:
    """Spiral measurements in one time window."""

    bounds: tuple[float, float]
    amplitude: F64  # (harmonics, rings), time-mean a_m
    wavenumber: F64  # (harmonics, rings - 1), signed d(arg A_m)/dR at the inner ring edges
    coherence: F64  # (harmonics, rings - 1)
    epsilon: F64  # (harmonics, rings)
    spectrogram: F64  # (harmonics, rings, omegas)


def per_particle(total: F64, count: F64, empty: float = np.nan) -> F64:
    """Divide ring sums by ring counts, giving ``empty`` where a ring holds no particle."""
    return np.asarray(np.divide(total, count, out=np.full(total.shape, empty), where=count > 0))


def layer_factor(k: F64) -> F64:
    r"""Return $\langle e^{-k|z|}\rangle$ over a $\mathrm{sech}^2(z/z_0)$ layer."""
    a = k * Z_DISK
    return np.asarray(1.0 - 0.5 * a * (special.digamma(1.0 + 0.25 * a) - special.digamma(0.5 + 0.25 * a)))


def rotation_curve(radii: F64) -> RotationCurve:
    """Compute the circular speed of the thick exponential disk plus the Hernquist halo."""
    sigma0 = M_DISK / (2.0 * np.pi * R_DISK**2)
    kernel = BESSEL_K * layer_factor(BESSEL_K) / (1.0 + BESSEL_K**2 * R_DISK**2) ** 1.5
    bessel = np.array([np.trapezoid(special.jv(1, r * BESSEL_K) * kernel, BESSEL_K) for r in radii])
    v2_disk = 2.0 * np.pi * G * sigma0 * R_DISK**2 * radii * bessel
    v2_halo = G * M_HALO * radii / (radii + A_HALO) ** 2
    v_circ = np.sqrt(v2_disk + v2_halo)
    omega = v_circ / radii
    kappa = np.sqrt(radii * np.gradient(omega**2, radii) + 4.0 * omega**2)
    return RotationCurve(radii, v_circ, omega, kappa)


@cache
def model_rotation_curve() -> RotationCurve:
    """Return the rotation curve of the model on :data:`CURVE_RADII`, computed once per process."""
    return rotation_curve(CURVE_RADII)


def load_rings(directory: Path) -> Rings:
    """Stack the ring sums of every snapshot in the directory, in time order."""
    files = sorted(directory.glob("snap_*.npz"))
    if not files:
        raise FileNotFoundError(f"no ring sums in {directory}")
    first = np.load(files[0])
    names = [str(name) for name in first["names"]]
    edges = np.asarray(first["edges"], dtype=np.float64)
    times = np.empty(len(files))
    values = np.empty((len(files), len(names), len(edges) - 1))
    for index, path in enumerate(files):
        data = np.load(path)
        times[index] = float(data["time"][0])
        values[index] = data["values"]
    order = np.argsort(times)
    times, values = times[order], values[order]
    count = values[:, names.index("count"), :]
    coef = np.empty((HARMONICS, len(files), len(edges) - 1), dtype=np.complex128)
    for m in range(1, HARMONICS + 1):
        real = per_particle(values[:, names.index(f"cos{m}"), :], count, 0.0)
        coef[m - 1] = real + 1j * per_particle(values[:, names.index(f"sin{m}"), :], count, 0.0)
    return Rings(times, edges, names, values, coef)


def parse_windows(spec: str, times: F64) -> list[tuple[float, float]]:
    """Expand ``start:end,start:end`` into window bounds; an empty spec is the whole run."""
    if not spec:
        return [(float(times[0]), float(times[-1]) + 1e-9)]
    bounds = []
    for part in spec.split(","):
        start, end = (float(x) for x in part.split(":"))
        bounds.append((start, end))
    return bounds


def spectrogram(rings: Rings, mask: Mask) -> F64:
    """Return the Hann-windowed power of every harmonic on the (ring, pattern speed) grid."""
    times = rings.times[mask] - rings.times[mask][0]
    window = 0.5 * (1.0 - np.cos(2.0 * np.pi * np.arange(len(times)) / max(len(times) - 1, 1)))
    power = np.empty((HARMONICS, rings.coef.shape[2], len(OMEGA_GRID)))
    for index in range(HARMONICS):
        m = index + 1
        phases = np.exp(-1j * m * np.outer(OMEGA_GRID, times))  # (omegas, snapshots)
        transform = phases @ (window[:, None] * rings.coef[index, mask, :])  # (omegas, rings)
        power[index] = (np.abs(transform.T) / window.sum()) ** 2
    return power


def wavenumbers(rings: Rings, mask: Mask) -> tuple[F64, F64]:
    """Return the signed radial wavenumber and the coherence between adjacent rings."""
    coef = rings.coef[:, mask, :]
    cross = np.sum(coef[:, :, 1:] * np.conj(coef[:, :, :-1]), axis=1)
    norm = np.sum(np.abs(coef[:, :, 1:]) * np.abs(coef[:, :, :-1]), axis=1)
    width = np.diff(rings.centers)
    return np.angle(cross) / width, np.abs(cross) / np.maximum(norm, 1e-300)


def measure_window(rings: Rings, curve: RotationCurve, bounds: tuple[float, float]) -> WindowModes:
    """Measure amplitudes, wavenumbers, strengths and the spectrogram in one window."""
    mask = (rings.times >= bounds[0]) & (rings.times < bounds[1])
    if mask.sum() < 2:
        raise ValueError(f"window {bounds} holds fewer than two snapshots")
    amplitude = 2.0 * np.mean(np.abs(rings.coef[:, mask, :]), axis=1)
    wavenumber, coherence = wavenumbers(rings, mask)
    sigma = rings.surface_density(mask)
    k_ring = np.abs(
        np.concatenate([wavenumber[:, :1], 0.5 * (wavenumber[:, 1:] + wavenumber[:, :-1]), wavenumber[:, -1:]], axis=1)
    )
    v_circ = curve.at("v_circ", rings.centers)
    epsilon = 2.0 * np.pi * G * sigma * amplitude * layer_factor(k_ring) / (np.maximum(k_ring, 1e-6) * v_circ**2)
    return WindowModes(bounds, amplitude, wavenumber, coherence, epsilon, spectrogram(rings, mask))


def combined_wavenumber(modes: WindowModes, edges: F64, harmonics: list[int], bounds: tuple[float, float]) -> float:
    """Average |k| over the harmonics in a ring, each weighted by its mean squared amplitude there.

    The |k| of one harmonic is its coherence-weighted mean over the ring edges inside the
    bounds; with one harmonic the amplitude weight drops out.
    """
    rows = [m - 1 for m in harmonics]
    at_edges = (edges[1:-1] >= bounds[0]) & (edges[1:-1] <= bounds[1])
    in_cells = (edges[:-1] >= bounds[0]) & (edges[1:] <= bounds[1])
    coherence = modes.coherence[rows][:, at_edges]
    per_harmonic = np.sum(coherence * np.abs(modes.wavenumber[rows][:, at_edges]), axis=1) / np.sum(coherence, axis=1)
    weights = np.mean(modes.amplitude[rows][:, in_cells] ** 2, axis=1)
    return float(np.sum(weights * per_harmonic) / np.sum(weights))


def local_maxima(power: F64) -> list[tuple[int, int]]:
    """Return the (ring, omega) indices of the local maxima above the peak fraction, strongest first."""
    padded = np.pad(power, 1, constant_values=-1.0)
    is_peak = np.ones_like(power, dtype=bool)
    for shift_r in (-1, 0, 1):
        for shift_o in (-1, 0, 1):
            if shift_r or shift_o:
                rows = slice(1 + shift_r, padded.shape[0] - 1 + shift_r)
                cols = slice(1 + shift_o, padded.shape[1] - 1 + shift_o)
                is_peak &= power >= padded[rows, cols]
    is_peak &= power >= PEAK_FRACTION * power.max()
    peaks = np.argwhere(is_peak)
    order = np.argsort(power[is_peak])[::-1]
    return [(int(peaks[i, 0]), int(peaks[i, 1])) for i in order[:MAX_PEAKS]]


def resonance_radius(curve: RotationCurve, frequency: F64, pattern_speed: float) -> float:
    """Return the radius where a decreasing frequency curve equals the pattern speed, or NaN."""
    if pattern_speed <= frequency[-1] or pattern_speed >= frequency[0]:
        return float("nan")
    return float(np.interp(-pattern_speed, -frequency, curve.radius))


def amplitude_table(rings: Rings, modes: WindowModes) -> list[str]:
    """Tabulate the time-mean density amplitude of every harmonic at the report radii."""
    lines = [f"\n### Window t = {modes.bounds[0]:.3f} to {modes.bounds[1]:.3f}: density amplitude a_m (percent)\n"]
    lines.append("| R (kpc) | " + " | ".join(f"m = {m}" for m in range(1, HARMONICS + 1)) + " | dominant m |")
    lines.append("|---|" + "---|" * (HARMONICS + 1))
    for radius in REPORT_RADII:
        row = modes.amplitude[:, rings.ring_index(radius)]
        cells = " | ".join(f"{100.0 * a:.1f}" for a in row)
        lines.append(f"| {radius:g} | {cells} | {int(np.argmax(row)) + 1} |")
    return lines


def wavenumber_table(rings: Rings, modes: WindowModes, harmonic: int, trailing_sign: float) -> list[str]:
    """Tabulate the wavenumber, pitch angle, coherence and strength of one harmonic."""
    index = harmonic - 1
    lines = [f"\n#### m = {harmonic}: wavenumber at the ring edges and strength\n"]
    lines.append(
        "| R (kpc) | k (1/kpc) | pitch angle (deg) | coherence | trailing | a_m (percent) | epsilon (percent) |"[:120]
    )
    lines.append("|---|---|---|---|---|---|---|")
    for radius in REPORT_RADII:
        edge = int(np.argmin(np.abs(rings.edges[1:-1] - radius)))
        k_signed = modes.wavenumber[index, edge]
        pitch = np.degrees(np.arctan2(harmonic, abs(k_signed) * rings.edges[edge + 1]))
        ring = rings.ring_index(radius)
        lines.append(
            f"| {radius:g} | {abs(k_signed):.2f} | {pitch:.1f} | {modes.coherence[index, edge]:.2f} | "
            f"{'yes' if np.sign(k_signed) == trailing_sign else 'no'} | {100.0 * modes.amplitude[index, ring]:.1f} | "
            f"{100.0 * modes.epsilon[index, ring]:.2f} |"
        )
    return lines


def _half_power_range(above: Mask, ring: int) -> tuple[int, int]:
    """Return the first and last ring of the contiguous run above half power that holds the peak."""
    inner = ring
    while inner > 0 and above[inner - 1]:
        inner -= 1
    outer = ring
    while outer < len(above) - 1 and above[outer + 1]:
        outer += 1
    return inner, outer


def peak_table(rings: Rings, modes: WindowModes, curve: RotationCurve, harmonic: int) -> list[str]:
    """Tabulate the spectrogram peaks of one harmonic with their resonance radii."""
    index = harmonic - 1
    power = modes.spectrogram[index]
    lines = [f"\n#### m = {harmonic}: spectrogram peaks (amplitude 2 sqrt(P), fraction of the strongest peak)\n"]
    lines.append(
        "| R (kpc) | Omega_p (km/s/kpc) | amplitude (percent) | fraction | R range at half power (kpc) "
        "| R_ILR | R_CR | R_OLR |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for ring, omega in local_maxima(power):
        pattern_speed = float(OMEGA_GRID[omega])
        inner, outer = _half_power_range(power[:, omega] >= 0.5 * power[ring, omega], ring)
        inner_lindblad = resonance_radius(curve, curve.omega - curve.kappa / harmonic, pattern_speed)
        corotation = resonance_radius(curve, curve.omega, pattern_speed)
        outer_lindblad = resonance_radius(curve, curve.omega + curve.kappa / harmonic, pattern_speed)
        lines.append(
            f"| {rings.centers[ring]:.2f} | {pattern_speed:.1f} | {200.0 * np.sqrt(power[ring, omega]):.1f} | "
            f"{power[ring, omega] / power.max():.2f} | {rings.edges[inner]:.2f} to {rings.edges[outer + 1]:.2f} | "
            f"{inner_lindblad:.1f} | {corotation:.1f} | {outer_lindblad:.1f} |"
        )
    return lines


def rotation_check_table(rings: Rings, curve: RotationCurve, mask: Mask) -> list[str]:
    """Tabulate the model circular speed against the Jeans estimate from the ring sums."""
    v_phi, v_r = rings.mean("v_phi", mask), rings.mean("v_r", mask)
    sigma_phi2 = rings.mean("v_phi2", mask) - v_phi**2
    sigma_r2 = rings.mean("v_r2", mask) - v_r**2
    pressure = np.log(rings.surface_density(mask) * sigma_r2)
    slope = np.gradient(pressure, np.log(rings.centers))
    v_jeans = np.sqrt(np.maximum(v_phi**2 + sigma_phi2 - sigma_r2 * (1.0 + slope), 0.0))
    lines = ["\n### Circular speed: model against the Jeans estimate (km/s)\n"]
    lines.append("| R (kpc) | V_c model | mean v_phi | V_c Jeans | sigma_R | sigma_phi |")
    lines.append("|---|---|---|---|---|---|")
    for radius in (2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0):
        ring = rings.ring_index(radius)
        model = curve.at("v_circ", np.array([radius]))[0]
        lines.append(
            f"| {radius:g} | {model:.1f} | {v_phi[ring]:.1f} | {v_jeans[ring]:.1f} | "
            f"{np.sqrt(sigma_r2[ring]):.1f} | {np.sqrt(sigma_phi2[ring]):.1f} |"
        )
    return lines


def combined_table(rings: Rings, windows: list[WindowModes], harmonics: list[int]) -> list[str]:
    """Tabulate the combined wavenumber of the chosen harmonics in rings of 1 kpc for every window."""
    bounds = [(float(r), float(r) + 1.0) for r in REPORT_RADII[:-1]]
    label = ", ".join(str(m) for m in harmonics)
    lines = [f"\n### Combined wavenumber of m = {label} (1/kpc), squared-amplitude weights, by ring and window\n"]
    lines.append("| ring (kpc) | " + " | ".join(f"t = {w.bounds[0]:.2f} to {w.bounds[1]:.2f}" for w in windows) + " |")
    lines.append("|---|" + "---|" * len(windows))
    for ring in bounds:
        values = [combined_wavenumber(modes, rings.edges, harmonics, ring) for modes in windows]
        lines.append(f"| {ring[0]:g} to {ring[1]:g} | " + " | ".join(f"{k:.2f}" for k in values) + " |")
    return lines


def report(rings: Rings, curve: RotationCurve, windows: list[WindowModes], min_amplitude: float) -> list[str]:
    """Build the full report: the rotation check, then per window the tables of every strong harmonic."""
    all_mask = np.ones(len(rings.times), dtype=bool)
    lines = [f"{len(rings.times)} snapshots from t = {rings.times[0]:.3f} to {rings.times[-1]:.3f}"]
    lines += rotation_check_table(rings, curve, all_mask)
    trailing_sign = -np.sign(rings.mean("v_phi", all_mask)[rings.ring_index(8.0)])
    inner, last = rings.ring_index(REPORT_RADII[0]), rings.ring_index(REPORT_RADII[-1]) + 1
    for modes in windows:
        lines += amplitude_table(rings, modes)
        for harmonic in range(1, HARMONICS + 1):
            if modes.amplitude[harmonic - 1, inner:last].max() >= min_amplitude:
                lines += wavenumber_table(rings, modes, harmonic, trailing_sign)
                lines += peak_table(rings, modes, curve, harmonic)
    lines += combined_table(rings, windows, list(ARM_HARMONICS))
    return lines


def save_modes(path: Path, rings: Rings, curve: RotationCurve, windows: list[WindowModes]) -> None:
    """Write the ring coefficients, the rotation curve and the window measurements."""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        times=rings.times,
        edges=rings.edges,
        coef=rings.coef.astype(np.complex64),
        rc_radius=curve.radius,
        v_circ=curve.v_circ,
        omega=curve.omega,
        kappa=curve.kappa,
        omega_grid=OMEGA_GRID,
        window_bounds=np.array([w.bounds for w in windows]),
        amplitude=np.stack([w.amplitude for w in windows]),
        wavenumber=np.stack([w.wavenumber for w in windows]),
        coherence=np.stack([w.coherence for w in windows]),
        epsilon=np.stack([w.epsilon for w in windows]),
        spectrogram=np.stack([w.spectrogram for w in windows]).astype(np.float32),
    )
