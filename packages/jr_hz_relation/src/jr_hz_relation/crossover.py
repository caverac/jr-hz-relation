"""The trapping-to-diffusion crossover weight across the overlap transition.

Single-resonance corotation trapping gives a vertical migration weight
``W ~ F^{1/2}`` (the trapped census; see :mod:`jr_hz_relation.trapping`), capping the
provenance bias near 7 per cent. Once the corotation resonances of the spiral
spectrum overlap (Chirikov parameter ``S > 1``; see :mod:`jr_hz_relation.overlap`),
trapping is destroyed and the churning becomes quasilinear stochastic diffusion,
whose angular-momentum diffusion coefficient scales as the squared coupling
``D ~ |Psi|^2 ~ F^2`` -- the diffusive weight ``W ~ F^2`` (bias ~24 per cent).

The two regimes are the limits of a single crossover. The local overlap is itself
vertical-action dependent, ``S(J_z) = S0 sqrt(F(J_z,k))`` (since the libration width
scales as ``sqrt(F)``), so vertically cold stars (large ``F``) overlap first. We
model the migration weight as a power of the form factor whose exponent runs from
the trapping value ``1/2`` to the diffusive value ``2`` through a smooth gate
centred on the overlap threshold ``S = 1``,

    W(J_z) = F^{p},   p = 1/2 + (3/2) * Theta(S),   Theta(S) = S^2 / (1 + S^2),
    S(J_z) = S0 sqrt(F(J_z,k)),

with a single physical parameter ``S0``, the effective resonance overlap (about
unity for the bar plus spiral alone, larger once recurrent transient spirals are
included). The crossover sits at the critical form factor ``F_crit = 1/S0^2`` (where
``S = 1``), separating diffusive cold stars from confined hot stars. The endpoints
(``p = 1/2`` trapping, ``p = 2`` diffusion) are physical; the gate is the minimal
smooth model of the crossover sharpness.
"""

from __future__ import annotations

import numpy as np

from jr_hz_relation.form_factor import vertical_form_factor
from jr_hz_relation.sheet import vertical_frequency

#: Single-resonance trapping exponent ``W ~ F^{1/2}``.
TRAPPING_EXPONENT: float = 0.5

#: Quasilinear diffusion exponent ``W ~ F^2``.
DIFFUSION_EXPONENT: float = 2.0


def overlap_gate(overlap: float) -> float:
    """Smooth crossover gate ``Theta(S) = S^2 / (1 + S^2)``.

    Parameters
    ----------
    overlap :
        The local Chirikov overlap ``S = S0 sqrt(F)``, non-negative.

    Returns
    -------
    float
        The gate value, rising from 0 (isolated resonances) through 1/2 at the
        threshold ``S = 1`` to 1 (strong overlap).

    Raises
    ------
    ValueError
        If ``overlap`` is negative.
    """
    if overlap < 0.0:
        raise ValueError("overlap must be non-negative")
    return float(overlap**2 / (1.0 + overlap**2))


def crossover_weight(form_factor: float, overlap_strength: float) -> float:
    """Overlap-controlled migration weight ``W = F^{p}`` bridging trapping and diffusion.

    Parameters
    ----------
    form_factor :
        The vertical form factor ``F`` of the orbit, in ``(0, 1]``.
    overlap_strength :
        The effective resonance overlap ``S0``, non-negative.

    Returns
    -------
    float
        The migration weight, with exponent running from ``1/2`` (trapping) to ``2``
        (diffusion) as the local overlap ``S0 sqrt(F)`` crosses unity.

    Raises
    ------
    ValueError
        If ``form_factor`` is outside ``(0, 1]`` or ``overlap_strength`` is negative.
    """
    if not 0.0 < form_factor <= 1.0:
        raise ValueError("form_factor must lie in (0, 1]")
    if overlap_strength < 0.0:
        raise ValueError("overlap_strength must be non-negative")
    gate = overlap_gate(overlap_strength * np.sqrt(form_factor))
    exponent = TRAPPING_EXPONENT + (DIFFUSION_EXPONENT - TRAPPING_EXPONENT) * gate
    return float(form_factor**exponent)


def critical_form_factor(overlap_strength: float) -> float:
    """Form factor ``F_crit = 1/S0^2`` at the overlap threshold ``S = 1``.

    Parameters
    ----------
    overlap_strength :
        The effective resonance overlap ``S0``, strictly positive.

    Returns
    -------
    float
        The critical form factor; orbits with ``F > F_crit`` are in the diffusive
        regime. Returns values above 1 (no diffusive orbits) when ``S0 < 1``.

    Raises
    ------
    ValueError
        If ``overlap_strength`` is not strictly positive.
    """
    if overlap_strength <= 0.0:
        raise ValueError("overlap_strength must be positive")
    return float(1.0 / overlap_strength**2)


def crossover_dispersion_ratio(alpha: float, overlap_strength: float, e_max: float = 12.0, n: int = 120) -> float:
    """Provenance bias ``sigma_z,mig / sigma_z,all`` from the crossover weight.

    The ratio falls from the trapping floor (``W ~ F^{1/2}``, ~7 per cent bias) at
    ``overlap_strength -> 0`` toward the diffusive ceiling (``W ~ F^2``, ~24 per
    cent) as the overlap grows.

    Parameters
    ----------
    alpha :
        Dimensionless spiral wavenumber ``alpha = k z0``, non-negative.
    overlap_strength :
        The effective resonance overlap ``S0``, non-negative.
    e_max :
        Upper limit of the vertical-energy quadrature grid.
    n :
        Number of grid points.

    Returns
    -------
    float
        The ratio ``sigma_z,mig / sigma_z,all`` (below 1 for a real bias).
    """
    energies = np.linspace(1e-3, e_max, n)
    frequencies = np.array([vertical_frequency(float(e)) for e in energies])
    base = np.exp(-energies) * (2.0 * np.pi / frequencies)
    form = np.array([vertical_form_factor(float(e), alpha) for e in energies])
    weight = np.array([crossover_weight(float(value), overlap_strength) for value in form])

    mean_all = float(np.trapezoid(energies * base, energies) / np.trapezoid(base, energies))
    mean_mig = float(np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies))
    return float(np.sqrt(mean_mig / mean_all))
