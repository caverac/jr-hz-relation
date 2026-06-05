"""Exact corotation trapped fraction and the single-resonance bias cap.

The slow corotation Hamiltonian is a pendulum
``H = (1/2) g p^2 + Psi cos(theta_r)`` in the slow action ``p = L_z - L_CR``, with
libration island half-width ``p_max = 2 sqrt(Psi/|g|) ~ sqrt(F)`` (the coupling
``Psi = Phi_0 G(J_R) F(J_z,k)``; see :mod:`experiments.overlap`). For a Gaussian
parent distribution in ``p`` of dispersion ``sigma_p``, the fraction of stars inside
the separatrix is the exact trapped weight

    W(F; kappa) = (1/pi) INT_0^pi erf( kappa sqrt(F) sin(u) / sqrt(2) ) du,

where ``kappa = p_max(F=1) / sigma_p`` is the dimensionless island-width parameter
(``kappa ~ sqrt(spiral strength) / sigma_p``). In the dilute limit ``kappa -> 0``
the trapped fraction is proportional to ``sqrt(F)`` -- the island-area-counting law
``W ~ F^{1/2}`` -- and for ``kappa -> infinity`` it saturates to unity. Because the
dilute limit gives the steepest ``F``-weighting, the single-resonance provenance
bias is *capped* at the ``sqrt(F)`` value (about 7 per cent at the Milky-Way
thickness): no single corotation resonance, however strong, can reproduce the
measured ~20 per cent. That larger bias requires the resonance-overlap diffusive
regime of :mod:`experiments.overlap`.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import integrate

from experiments.form_factor import vertical_form_factor
from experiments.sheet import vertical_frequency


def trapped_fraction(form_factor: float, island_width: float) -> float:
    """Exact corotation trapped fraction ``W(F; kappa)`` of the pendulum island.

    Parameters
    ----------
    form_factor :
        The vertical form factor ``F`` of the orbit, in ``(0, 1]``.
    island_width :
        The dimensionless island-width parameter ``kappa = p_max(F=1)/sigma_p``,
        non-negative.

    Returns
    -------
    float
        The fraction of a Gaussian parent population trapped in the libration
        island, in ``[0, 1)``.

    Raises
    ------
    ValueError
        If ``form_factor`` is outside ``(0, 1]`` or ``island_width`` is negative.
    """
    if not 0.0 < form_factor <= 1.0:
        raise ValueError("form_factor must lie in (0, 1]")
    if island_width < 0.0:
        raise ValueError("island_width must be non-negative")
    lam = island_width * math.sqrt(form_factor)
    integral, _ = integrate.quad(
        lambda u: math.erf(lam * math.sin(u) / math.sqrt(2.0)),
        0.0,
        math.pi,
        limit=200,
    )
    return float(integral / math.pi)


def trapping_dispersion_ratio(alpha: float, island_width: float, e_max: float = 12.0, n: int = 120) -> float:
    """Provenance bias ``sigma_z,mig / sigma_z,all`` from the exact trapped fraction.

    The equilibrium vertical distribution is reweighted by
    :func:`trapped_fraction`; the ratio decreases toward the ``W ~ sqrt(F)`` cap as
    ``island_width -> 0`` and toward unity (no bias) as ``island_width -> infinity``.

    Parameters
    ----------
    alpha :
        Dimensionless spiral wavenumber ``alpha = k z0``, non-negative.
    island_width :
        The dimensionless island-width parameter ``kappa``, non-negative.
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
    weight = np.array([trapped_fraction(float(value), island_width) for value in form])

    mean_all = float(np.trapezoid(energies * base, energies) / np.trapezoid(base, energies))
    mean_mig = float(np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies))
    return float(np.sqrt(mean_mig / mean_all))
