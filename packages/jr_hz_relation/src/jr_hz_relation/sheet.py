"""Self-consistent isothermal stellar sheet and its vertical action-angle structure.

The vertical structure that fixes the disc scale height, and the vertical orbit the
spiral form factor is averaged over, both come from the self-gravitating isothermal
(Spitzer 1942) sheet. In dimensionless units G = sigma_z = z0 = 1 it has

    Phi(z) = 2 ln cosh z,  rho(z) = rho0 sech^2 z,  rho0 = 1/(2 pi),  nu_max = sqrt(2),

and the isothermal distribution function f0(E) = rho0/sqrt(2 pi) e^{-E}. A star of
vertical energy E oscillates anharmonically between turning points +/- z_m; this
module provides z_m, the vertical action J_z(E), and the frequency nu_z(E) by
quadrature.
"""

from __future__ import annotations

import numpy as np
from scipy import integrate

#: Midplane density rho0 in units G = sigma_z = z0 = 1.
RHO0: float = 1.0 / (2.0 * np.pi)

#: Small-oscillation (midplane) vertical frequency nu_max = sqrt(4 pi G rho0).
NU_MAX: float = float(np.sqrt(2.0))


def potential(z: float) -> float:
    """Vertical potential of the isothermal sheet.

    Parameters
    ----------
    z :
        Height above the midplane, in units of the scale height.

    Returns
    -------
    float
        The potential ``Phi(z) = 2 ln cosh z``.
    """
    return float(2.0 * np.log(np.cosh(z)))


def density(z: float) -> float:
    """Equilibrium density of the isothermal sheet.

    Parameters
    ----------
    z :
        Height above the midplane, in units of the scale height.

    Returns
    -------
    float
        The density ``rho(z) = rho0 sech^2 z``.
    """
    return float(RHO0 / np.cosh(z) ** 2)


def turning_point(energy: float) -> float:
    """Vertical turning point ``z_m`` where ``Phi(z_m) = E``.

    Parameters
    ----------
    energy :
        Vertical energy ``E``, strictly positive.

    Returns
    -------
    float
        The turning point ``z_m = arccosh(exp(E / 2))``.

    Raises
    ------
    ValueError
        If ``energy`` is not strictly positive.
    """
    if energy <= 0.0:
        raise ValueError("energy must be positive")
    return float(np.arccosh(np.exp(energy / 2.0)))


def vertical_frequency(energy: float) -> float:
    """Vertical orbital frequency ``nu_z(E) = 2 pi / T``.

    Parameters
    ----------
    energy :
        Vertical energy ``E``, strictly positive.

    Returns
    -------
    float
        The frequency, obtained from the quarter-period quadrature.
    """
    z_m = turning_point(energy)
    quarter, _ = integrate.quad(
        lambda s: 1.0 / np.sqrt(np.maximum(2.0 * (energy - potential(z_m * s)), 1e-300)),
        0.0,
        1.0,
        points=[1.0],
        limit=200,
    )
    return float(2.0 * np.pi / (4.0 * z_m * quarter))


def vertical_action(energy: float) -> float:
    """Vertical action ``J_z(E) = (1/pi) INT |v_z| dz``.

    Parameters
    ----------
    energy :
        Vertical energy ``E``, strictly positive.

    Returns
    -------
    float
        The vertical action of the orbit.
    """
    z_m = turning_point(energy)
    integral, _ = integrate.quad(
        lambda s: np.sqrt(np.maximum(2.0 * (energy - potential(z_m * s)), 0.0)),
        0.0,
        1.0,
        limit=200,
    )
    return float(2.0 / np.pi * z_m * integral)
