"""Test-particle validation of the provenance bias (paper figure generator).

Integrates a population of test-particle orbits in MWPotential2014 plus an imposed
transient spiral that falls off vertically (scale height ``H``), with no analytic
input, and measures the vertical velocity dispersion of the churned (migrating)
stars relative to the parent population. Two experiments:

* Series A -- a single transient spiral, sweeping the spiral thinness
  ``alpha ~ z0 / H``: the provenance bias (migrators colder) appears and strengthens
  with ``alpha`` as the analytic form factor predicts, reaching the single-resonance
  trapping value (~7 per cent) near the Milky-Way ``alpha`` ~ 1.

* Series B -- stacking ``M`` overlapping transient patterns of different pattern
  speed: the bias grows beyond the single-resonance value as the corotation
  resonances overlap.

This is an expensive, stochastic experiment (a few minutes), not part of the lean
engine or its test suite. Regenerate ``test-particle-bias.pdf`` with::

    uv run python packages/pre-print/test_particle_bias.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from galpy.orbit import Orbit
from galpy.potential import (
    GaussianAmplitudeWrapperPotential,
    MWPotential2014,
    SpiralArmsPotential,
    vcirc,
    verticalfreq,
)
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from jr_hz_relation.trapping import trapping_dispersion_ratio

SIGMA_Z0 = 0.11  # vertical dispersion in natural units (~24 km/s)
N_PART = 3000
N_SEED = 8  # realizations averaged per point to beat corotation-sample noise
T_END = 84.0  # ~3 Gyr in natural units
N_STEP = 1200


def _sample(rng: np.random.Generator) -> np.ndarray:
    """Sample near-circular orbits with guiding radii concentrated on corotation."""
    radius = rng.uniform(0.90, 1.10, N_PART)
    v_r = rng.normal(0.0, 0.05, N_PART)
    v_t = vcirc(MWPotential2014, radius) + rng.normal(0.0, 0.05, N_PART)
    v_z = rng.normal(0.0, SIGMA_Z0, N_PART)
    height = np.zeros(N_PART)
    phi = rng.uniform(0.0, 2.0 * np.pi, N_PART)
    return np.array([radius, v_r, v_t, height, v_z, phi]).T


def _mean_se(values: list[float]) -> tuple[float, float]:
    """Mean and standard error of a list of per-seed bias estimates."""
    arr = np.array(values)
    return float(arr.mean()), float(arr.std(ddof=1) / np.sqrt(len(arr)))


def _bias(potential: list, ic: np.ndarray, v_z: np.ndarray) -> float:
    """Integrate and return 1 - sigma_z(migrators)/sigma_z(all).

    The migrator population is every star weighted by its churning amount
    ``|Delta L_z|`` -- the direct analogue of the analytic migration weight ``W`` --
    which is far less noisy than a top-quantile cut.
    """
    orbit = Orbit(ic.copy())
    lz0 = np.array(orbit.Lz())
    times = np.linspace(0.0, T_END, N_STEP)
    orbit.integrate(times, potential, method="dop853_c")
    delta_lz = np.abs(np.array(orbit.Lz(times[-1])) - lz0)
    weighted = float(np.sum(delta_lz * v_z**2) / np.sum(delta_lz))
    return float(1.0 - np.sqrt(weighted / np.mean(v_z**2)))


def _single_transient(height: float) -> object:
    """One transient spiral of vertical scale height ``height`` at corotation R=1."""
    spiral = SpiralArmsPotential(amp=1.0, N=2, alpha=np.deg2rad(15.0), omega=1.0, H=height)
    return GaussianAmplitudeWrapperPotential(amp=1.0, pot=spiral, to=42.0, sigma=12.0)


def _overlapping_patterns(count: int) -> list:
    """``count`` thin transient patterns of staggered pattern speed and epoch."""
    omegas = np.linspace(0.85, 1.15, 8)
    times0 = np.linspace(20.0, 64.0, 8)
    patterns = []
    for idx in range(count):
        spiral = SpiralArmsPotential(amp=0.6, N=2, alpha=np.deg2rad(15.0), omega=float(omegas[idx]), H=0.05)
        patterns.append(GaussianAmplitudeWrapperPotential(amp=1.0, pot=spiral, to=float(times0[idx]), sigma=8.0))
    return patterns


def series_a() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Single transient spiral; bias (mean, SE over seeds) versus thinness alpha."""
    z0 = SIGMA_Z0 / float(verticalfreq(MWPotential2014, 1.0))
    heights = np.array([0.4, 0.2, 0.1, 0.06, 0.04])
    means, errors = [], []
    for height in heights:
        per_seed = []
        for seed in range(N_SEED):
            ic = _sample(np.random.default_rng(seed))
            per_seed.append(_bias([*MWPotential2014, _single_transient(float(height))], ic, ic[:, 4]))
        mean, err = _mean_se(per_seed)
        means.append(mean)
        errors.append(err)
        print(f"  A: alpha={z0/height:.2f} bias=({100*mean:.1f} +/- {100*err:.1f})%")
    return z0 / heights, np.array(means), np.array(errors)


def series_b() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Stack of M overlapping patterns; bias (mean, SE over seeds) versus M."""
    counts = np.array([1, 2, 4, 8])
    means, errors = [], []
    for count in counts:
        per_seed = []
        for seed in range(N_SEED):
            ic = _sample(np.random.default_rng(seed))
            per_seed.append(_bias([*MWPotential2014, *_overlapping_patterns(int(count))], ic, ic[:, 4]))
        mean, err = _mean_se(per_seed)
        means.append(mean)
        errors.append(err)
        print(f"  B: M={count} bias=({100*mean:.1f} +/- {100*err:.1f})%")
    return counts, np.array(means), np.array(errors)


def main() -> None:
    """Run both experiments (seed-averaged) and write the validation figure."""
    print("Series A (single transient, alpha sweep):")
    alphas, mean_a, err_a = series_a()
    print("Series B (overlapping transients):")
    counts, mean_b, err_b = series_b()

    grid = np.linspace(0.1, 1.5, 60)
    analytic = np.array([100.0 * (1.0 - trapping_dispersion_ratio(float(a), 1e-3)) for a in grid])

    fig = Figure(figsize=(9.0, 3.6))
    left = fig.add_subplot(1, 2, 1)
    left.plot(grid, analytic, "k-", label="analytic single-resonance")
    left.errorbar(
        alphas, 100.0 * mean_a, yerr=100.0 * err_a, fmt="C0o", markersize=6, capsize=3, label="test particles"
    )
    left.set_xlabel(r"spiral thinness $\alpha \sim z_0/H$")
    left.set_ylabel(r"migrator coldness $1-\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$ (\%)")
    left.set_title("single transient")
    left.legend()
    right = fig.add_subplot(1, 2, 2)
    right.errorbar(counts, 100.0 * mean_b, yerr=100.0 * err_b, fmt="C3o-", markersize=6, capsize=3)
    right.set_xlabel(r"number of overlapping patterns $M$")
    right.set_ylabel(r"migrator coldness (\%)")
    right.set_title("resonance overlap")
    out = Path(__file__).resolve().parent / "test-particle-bias.pdf"
    FigureCanvasAgg(fig)
    fig.savefig(out, format="pdf", bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
