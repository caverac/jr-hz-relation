"""Tests for the isothermal-sheet vertical orbit structure."""

import numpy as np
import pytest

from jr_hz_relation.sheet import (
    NU_MAX,
    RHO0,
    density,
    potential,
    turning_point,
    vertical_action,
    vertical_frequency,
)


def test_potential_and_density_at_midplane() -> None:
    """At the midplane the potential vanishes and the density is rho0."""
    assert potential(0.0) == pytest.approx(0.0)
    assert density(0.0) == pytest.approx(RHO0)


def test_density_decays_with_height() -> None:
    """The density falls as sech^2 away from the plane."""
    assert density(1.0) < density(0.5) < density(0.0)


def test_turning_point_solves_potential() -> None:
    """At the turning point the potential equals the energy."""
    z_m = turning_point(1.5)
    assert potential(z_m) == pytest.approx(1.5)


def test_turning_point_rejects_nonpositive_energy() -> None:
    """A non-positive energy raises ValueError."""
    with pytest.raises(ValueError, match="positive"):
        turning_point(0.0)


def test_vertical_frequency_tends_to_nu_max() -> None:
    """As E -> 0 the frequency approaches the small-oscillation value sqrt(2)."""
    assert vertical_frequency(1e-3) == pytest.approx(NU_MAX, rel=1e-2)


def test_vertical_frequency_decreases_with_energy() -> None:
    """The anharmonic frequency decreases with vertical energy."""
    assert vertical_frequency(2.0) < vertical_frequency(0.2)


def test_vertical_action_increases_with_energy() -> None:
    """The vertical action grows monotonically with energy and is finite."""
    j_low = vertical_action(0.3)
    j_high = vertical_action(2.0)
    assert np.isfinite(j_low) and 0.0 < j_low < j_high
