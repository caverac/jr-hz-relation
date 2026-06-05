"""Tests for the finite-thickness softening of the form factor."""

import pytest

from experiments.form_factor import vertical_form_factor
from experiments.thickness import softened_dispersion_ratio, softened_form_factor


def test_softened_recovers_razor_thin_at_zero_thickness() -> None:
    """A razor-thin spiral (h=0) recovers the bare form factor."""
    assert softened_form_factor(1.0, 0.84, 0.0) == pytest.approx(vertical_form_factor(1.0, 0.84))


def test_softening_raises_the_form_factor() -> None:
    """Finite thickness rounds the kernel, raising F toward unity."""
    assert softened_form_factor(1.0, 0.84, 0.5) > vertical_form_factor(1.0, 0.84)


def test_softened_tends_to_unity_for_thick_spiral() -> None:
    """A very thick spiral has no vertical structure: F_soft -> 1."""
    assert softened_form_factor(1.0, 0.84, 50.0) == pytest.approx(1.0, abs=0.05)


def test_softened_handles_degenerate_thickness() -> None:
    """The beta = k point (thickness = 1/alpha) is guarded and returns a finite value."""
    value = softened_form_factor(1.0, 0.84, 1.0 / 0.84)
    assert 0.0 < value < 1.0


def test_softened_rejects_bad_inputs() -> None:
    """Negative alpha or thickness raises ValueError."""
    with pytest.raises(ValueError, match="alpha"):
        softened_form_factor(1.0, -0.1, 0.5)
    with pytest.raises(ValueError, match="thickness"):
        softened_form_factor(1.0, 0.84, -0.5)


def test_softened_dispersion_ratio_weakens_with_thickness() -> None:
    """A thicker spiral weakens the bias (ratio closer to 1)."""
    thin = softened_dispersion_ratio(0.84, 0.0)
    thick = softened_dispersion_ratio(0.84, 1.0)
    assert thin < thick < 1.0


def test_softened_dispersion_ratio_matches_sqrt_f_at_zero_thickness() -> None:
    """At zero thickness the bias is the razor-thin single-resonance value (~7%)."""
    assert 1.0 - softened_dispersion_ratio(0.84, 0.0) == pytest.approx(0.069, abs=0.01)
