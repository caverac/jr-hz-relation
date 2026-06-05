"""Tests for the Balescu-Lenard resonance-broadened diffusive weight."""

import pytest

from experiments.balescu_lenard import bl_dispersion_ratio, diffusion_weight


def test_diffusion_weight_quasilinear_limit() -> None:
    """At zero broadening the weight is the quasilinear F^2."""
    assert diffusion_weight(0.5, 0.0) == pytest.approx(0.25)


def test_diffusion_weight_broadened_limit() -> None:
    """At strong broadening the weight shape tends to F^{3/2} (a 1/b prefactor cancels)."""
    ratio = diffusion_weight(0.4, 1e6) / diffusion_weight(0.1, 1e6)
    assert ratio == pytest.approx((0.4 / 0.1) ** 1.5, rel=1e-3)


def test_diffusion_weight_decreases_with_broadening() -> None:
    """Broadening softens the weight (smaller for a sub-unity form factor)."""
    assert diffusion_weight(0.5, 5.0) < diffusion_weight(0.5, 0.0)


def test_diffusion_weight_rejects_bad_inputs() -> None:
    """Invalid form factor or negative broadening raise ValueError."""
    with pytest.raises(ValueError, match="form_factor"):
        diffusion_weight(0.0, 1.0)
    with pytest.raises(ValueError, match="broadening"):
        diffusion_weight(0.5, -1.0)


def test_bl_bias_pinned_to_diffusive_band() -> None:
    """The diffusive bias sits in the narrow F^{3/2}--F^2 band (~19-24%)."""
    ceiling = 1.0 - bl_dispersion_ratio(0.84, 0.0)
    floor = 1.0 - bl_dispersion_ratio(0.84, 1e6)
    assert ceiling == pytest.approx(0.237, abs=0.01)
    assert floor == pytest.approx(0.187, abs=0.01)
    assert floor < 1.0 - bl_dispersion_ratio(0.84, 3.0) < ceiling


def test_bl_band_brackets_measured() -> None:
    """The measured ~20% lies inside the derived diffusive band."""
    ceiling = 1.0 - bl_dispersion_ratio(0.84, 0.0)
    floor = 1.0 - bl_dispersion_ratio(0.84, 1e6)
    assert floor < 0.20 < ceiling
