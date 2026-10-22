"""Tests for the vertical profile of the arms."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from conftest import SPIRAL_M

from experiments.arms import ArmSetup, accumulate, layer_scale, profile_rows, profile_table, window_numbers


def test_layer_scale_of_a_sech2_layer() -> None:
    """The scale of a sech^2 layer is recovered from its second moment."""
    z_a = 0.3
    z2 = np.array([(np.pi**2 / 12.0) * z_a**2])
    assert layer_scale(z2, np.array([1.0]), np.array([1.0])) == pytest.approx(z_a)


def test_window_numbers(extracted: Path) -> None:
    """Snapshots with start < t <= start + length enter, thinned by ``every``."""
    numbers = window_numbers(extracted, ArmSetup(0.0, 0.12, every=2, disk_rows=4000))
    assert numbers == [1, 3, 5, 7, 9, 11]


def test_imprinted_arm_has_the_disk_thickness(extracted: Path) -> None:
    """The imprinted pattern is seen in the strongest harmonic with a scale near the disk's."""
    sums, numbers = accumulate(extracted, ArmSetup(0.0, 0.12, every=3, disk_rows=4000), (3, SPIRAL_M))
    assert len(numbers) == 4
    rows = profile_rows(sums)
    strongest = max((row for row in rows if row["ring"] == "4 to 5"), key=lambda row: float(row["a_all"]))
    assert strongest["m"] == SPIRAL_M
    assert 0.5 < float(strongest["ratio"]) < 1.5
    lines = profile_table(rows, numbers)
    assert lines[0] == "4 snapshots: 1 to 10"
    assert any(line.startswith("| 4 to 5 | 5 |") for line in lines)
