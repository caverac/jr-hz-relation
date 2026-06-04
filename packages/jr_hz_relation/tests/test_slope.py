"""Tests for the structural J_R-h_Z slope and its age-running."""

import math

import pytest

from jr_hz_relation.slope import (
    G_PC,
    AVRExponents,
    SolarNeighbourhood,
    radial_action_scale,
    scale_height,
    slope_age_factor,
    slope_in_lsun_per_kpc,
    structural_slope,
)


def test_solar_angular_momentum() -> None:
    """L_sun = R0 V0 for the default solar neighbourhood."""
    env = SolarNeighbourhood()
    assert env.solar_angular_momentum == pytest.approx(8.2 * 233.0)


def test_scale_height_default_is_a_few_hundred_pc() -> None:
    """The default vertical scale height is a few hundred parsec."""
    assert scale_height(18.0, 50.0) == pytest.approx(479.6, rel=1e-3)


def test_radial_action_scale_linear_in_c_max() -> None:
    """The action scale is linear in c_max."""
    assert radial_action_scale(35.0, 0.037, 2.0) == pytest.approx(2.0 * 35.0**2 / 0.037)


def test_structural_slope_matches_factored_form() -> None:
    """The direct ratio equals the (pi G Sigma / kappa)(sigma_R/sigma_z)^2 form."""
    env = SolarNeighbourhood()
    factored = math.pi * G_PC * env.sigma_dyn / env.kappa * (env.sigma_R / env.sigma_z) ** 2
    assert structural_slope(env, 1.0) == pytest.approx(factored)


def test_slope_in_lsun_per_kpc_matches_palicio() -> None:
    """At c_max = 1 the slope reproduces the measured 3.69e-2 L_sun/kpc to ~few %."""
    env = SolarNeighbourhood()
    assert slope_in_lsun_per_kpc(env, 1.0) == pytest.approx(3.69e-2, rel=0.05)


def test_avr_slope_exponent() -> None:
    """The slope exponent is 2(beta_R - beta_z)."""
    assert AVRExponents(0.35, 0.50).slope_exponent == pytest.approx(-0.30)


def test_slope_age_factor_flattens_for_old_populations() -> None:
    """With beta_R < beta_z the slope of an old population is below the young one."""
    avr = AVRExponents(0.35, 0.50)
    assert slope_age_factor(8.0, 1.0, avr) < 1.0


def test_slope_age_factor_unity_at_reference() -> None:
    """The factor is unity at the reference age."""
    assert slope_age_factor(4.0, 4.0, AVRExponents(0.3, 0.5)) == pytest.approx(1.0)


def test_slope_age_factor_rejects_nonpositive_age() -> None:
    """Non-positive ages raise ValueError."""
    avr = AVRExponents(0.3, 0.5)
    with pytest.raises(ValueError, match="positive"):
        slope_age_factor(0.0, 1.0, avr)
    with pytest.raises(ValueError, match="positive"):
        slope_age_factor(1.0, -1.0, avr)
