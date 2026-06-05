"""Tests for the trapping-to-diffusion crossover weight."""

import numpy as np
import pytest

from experiments.crossover import (
    critical_form_factor,
    crossover_dispersion_ratio,
    crossover_weight,
    overlap_gate,
)


def test_overlap_gate_limits() -> None:
    """The gate runs from 0 (isolated) through 1/2 at threshold to 1 (overlap)."""
    assert overlap_gate(0.0) == pytest.approx(0.0)
    assert overlap_gate(1.0) == pytest.approx(0.5)
    assert overlap_gate(1e3) == pytest.approx(1.0, abs=1e-5)


def test_overlap_gate_rejects_negative() -> None:
    """A negative overlap raises ValueError."""
    with pytest.raises(ValueError, match="overlap"):
        overlap_gate(-0.1)


def test_crossover_weight_trapping_floor() -> None:
    """At zero overlap the weight is the trapping value W = sqrt(F)."""
    assert crossover_weight(0.5, 0.0) == pytest.approx(np.sqrt(0.5))


def test_crossover_weight_diffusion_ceiling() -> None:
    """At strong overlap the weight approaches the diffusive value W = F^2."""
    assert crossover_weight(0.5, 1e3) == pytest.approx(0.25, abs=1e-3)


def test_crossover_weight_steepens_with_overlap() -> None:
    """More overlap steepens the weight, lowering it for sub-unity form factors."""
    assert crossover_weight(0.5, 3.0) < crossover_weight(0.5, 0.0)


def test_crossover_weight_rejects_bad_inputs() -> None:
    """Invalid form factor or negative overlap strength raise ValueError."""
    with pytest.raises(ValueError, match="form_factor"):
        crossover_weight(0.0, 1.0)
    with pytest.raises(ValueError, match="overlap_strength"):
        crossover_weight(0.5, -1.0)


def test_critical_form_factor_value_and_guard() -> None:
    """F_crit = 1/S0^2, and a non-positive overlap raises ValueError."""
    assert critical_form_factor(2.0) == pytest.approx(0.25)
    with pytest.raises(ValueError, match="positive"):
        critical_form_factor(0.0)


def test_crossover_bias_rises_from_floor_to_ceiling() -> None:
    """The bias rises from the ~7% trapping floor toward the ~24% diffusion ceiling."""
    floor = 1.0 - crossover_dispersion_ratio(0.84, 0.0)
    ceiling = 1.0 - crossover_dispersion_ratio(0.84, 50.0)
    assert floor == pytest.approx(0.069, abs=0.01)
    assert ceiling == pytest.approx(0.236, abs=0.02)
    assert floor < 1.0 - crossover_dispersion_ratio(0.84, 2.0) < ceiling


def test_crossover_bias_brackets_measured() -> None:
    """The measured ~20% bias lies between the trapping floor and diffusion ceiling."""
    floor = 1.0 - crossover_dispersion_ratio(0.84, 0.0)
    ceiling = 1.0 - crossover_dispersion_ratio(0.84, 50.0)
    assert floor < 0.20 < ceiling
