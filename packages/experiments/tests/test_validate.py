"""Tests for the galpy-based independent validation of the form factor."""

import pytest

from experiments.form_factor import vertical_form_factor
from experiments.validate import form_factor_orbit


@pytest.mark.parametrize("energy", [0.3, 1.0, 3.0])
@pytest.mark.parametrize("alpha", [0.3, 0.84, 2.0])
def test_orbit_matches_quadrature(energy: float, alpha: float) -> None:
    """The galpy orbit average reproduces the scipy quadrature form factor."""
    quad = vertical_form_factor(energy, alpha)
    orbit = form_factor_orbit(energy, alpha, n_periods=15, samples_per_period=300)
    assert orbit == pytest.approx(quad, abs=2e-3)


def test_orbit_form_factor_tends_to_one_at_midplane() -> None:
    """A near-midplane orbit feels the full in-plane amplitude (F -> 1 as E -> 0)."""
    assert form_factor_orbit(1e-5, 1.0) == pytest.approx(1.0, abs=5e-3)


def test_orbit_form_factor_decreases_with_energy() -> None:
    """A hotter (higher J_z) orbit couples more weakly to the spiral."""
    assert form_factor_orbit(2.0, 1.0) < form_factor_orbit(0.3, 1.0)


def test_orbit_form_factor_rejects_negative_alpha() -> None:
    """A negative wavenumber raises ValueError, matching the quadrature."""
    with pytest.raises(ValueError, match="non-negative"):
        form_factor_orbit(1.0, -0.1)
