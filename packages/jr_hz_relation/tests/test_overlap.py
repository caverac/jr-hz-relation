"""Tests for the Chirikov resonance-overlap criterion."""

import numpy as np
import pytest

from jr_hz_relation.overlap import (
    corotation_radius,
    libration_halfwidth,
    milky_way_overlap,
    overlap_parameter,
)


def test_corotation_radius_flat_curve() -> None:
    """The corotation radius is V_c / Omega_p."""
    assert corotation_radius(23.0, v_circ=230.0) == pytest.approx(10.0)


def test_corotation_radius_rejects_nonpositive() -> None:
    """A non-positive pattern speed or circular speed raises ValueError."""
    with pytest.raises(ValueError, match="positive"):
        corotation_radius(0.0)
    with pytest.raises(ValueError, match="positive"):
        corotation_radius(20.0, v_circ=-1.0)


def test_libration_halfwidth_scales_as_sqrt_strength() -> None:
    """The half-width grows as the square root of the spiral strength."""
    quad = libration_halfwidth(10.0, 0.04)
    single = libration_halfwidth(10.0, 0.01)
    assert quad == pytest.approx(2.0 * single)


def test_libration_halfwidth_value() -> None:
    """The half-width equals 2 R sqrt(epsilon G F) at unit reduction factors."""
    assert libration_halfwidth(10.0, 0.04) == pytest.approx(2.0 * 10.0 * np.sqrt(0.04))


def test_libration_halfwidth_rejects_bad_inputs() -> None:
    """Invalid radius, strength, or reduction factors raise ValueError."""
    with pytest.raises(ValueError, match="radius"):
        libration_halfwidth(0.0, 0.02)
    with pytest.raises(ValueError, match="non-negative"):
        libration_halfwidth(10.0, -0.01)
    with pytest.raises(ValueError, match="radial_factor and form_factor"):
        libration_halfwidth(10.0, 0.02, form_factor=1.5)
    with pytest.raises(ValueError, match="radial_factor and form_factor"):
        libration_halfwidth(10.0, 0.02, radial_factor=0.0)


def test_overlap_parameter_scales_as_sqrt_form_factor() -> None:
    """S scales as sqrt(F): quartering F halves the overlap parameter."""
    full = overlap_parameter(6.0, 11.5, 0.02, form_factor=1.0)
    quarter = overlap_parameter(6.0, 11.5, 0.02, form_factor=0.25)
    assert quarter == pytest.approx(0.5 * full)


def test_overlap_parameter_rejects_bad_ordering() -> None:
    """A non-increasing radius pair raises ValueError."""
    with pytest.raises(ValueError, match="outer_radius"):
        overlap_parameter(11.5, 6.0, 0.02)


def test_milky_way_overlap_at_threshold() -> None:
    """The MW bar-spiral overlap sits near unity for physical spiral strengths."""
    weak = milky_way_overlap(0.01)
    fiducial = milky_way_overlap(0.02)
    strong = milky_way_overlap(0.03)
    assert weak < 1.0 < strong
    assert fiducial == pytest.approx(0.91, abs=0.03)


def test_milky_way_overlap_cold_stars_cross_first() -> None:
    """At fixed strength, vertically cold stars overlap more than hot ones."""
    assert milky_way_overlap(0.03, form_factor=1.0) > milky_way_overlap(0.03, form_factor=0.5)
