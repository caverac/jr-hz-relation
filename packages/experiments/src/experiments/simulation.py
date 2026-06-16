"""Test-particle simulation of the provenance bias (Series A and B).

Expensive, stochastic galpy orbit integrations that validate the analytic bias by
direct churning: a population of near-circular orbits is integrated in
``MWPotential2014`` plus imposed transient spiral(s), and the vertical dispersion of
the churned (migrating) stars is compared with the parent population. Two series:

* Series A -- a single transient spiral, swept in thinness ``alpha = z0 / H``;
* Series B -- a stack of ``count`` overlapping transient patterns.

Results accumulate in a JSON store (:func:`load_store`, :func:`save_store`,
:func:`merge_point`) so the figure can be re-plotted -- and extended with new points
-- without re-running the existing ones.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from galpy.orbit import Orbit
from galpy.potential import (
    GaussianAmplitudeWrapperPotential,
    MWPotential2014,
    SpiralArmsPotential,
    vcirc,
    verticalfreq,
)

#: Vertical velocity dispersion of the parent population (natural units, ~24 km/s).
SIGMA_Z0 = 0.11

#: Default Series-A thinness values (alpha = z0/H) for a full run.
DEFAULT_ALPHAS: tuple[float, ...] = (0.1, 0.2, 0.4, 0.7, 1.0)

#: Default Series-B overlapping-pattern counts for a full run.
DEFAULT_COUNTS: tuple[int, ...] = (1, 2, 4, 8)


@dataclass(frozen=True)
class SimConfig:
    """Resolution of one seed-averaged test-particle estimate."""

    n_part: int = 3000
    n_seed: int = 8
    t_end: float = 84.0
    n_step: int = 1200


@dataclass(frozen=True)
class SeriesPoint:
    """One stored ``(x, bias)`` estimate with the resolution that produced it.

    ``bias_mean`` is the seed-averaged log dispersion ratio
    ``ln(sigma_z,mig/sigma_z,all)`` (negative for a real bias) and ``bias_err`` its
    standard error.
    """

    x: float
    bias_mean: float
    bias_err: float
    n_part: int
    n_seed: int


def _sample(rng: np.random.Generator, n_part: int) -> npt.NDArray[np.float64]:
    """Sample near-circular orbits with guiding radii concentrated on corotation."""
    radius = rng.uniform(0.90, 1.10, n_part)
    v_r = rng.normal(0.0, 0.05, n_part)
    v_t = vcirc(MWPotential2014, radius) + rng.normal(0.0, 0.05, n_part)
    v_z = rng.normal(0.0, SIGMA_Z0, n_part)
    height = np.zeros(n_part)
    phi = rng.uniform(0.0, 2.0 * np.pi, n_part)
    return np.array([radius, v_r, v_t, height, v_z, phi]).T


def _churning_bias(
    potential: list[Any], ics: npt.NDArray[np.float64], v_z: npt.NDArray[np.float64], config: SimConfig
) -> float:
    """Integrate the population and return ``ln(sigma_z(migrators)/sigma_z(all))``.

    This is the **log dispersion ratio** -- the same quantity plotted by every other
    figure (negative for a real bias) -- computed directly here rather than as a
    fractional coldness. Each star is weighted by its churning amount ``|Delta L_z|``
    -- the direct analogue of the analytic migration weight ``W`` -- which is far less
    noisy than a top-quantile cut.
    """
    orbit = Orbit(ics.copy())
    lz0 = np.array(orbit.Lz())
    times = np.linspace(0.0, config.t_end, config.n_step)
    orbit.integrate(times, potential, method="dop853_c")
    delta_lz = np.abs(np.array(orbit.Lz(times[-1])) - lz0)
    weighted = float(np.sum(delta_lz * v_z**2) / np.sum(delta_lz))
    return float(np.log(np.sqrt(weighted / np.mean(v_z**2))))


def _mean_se(values: list[float]) -> tuple[float, float]:
    """Mean and standard error of the per-seed bias estimates (zero error for one seed)."""
    arr = np.array(values)
    if arr.size < 2:
        return float(arr.mean()), 0.0
    return float(arr.mean()), float(arr.std(ddof=1) / np.sqrt(arr.size))


def _single_transient(height: float) -> Any:
    """One transient spiral of vertical scale height ``height`` at corotation R=1."""
    spiral = SpiralArmsPotential(amp=1.0, N=2, alpha=np.deg2rad(15.0), omega=1.0, H=height)
    return GaussianAmplitudeWrapperPotential(amp=1.0, pot=spiral, to=42.0, sigma=12.0)


def _overlapping_patterns(count: int) -> list[Any]:
    """``count`` thin transient patterns of staggered pattern speed and epoch."""
    omegas = np.linspace(0.85, 1.15, 8)
    times0 = np.linspace(20.0, 64.0, 8)
    patterns = []
    for idx in range(count):
        spiral = SpiralArmsPotential(amp=0.6, N=2, alpha=np.deg2rad(15.0), omega=float(omegas[idx]), H=0.05)
        patterns.append(GaussianAmplitudeWrapperPotential(amp=1.0, pot=spiral, to=float(times0[idx]), sigma=8.0))
    return patterns


def scale_height() -> float:
    """Vertical scale ``z0 = sigma_z0 / nu_z(R=1)`` -- the ``alpha <-> H`` conversion."""
    return SIGMA_Z0 / float(verticalfreq(MWPotential2014, 1.0))


def simulate_series_a(alpha: float, config: SimConfig) -> SeriesPoint:
    """Single transient spiral at thinness ``alpha``; seed-averaged migrator coldness."""
    potential = [*MWPotential2014, _single_transient(scale_height() / alpha)]
    per_seed = []
    for seed in range(config.n_seed):
        ics = _sample(np.random.default_rng(seed), config.n_part)
        per_seed.append(_churning_bias(potential, ics, ics[:, 4], config))
    mean, err = _mean_se(per_seed)
    return SeriesPoint(alpha, mean, err, config.n_part, config.n_seed)


def simulate_series_b(count: int, config: SimConfig) -> SeriesPoint:
    """Stack of ``count`` overlapping patterns; seed-averaged migrator coldness."""
    potential = [*MWPotential2014, *_overlapping_patterns(count)]
    per_seed = []
    for seed in range(config.n_seed):
        ics = _sample(np.random.default_rng(seed), config.n_part)
        per_seed.append(_churning_bias(potential, ics, ics[:, 4], config))
    mean, err = _mean_se(per_seed)
    return SeriesPoint(float(count), mean, err, config.n_part, config.n_seed)


def _point_from_dict(raw: dict[str, Any]) -> SeriesPoint:
    """Reconstruct a :class:`SeriesPoint` from its JSON mapping."""
    return SeriesPoint(
        x=float(raw["x"]),
        bias_mean=float(raw["bias_mean"]),
        bias_err=float(raw["bias_err"]),
        n_part=int(raw["n_part"]),
        n_seed=int(raw["n_seed"]),
    )


def load_store(path: Path) -> dict[str, list[SeriesPoint]]:
    """Load the JSON store, returning empty series when ``path`` does not exist."""
    if not path.exists():
        return {"series_a": [], "series_b": []}
    raw: dict[str, Any] = json.loads(path.read_text())
    return {
        "series_a": [_point_from_dict(point) for point in raw.get("series_a", [])],
        "series_b": [_point_from_dict(point) for point in raw.get("series_b", [])],
    }


def save_store(store: dict[str, list[SeriesPoint]], path: Path) -> None:
    """Write the store to JSON, each series sorted by ``x``."""
    payload = {
        series: [asdict(point) for point in sorted(points, key=lambda q: q.x)] for series, points in store.items()
    }
    path.write_text(json.dumps(payload, indent=2))


def merge_point(points: list[SeriesPoint], new: SeriesPoint) -> list[SeriesPoint]:
    """Return ``points`` with ``new`` added, replacing any existing point at the same ``x``."""
    kept = [point for point in points if abs(point.x - new.x) > 1e-9]
    kept.append(new)
    return kept
