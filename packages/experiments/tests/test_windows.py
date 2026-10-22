"""Tests for the orbit window summaries."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from experiments.windows import (
    Crossings,
    layer_profile,
    load_window,
    loop_action,
    parse_grid,
    upward_crossings,
)


def test_parse_grid() -> None:
    """A ``start:stop:step`` spec expands to a float grid."""
    assert np.allclose(parse_grid("0.5:1.51:0.5"), [0.5, 1.0, 1.5])


def test_layer_profile_is_flat_then_exponential() -> None:
    """The layer profile is one at the plane, flat below the arm scale and exponential far above it."""
    heights, profile = layer_profile(2.0, 0.25)
    assert profile[0] == 1.0
    assert profile[np.searchsorted(heights, 0.1)] > 0.9
    far = heights > 2.0
    slope = np.polyfit(heights[far], np.log(profile[far]), 1)[0]
    assert slope == pytest.approx(-2.0, abs=0.01)


def test_loop_action_of_a_harmonic_oscillator() -> None:
    """The loop integral recovers J = E / nu for a sampled harmonic oscillation."""
    nu, amplitude = 2.0 * np.pi / 0.05, 0.3
    times = np.arange(0.0, 0.2, 0.001)
    z = (amplitude * np.cos(nu * times))[:, None].astype(np.float32)
    v_z = (-amplitude * nu * np.sin(nu * times))[:, None].astype(np.float32)
    loop = loop_action(times, v_z * v_z, upward_crossings(z))
    assert loop.action[0] == pytest.approx(0.5 * amplitude**2 * nu, rel=1e-3)
    assert loop.period[0] == pytest.approx(0.05, rel=1e-3)
    assert loop.count[0] == 4


def test_loop_action_needs_two_crossings() -> None:
    """A particle with fewer than two crossings gets NaN."""
    times = np.array([0.0, 1.0, 2.0])
    crossings = Crossings(np.array([1]), np.array([0]), np.array([0]), np.array([0.5]), np.array([0.5]))
    loop = loop_action(times, np.ones((3, 1), dtype=np.float32), crossings)
    assert np.isnan(loop.action[0]) and np.isnan(loop.period[0])


def test_load_window_needs_three_snapshots(extracted: Path) -> None:
    """A window with fewer than three snapshots is rejected."""
    with pytest.raises(ValueError, match="only 2 snapshots"):
        load_window(extracted, 0.0, 0.015)


def test_summary_contents(window_files: tuple[Path, Path]) -> None:
    """The window summary holds finite averages and actions for most particles."""
    data = np.load(window_files[0])
    rows = int(data["disk_rows"])
    assert rows == 4000
    assert len(data["times"]) == 12
    assert np.isfinite(data["lz"][:rows]).all()
    assert np.isfinite(data["j_z"][:rows]).mean() > 0.9
    assert np.isfinite(data["j_r"][:rows]).mean() > 0.3
    assert np.all(data["form_layer"][:rows] >= data["form"][:rows] - 1e-6)
    assert float(data["arm_scale"]) == 0.25
