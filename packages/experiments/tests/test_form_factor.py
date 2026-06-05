"""Tests for the vertical form factor and the analytic provenance bias."""

import pytest

from experiments.form_factor import (
    capture_weight,
    dispersion_ratio,
    strength_matching_anchor,
    vertical_form_factor,
)


def test_form_factor_tends_to_one_at_midplane() -> None:
    """A near-midplane orbit feels the full in-plane amplitude (F -> 1 as E -> 0)."""
    near = vertical_form_factor(1e-3, 1.0)
    nearer = vertical_form_factor(1e-5, 1.0)
    assert near < nearer <= 1.0
    assert nearer == pytest.approx(1.0, abs=5e-3)


def test_form_factor_decreases_with_energy() -> None:
    """The form factor is monotonically suppressed for hotter (higher J_z) orbits."""
    assert vertical_form_factor(2.0, 1.0) < vertical_form_factor(0.3, 1.0) < 1.0


def test_form_factor_decreases_with_wavenumber() -> None:
    """A more tightly wound spiral (larger alpha) couples more weakly."""
    assert vertical_form_factor(1.0, 2.0) < vertical_form_factor(1.0, 0.5)


def test_form_factor_rejects_negative_alpha() -> None:
    """A negative wavenumber raises ValueError."""
    with pytest.raises(ValueError, match="non-negative"):
        vertical_form_factor(1.0, -0.1)


def test_capture_weight_unity_at_full_coupling() -> None:
    """The weight is 1 for a midplane orbit (F = 1)."""
    assert capture_weight(1.0, 0.9) == pytest.approx(1.0)


def test_capture_weight_suppressed_for_low_form_factor() -> None:
    """A reduced form factor suppresses the migration weight below 1."""
    assert 0.0 < capture_weight(0.5, 1.0) < 1.0


def test_capture_weight_rejects_bad_form_factor() -> None:
    """Form factors outside (0, 1] raise ValueError."""
    with pytest.raises(ValueError, match="form_factor"):
        capture_weight(0.0, 1.0)
    with pytest.raises(ValueError, match="form_factor"):
        capture_weight(1.5, 1.0)


def test_capture_weight_rejects_negative_strength() -> None:
    """A negative spiral strength raises ValueError."""
    with pytest.raises(ValueError, match="non-negative"):
        capture_weight(0.5, -1.0)


def test_dispersion_ratio_is_a_real_bias() -> None:
    """Migrators are vertically colder than the parent population (ratio < 1)."""
    ratio = dispersion_ratio(0.84, 0.9)
    assert 0.0 < ratio < 1.0


def test_dispersion_ratio_strengthens_with_thickness() -> None:
    """A thicker disc (larger alpha) yields a stronger bias (smaller ratio)."""
    assert dispersion_ratio(1.5, 0.9) < dispersion_ratio(0.4, 0.9)


def test_strength_matching_anchor_recovers_target() -> None:
    """The matched spiral strength reproduces the target ratio and is physical."""
    strength = strength_matching_anchor(0.84, 0.80)
    assert 0.5 < strength < 3.0
    assert dispersion_ratio(0.84, strength) == pytest.approx(0.80, abs=1e-2)


def test_strength_matching_anchor_rejects_bad_target() -> None:
    """A target ratio outside (0, 1) raises ValueError."""
    with pytest.raises(ValueError, match="target_ratio"):
        strength_matching_anchor(0.84, 1.0)
