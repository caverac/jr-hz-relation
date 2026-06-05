"""The vertical form factor and the analytic provenance bias.

A razor-thin spiral of radial wavenumber k has a potential that decays above the
plane as e^{-k|z|} (Laplace's equation in the source-free region; Binney & Tremaine
sec. 6). A star couples to the spiral through the angle-average of that decay over
its vertical orbit -- the vertical form factor

    F(J_z, k) = < e^{-k|z(theta_z, J_z)|} >_{theta_z}
              = (2/pi) INT_0^{z_m} e^{-k z} (nu_z / |v_z|) dz,

with F(0,k) = 1 and F decreasing monotonically in J_z. The migration efficiency
follows the Daniel & Wyse (2015, 2018) corotation-capture criterion (capture
requires the radial random energy within ~|Phi_s|), which we represent by an
in-plane captured fraction ~ exp(-sigma_R^2/|Phi_s|); reducing the felt well depth
by F gives the migrator weight W(J_z) = exp[-s(1/F - 1)] where s = sigma_R^2/|Phi_s|
is the spiral strength.
Reweighting the equilibrium vertical distribution by W yields the provenance bias
sigma_z,mig / sigma_z,all.

Everything is in the dimensionless sheet units of experiments.sheet, so the only
parameters are alpha = k z0 (thickness) and s (spiral strength).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy import integrate

from experiments.sheet import potential, turning_point, vertical_frequency


def vertical_form_factor(energy: float, alpha: float) -> float:
    """Vertical form factor ``F(E; alpha) = <e^{-alpha|z|}>`` over the orbit.

    Parameters
    ----------
    energy :
        Vertical energy ``E``, strictly positive.
    alpha :
        Dimensionless spiral wavenumber ``alpha = k z0``, non-negative.

    Returns
    -------
    float
        The form factor, which tends to 1 as ``E -> 0`` and decreases with ``E``.

    Raises
    ------
    ValueError
        If ``alpha`` is negative.
    """
    if alpha < 0.0:
        raise ValueError("alpha must be non-negative")
    z_m = turning_point(energy)
    nu = vertical_frequency(energy)
    integral, _ = integrate.quad(
        lambda s: np.exp(-alpha * z_m * s) / np.sqrt(np.maximum(2.0 * (energy - potential(z_m * s)), 1e-300)),
        0.0,
        1.0,
        points=[1.0],
        limit=200,
    )
    return float((2.0 / np.pi) * nu * z_m * integral)


def capture_weight(form_factor: float, spiral_strength: float) -> float:
    """Daniel-Wyse-grounded migrator weight ``W = exp[-s(1/F - 1)]``.

    Parameters
    ----------
    form_factor :
        The vertical form factor ``F`` of the orbit, in ``(0, 1]``.
    spiral_strength :
        The dimensionless spiral strength ``s = sigma_R^2 / |Phi_s|``,
        non-negative.

    Returns
    -------
    float
        The migration weight, normalised to 1 for a midplane orbit (``F = 1``).

    Raises
    ------
    ValueError
        If ``form_factor`` is outside ``(0, 1]`` or ``spiral_strength`` is
        negative.
    """
    if not 0.0 < form_factor <= 1.0:
        raise ValueError("form_factor must lie in (0, 1]")
    if spiral_strength < 0.0:
        raise ValueError("spiral_strength must be non-negative")
    return float(np.exp(-spiral_strength * (1.0 / form_factor - 1.0)))


def _energy_grid(e_max: float, n: int) -> NDArray[np.float64]:
    """Quadrature grid in vertical energy on ``(0, e_max]``."""
    return np.linspace(1e-3, e_max, n)


def _density_of_states(energies: NDArray[np.float64]) -> NDArray[np.float64]:
    """Vertical energy distribution ``dN/dE ~ e^{-E} * T(E)`` of the sheet."""
    nu = np.array([vertical_frequency(float(e)) for e in energies])
    return np.exp(-energies) * (2.0 * np.pi / nu)


def dispersion_ratio(alpha: float, spiral_strength: float, e_max: float = 12.0, n: int = 120) -> float:
    """Provenance bias ``sigma_z,mig / sigma_z,all`` at thickness ``alpha`` and strength ``s``.

    The migrator distribution is the equilibrium one reweighted by the capture
    weight; the ratio of mean vertical energies gives the squared dispersion
    ratio, whose root is returned.

    Parameters
    ----------
    alpha :
        Dimensionless spiral wavenumber ``alpha = k z0``, non-negative.
    spiral_strength :
        The dimensionless spiral strength ``s = sigma_R^2 / |Phi_s|``.
    e_max :
        Upper limit of the vertical-energy quadrature grid.
    n :
        Number of grid points.

    Returns
    -------
    float
        The ratio ``sigma_z,mig / sigma_z,all`` (below 1 for a real bias).
    """
    energies = _energy_grid(e_max, n)
    base = _density_of_states(energies)
    form = np.array([vertical_form_factor(float(e), alpha) for e in energies])
    weight = np.array([capture_weight(float(value), spiral_strength) for value in form])

    mean_all = float(np.trapezoid(energies * base, energies) / np.trapezoid(base, energies))
    mean_mig = float(np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies))
    return float(np.sqrt(mean_mig / mean_all))


def strength_matching_anchor(alpha: float, target_ratio: float, iterations: int = 48) -> float:
    """Spiral strength ``s`` reproducing ``target_ratio`` at thickness ``alpha``.

    The dispersion ratio decreases monotonically with ``s``, so a bisection on
    ``s`` converges to the value matching the observed provenance bias.

    Parameters
    ----------
    alpha :
        Dimensionless spiral wavenumber ``alpha = k z0``.
    target_ratio :
        The target ``sigma_z,mig / sigma_z,all`` in ``(0, 1)``.
    iterations :
        Number of bisection steps.

    Returns
    -------
    float
        The spiral strength ``s`` matching the target.

    Raises
    ------
    ValueError
        If ``target_ratio`` is not in ``(0, 1)``.
    """
    if not 0.0 < target_ratio < 1.0:
        raise ValueError("target_ratio must lie in (0, 1)")
    lo, hi = 1e-3, 20.0
    for _ in range(iterations):
        mid = 0.5 * (lo + hi)
        if dispersion_ratio(alpha, mid) > target_ratio:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
