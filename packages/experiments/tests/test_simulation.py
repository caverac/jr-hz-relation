"""Tests for the test-particle simulation and its JSON store."""

import math
from pathlib import Path

from experiments.simulation import (
    SeriesPoint,
    SimConfig,
    _mean_se,
    load_store,
    merge_point,
    save_store,
    scale_height,
    simulate_series_a,
    simulate_series_b,
)

_TINY = SimConfig(n_part=12, n_seed=2, t_end=20.0, n_step=30)


def test_scale_height_positive() -> None:
    """The alpha<->height scale is a positive number."""
    assert scale_height() > 0.0


def test_simulate_series_a_returns_finite_point() -> None:
    """Series A produces a finite seed-averaged bias at the requested alpha."""
    point = simulate_series_a(0.5, _TINY)
    assert point.x == 0.5
    assert point.n_seed == 2
    assert math.isfinite(point.bias_mean)
    assert math.isfinite(point.bias_err)


def test_simulate_series_b_single_seed_has_zero_error() -> None:
    """Series B with one seed reports zero standard error."""
    point = simulate_series_b(1, SimConfig(n_part=12, n_seed=1, t_end=20.0, n_step=30))
    assert point.x == 1.0
    assert point.bias_err == 0.0


def test_mean_se_single_value() -> None:
    """A single value has zero standard error."""
    mean, err = _mean_se([0.05])
    assert mean == 0.05
    assert err == 0.0


def test_store_roundtrip_and_merge(tmp_path: Path) -> None:
    """Saving then loading recovers the points; merge replaces by ``x``."""
    path = tmp_path / "store.json"
    points = [SeriesPoint(0.4, 0.05, 0.01, 12, 2)]
    points = merge_point(points, SeriesPoint(0.4, 0.07, 0.02, 12, 2))
    points = merge_point(points, SeriesPoint(0.8, 0.10, 0.01, 12, 2))
    save_store({"series_a": points, "series_b": []}, path)
    loaded = load_store(path)
    assert len(loaded["series_a"]) == 2
    assert loaded["series_a"][0].x == 0.4
    assert loaded["series_a"][0].bias_mean == 0.07


def test_load_store_missing_returns_empty(tmp_path: Path) -> None:
    """Loading a non-existent store returns empty series."""
    assert load_store(tmp_path / "nope.json") == {"series_a": [], "series_b": []}
