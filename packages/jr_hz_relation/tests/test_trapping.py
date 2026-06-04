"""Tests for the exact corotation trapped fraction and the bias cap."""

import numpy as np
import pytest

from jr_hz_relation.trapping import trapped_fraction, trapping_dispersion_ratio


def test_trapped_fraction_in_unit_interval() -> None:
    """The trapped fraction lies in (0, 1)."""
    assert 0.0 < trapped_fraction(0.6, 1.0) < 1.0


def test_trapped_fraction_dilute_limit_scales_as_sqrt_form_factor() -> None:
    """For a narrow island W ~ sqrt(F): W(1)/W(0.5) -> sqrt(2)."""
    ratio = trapped_fraction(1.0, 0.05) / trapped_fraction(0.5, 0.05)
    assert ratio == pytest.approx(np.sqrt(2.0), abs=2e-3)


def test_trapped_fraction_saturates_for_wide_island() -> None:
    """A wide island traps essentially the whole parent population."""
    assert trapped_fraction(1.0, 30.0) == pytest.approx(1.0, abs=2e-2)


def test_trapped_fraction_increases_with_island_width() -> None:
    """More coupling (larger kappa) traps a larger fraction."""
    assert trapped_fraction(0.6, 0.5) < trapped_fraction(0.6, 2.0)


def test_trapped_fraction_rejects_bad_inputs() -> None:
    """Invalid form factor or negative island width raise ValueError."""
    with pytest.raises(ValueError, match="form_factor"):
        trapped_fraction(0.0, 1.0)
    with pytest.raises(ValueError, match="island_width"):
        trapped_fraction(0.5, -1.0)


def test_trapping_dispersion_ratio_is_a_real_bias() -> None:
    """The exact trapped fraction yields a genuine bias (ratio < 1)."""
    assert 0.0 < trapping_dispersion_ratio(0.84, 1.0) < 1.0


def test_trapping_bias_capped_at_sqrt_f_limit() -> None:
    """The bias is maximal in the dilute limit and weakens with island width."""
    cap = 1.0 - trapping_dispersion_ratio(0.84, 1e-3)
    finite = 1.0 - trapping_dispersion_ratio(0.84, 3.0)
    assert finite < cap
    assert cap == pytest.approx(0.069, abs=0.01)


def test_trapping_bias_cap_below_measured() -> None:
    """Single-resonance trapping cannot reach the measured ~20 per cent bias."""
    cap = 1.0 - trapping_dispersion_ratio(0.84, 1e-3)
    assert cap < 0.20
