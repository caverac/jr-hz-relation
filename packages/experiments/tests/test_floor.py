"""Tests for the perturber floor."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from experiments.floor import exponent, load_run, parse_rings, ring_row, snapshot_near


def test_snapshot_near(extracted: Path, tmp_path: Path) -> None:
    """The nearest snapshot is found within the tolerance and errors are raised otherwise."""
    assert snapshot_near(extracted, 0.1) == 10
    with pytest.raises(ValueError, match="no snapshot within"):
        snapshot_near(extracted, 0.9)
    with pytest.raises(ValueError, match="no ring sums"):
        snapshot_near(tmp_path, 0.1)


def test_exponent_ignores_empty_bins() -> None:
    """Bins with zero variance do not enter the fit."""
    assert exponent(np.array([1.0, 2.0, 4.0]), np.array([1.0, 0.0, 16.0])) == pytest.approx(2.0)


def test_control_floor(extracted: Path, control_extracted: Path) -> None:
    """The control run, which holds the same orbits, has the same dLz variance as the run."""
    control = load_run(control_extracted, (0.0, 0.2), 4000)
    run = load_run(extracted, (0.0, 0.2), 4000)
    row = ring_row(control, run, (4.0, 5.0), 4)
    assert int(row["n"]) > 100
    assert row["ratio"] == pytest.approx(1.0, rel=1e-3)
    assert parse_rings("4:6:1") == [(4.0, 5.0), (5.0, 6.0)]
