"""First-principles Balescu-Lenard churning diffusion and the diffusive weight.

The inhomogeneous Balescu-Lenard / quasilinear corotation diffusion coefficient in
angular momentum is ``D_Lz(J) = pi Sum_m |Psi_m(J)|^2 C_m(Omega(J))`` -- the
resonance condition collapses the pattern-speed integral -- with the resonant
coupling ``Psi_m = Phi_0 J_0(k a_R) F(J_z,k)`` of the corotation Hamiltonian. Hence
the bare diffusive migration weight is ``W ~ |Psi|^2 ~ F^2``: the ``F^2`` diffusion
ceiling, here *derived* rather than assumed (the tightly-wound Balescu-Lenard
diffusion of Fouvry, Pichon & Chavanis 2015).

A finite libration width ``Delta_omega ~ sqrt(Psi) ~ sqrt(F)`` broadens the resonant
denominator (Dupree 1966); with a Lorentzian spiral fluctuation spectrum of width
``W_s`` the broadened diffusion coefficient is the closed form

    W(J_z) = F^2 / (1 + b sqrt(F)),     b = Delta_omega(F=1) / W_s,

with a single physical broadening parameter ``b`` -- the ratio of the libration width
to the spectral width. It interpolates the decorrelated quasilinear limit ``W ~ F^2``
(``b -> 0``) and the coherent, resonance-broadened limit ``W ~ F^{3/2}``
(``b -> infinity``). The provenance bias in this diffusive regime is therefore pinned
to a narrow, *derived* band (about 19-24 per cent at the Milky-Way thickness),
nearly independent of ``b`` -- so the observed bias follows from the disc being in
the diffusive (resonance-overlap) regime, with no tuned parameter. The trapping floor
(``W ~ F^{1/2}``, ~7 per cent) is the separate non-diffusive regime below overlap.
"""

from __future__ import annotations

import numpy as np

from jr_hz_relation.form_factor import vertical_form_factor
from jr_hz_relation.sheet import vertical_frequency


def diffusion_weight(form_factor: float, broadening: float) -> float:
    """Resonance-broadened Balescu-Lenard diffusive weight ``W = F^2/(1 + b sqrt(F))``.

    Parameters
    ----------
    form_factor :
        The vertical form factor ``F`` of the orbit, in ``(0, 1]``.
    broadening :
        The broadening parameter ``b = Delta_omega / W_s``, non-negative.

    Returns
    -------
    float
        The diffusive migration weight, interpolating ``F^2`` (``b=0``) and
        ``F^{3/2}`` (``b -> infinity``).

    Raises
    ------
    ValueError
        If ``form_factor`` is outside ``(0, 1]`` or ``broadening`` is negative.
    """
    if not 0.0 < form_factor <= 1.0:
        raise ValueError("form_factor must lie in (0, 1]")
    if broadening < 0.0:
        raise ValueError("broadening must be non-negative")
    return float(form_factor**2 / (1.0 + broadening * np.sqrt(form_factor)))


def bl_dispersion_ratio(alpha: float, broadening: float, e_max: float = 12.0, n: int = 120) -> float:
    """Provenance bias ``sigma_z,mig/sigma_z,all`` from the Balescu-Lenard weight.

    The ratio varies only weakly with ``broadening`` -- the diffusive bias is pinned
    to a narrow band between the ``F^2`` and ``F^{3/2}`` limits.

    Parameters
    ----------
    alpha :
        Dimensionless spiral wavenumber ``alpha = k z0``, non-negative.
    broadening :
        The broadening parameter ``b``, non-negative.
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
    weight = np.array([diffusion_weight(float(value), broadening) for value in form])

    mean_all = float(np.trapezoid(energies * base, energies) / np.trapezoid(base, energies))
    mean_mig = float(np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies))
    return float(np.sqrt(mean_mig / mean_all))
