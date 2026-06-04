"""Chirikov resonance overlap of spiral corotation resonances.

The single-resonance pendulum of the resonant-trapping picture (see the derivation
roadmap) traps stars in a corotation libration island whose half-width scales as the
square root of the coupling ``Psi = Phi_0 G(J_R) F(J_z, k)``. When two patterns
(e.g. the Milky Way bar and a spiral) have corotation radii closer than the sum of
their island half-widths, the islands overlap and the regular libration gives way to
stochastic, diffusive churning -- the Chirikov criterion, and the Minchev & Famaey
(2010) bar-spiral overlap mechanism.

For a flat rotation curve (``V_c`` constant) the corotation libration half-width is a
pure fraction of the corotation radius,

    dR / R = 2 sqrt(epsilon * G * F),     epsilon = |Phi_s| / V_c^2,

with ``G`` the radial reduction factor ``J_0(k a_R)`` and ``F`` the vertical form
factor. The overlap parameter of two corotation resonances at radii ``R_in < R_out``
is ``S = (dR_in + dR_out) / (R_out - R_in)``; ``S >= 1`` marks overlap. Because
``dR ~ sqrt(F)``, vertically cold stars (larger ``F``) have wider islands and cross
into the overlapping (diffusive) regime first -- so the diffusive channel is itself
biased toward vertically cold stars, steepening the provenance bias beyond the
single-resonance ``W = F^{1/2}`` law.
"""

from __future__ import annotations

import numpy as np

#: Milky Way circular speed (km/s).
MW_VCIRC: float = 230.0

#: Milky Way bar pattern speed (km/s/kpc).
MW_BAR_PATTERN_SPEED: float = 38.0

#: Milky Way spiral pattern speed (km/s/kpc).
MW_SPIRAL_PATTERN_SPEED: float = 20.0


def corotation_radius(pattern_speed: float, v_circ: float = MW_VCIRC) -> float:
    """Corotation radius ``R_CR = V_c / Omega_p`` for a flat rotation curve.

    Parameters
    ----------
    pattern_speed :
        Pattern speed ``Omega_p`` (km/s/kpc), strictly positive.
    v_circ :
        Circular speed ``V_c`` (km/s), strictly positive.

    Returns
    -------
    float
        The corotation radius in kpc.

    Raises
    ------
    ValueError
        If ``pattern_speed`` or ``v_circ`` is not strictly positive.
    """
    if pattern_speed <= 0.0 or v_circ <= 0.0:
        raise ValueError("pattern_speed and v_circ must be positive")
    return float(v_circ / pattern_speed)


def libration_halfwidth(radius: float, strength: float, radial_factor: float = 1.0, form_factor: float = 1.0) -> float:
    """Corotation libration half-width ``dR = 2 R sqrt(epsilon G F)`` (kpc).

    Parameters
    ----------
    radius :
        Corotation radius ``R_CR`` (kpc), strictly positive.
    strength :
        Fractional spiral strength ``epsilon = |Phi_s| / V_c^2``, non-negative.
    radial_factor :
        Radial reduction factor ``G(J_R) = J_0(k a_R)`` in ``(0, 1]``.
    form_factor :
        Vertical form factor ``F(J_z, k)`` in ``(0, 1]``.

    Returns
    -------
    float
        The libration half-width in kpc.

    Raises
    ------
    ValueError
        If ``radius`` is not positive, ``strength`` is negative, or either factor
        is outside ``(0, 1]``.
    """
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if strength < 0.0:
        raise ValueError("strength must be non-negative")
    if not 0.0 < radial_factor <= 1.0 or not 0.0 < form_factor <= 1.0:
        raise ValueError("radial_factor and form_factor must lie in (0, 1]")
    return float(2.0 * radius * np.sqrt(strength * radial_factor * form_factor))


def overlap_parameter(
    inner_radius: float,
    outer_radius: float,
    strength: float,
    radial_factor: float = 1.0,
    form_factor: float = 1.0,
) -> float:
    """Chirikov overlap ``S = (dR_in + dR_out) / (R_out - R_in)`` of two corotations.

    ``S >= 1`` marks resonance overlap and the onset of stochastic, diffusive
    churning. Since ``dR ~ sqrt(F)``, ``S`` scales as ``sqrt(form_factor)``.

    Parameters
    ----------
    inner_radius :
        Inner corotation radius (kpc), strictly positive.
    outer_radius :
        Outer corotation radius (kpc), strictly greater than ``inner_radius``.
    strength :
        Fractional spiral strength ``epsilon = |Phi_s| / V_c^2``, non-negative.
    radial_factor :
        Radial reduction factor ``G(J_R)`` in ``(0, 1]``.
    form_factor :
        Vertical form factor ``F(J_z, k)`` in ``(0, 1]``.

    Returns
    -------
    float
        The overlap parameter ``S``.

    Raises
    ------
    ValueError
        If ``outer_radius`` does not exceed ``inner_radius``.
    """
    if outer_radius <= inner_radius:
        raise ValueError("outer_radius must exceed inner_radius")
    inner = libration_halfwidth(inner_radius, strength, radial_factor, form_factor)
    outer = libration_halfwidth(outer_radius, strength, radial_factor, form_factor)
    return float((inner + outer) / (outer_radius - inner_radius))


def milky_way_overlap(strength: float, radial_factor: float = 1.0, form_factor: float = 1.0) -> float:
    """Overlap parameter of the Milky Way bar and spiral corotation resonances.

    Parameters
    ----------
    strength :
        Fractional spiral strength ``epsilon = |Phi_s| / V_c^2``, non-negative.
    radial_factor :
        Radial reduction factor ``G(J_R)`` in ``(0, 1]``.
    form_factor :
        Vertical form factor ``F(J_z, k)`` in ``(0, 1]``.

    Returns
    -------
    float
        The bar-spiral overlap parameter ``S`` for the fiducial Milky Way pattern
        speeds.
    """
    inner = corotation_radius(MW_BAR_PATTERN_SPEED)
    outer = corotation_radius(MW_SPIRAL_PATTERN_SPEED)
    return overlap_parameter(inner, outer, strength, radial_factor, form_factor)
