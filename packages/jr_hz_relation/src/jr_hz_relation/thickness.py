"""Finite-thickness softening of the vertical form factor.

The razor-thin form factor uses the Laplace kernel ``e^{-k|z|}`` of an infinitely
thin spiral. A spiral of finite vertical scale height ``h_s`` distributes its mass in
``z`` and the felt potential is the convolution of ``e^{-k|z|}`` with that profile.
For an exponential spiral profile ``rho_s(z) = (1/2h_s) e^{-|z|/h_s}`` the convolution
is the softened kernel

    K(z) = [ beta e^{-k|z|} - k e^{-beta|z|} ] / (beta - k),     beta = 1/h_s,

which equals unity at ``z=0`` with zero slope there -- the midplane cusp of the
razor-thin kernel is rounded over the spiral scale. Its orbit average is a simple
combination of the bare form factor at the two wavenumbers,

    F_soft(J_z; alpha, h) = [ F(J_z, alpha) - alpha h F(J_z, 1/h) ] / (1 - alpha h),

with ``h = h_s / z0`` the spiral-to-disc thickness ratio. For ``h -> 0`` it recovers
the razor-thin ``F``; for ``h -> infinity`` it tends to unity (a vertically
structureless spiral cannot distinguish orbits). At the Galactic ``alpha ~ 1`` and
``h ~ 0.5``--``1`` the softening reduces the form-factor contrast and weakens the
single-resonance bias at the tens-of-per-cent level -- the order-unity correction
that the razor-thin treatment must carry.
"""

from __future__ import annotations

import numpy as np

from jr_hz_relation.form_factor import vertical_form_factor
from jr_hz_relation.sheet import vertical_frequency


def softened_form_factor(energy: float, alpha: float, thickness: float) -> float:
    """Finite-thickness vertical form factor ``F_soft(E; alpha, h)``.

    Parameters
    ----------
    energy :
        Vertical energy ``E``, strictly positive.
    alpha :
        Dimensionless spiral wavenumber ``alpha = k z0``, non-negative.
    thickness :
        Spiral-to-disc thickness ratio ``h = h_s / z0``, non-negative; ``0`` is the
        razor-thin limit.

    Returns
    -------
    float
        The softened form factor, between the razor-thin value and unity.

    Raises
    ------
    ValueError
        If ``alpha`` or ``thickness`` is negative.
    """
    if alpha < 0.0:
        raise ValueError("alpha must be non-negative")
    if thickness < 0.0:
        raise ValueError("thickness must be non-negative")
    if thickness == 0.0:
        return vertical_form_factor(energy, alpha)
    product = alpha * thickness
    if abs(1.0 - product) < 1e-6:  # avoid the beta = k degeneracy by a negligible nudge
        thickness *= 1.0 + 1e-4
        product = alpha * thickness
    beta = 1.0 / thickness
    bare = vertical_form_factor(energy, alpha)
    deep = vertical_form_factor(energy, beta)
    return float((bare - product * deep) / (1.0 - product))


def softened_dispersion_ratio(alpha: float, thickness: float, e_max: float = 12.0, n: int = 120) -> float:
    """Single-resonance bias ``sigma_z,mig/sigma_z,all`` with the softened form factor.

    Uses the trapping weight ``W = sqrt(F_soft)`` (the single-resonance reference) so
    the ratio rises toward unity -- the bias weakens -- as the spiral thickens.

    Parameters
    ----------
    alpha :
        Dimensionless spiral wavenumber ``alpha = k z0``, non-negative.
    thickness :
        Spiral-to-disc thickness ratio ``h = h_s / z0``, non-negative.
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
    form = np.array([softened_form_factor(float(e), alpha, thickness) for e in energies])
    weight = np.sqrt(np.clip(form, 1e-12, None))

    mean_all = float(np.trapezoid(energies * base, energies) / np.trapezoid(base, energies))
    mean_mig = float(np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies))
    return float(np.sqrt(mean_mig / mean_all))
