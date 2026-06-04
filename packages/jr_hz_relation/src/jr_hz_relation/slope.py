"""The structural J_R-h_Z slope and its age-running.

Combining the self-gravitating isothermal sheet h_Z = sigma_z^2 / (pi G Sigma) with
the epicyclic radial action J_R^max = c_max sigma_R^2 / kappa gives the Palicio et
al. (2024) slope as the squared radial-to-vertical heating-anisotropy ratio,

    a = J_R^max / h_Z = c_max (pi G Sigma / kappa) (sigma_R / sigma_z)^2.

Because each channel obeys a secular age-velocity-dispersion relation
sigma ~ age^beta, the slope runs with population age as
a(age) ~ age^{2(beta_R - beta_z)}.

Units: G in pc (km/s)^2 / Msun, Sigma in Msun/pc^2, kappa in (km/s)/pc, dispersions
in km/s; the slope is then in km/s (action per unit length), converted to
L_sun/kpc with L_sun = R0 V0.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

#: Gravitational constant in pc (km/s)^2 / Msun.
G_PC: float = 4.30091e-3


@dataclass(frozen=True)
class SolarNeighbourhood:
    """Solar-neighbourhood inputs for the structural slope.

    Attributes
    ----------
    sigma_dyn :
        Total dynamical surface density within ~1 scale height, in Msun/pc^2.
    kappa :
        Epicyclic frequency at R0, in (km/s)/pc.
    sigma_R :
        Radial velocity dispersion of the spiral population, in km/s.
    sigma_z :
        Vertical velocity dispersion of the same population, in km/s.
    R0 :
        Solar galactocentric radius, in kpc.
    V0 :
        Circular speed at R0, in km/s.
    """

    sigma_dyn: float = 50.0
    kappa: float = 0.037
    sigma_R: float = 35.0
    sigma_z: float = 18.0
    R0: float = 8.2
    V0: float = 233.0

    @property
    def solar_angular_momentum(self) -> float:
        """Solar angular momentum ``L_sun = R0 V0`` in kpc km/s."""
        return self.R0 * self.V0


def scale_height(sigma_z: float, sigma_dyn: float) -> float:
    """Isothermal self-gravitating-sheet scale height in pc.

    Parameters
    ----------
    sigma_z :
        Vertical velocity dispersion, in km/s.
    sigma_dyn :
        Total dynamical surface density, in Msun/pc^2.

    Returns
    -------
    float
        The scale height ``h_Z = sigma_z^2 / (pi G Sigma)``.
    """
    return sigma_z**2 / (math.pi * G_PC * sigma_dyn)


def radial_action_scale(sigma_R: float, kappa: float, c_max: float) -> float:
    """Characteristic spiral-arm radial action ``c_max sigma_R^2 / kappa`` in pc km/s.

    Parameters
    ----------
    sigma_R :
        Radial velocity dispersion, in km/s.
    kappa :
        Epicyclic frequency, in (km/s)/pc.
    c_max :
        Order-unity factor converting the characteristic to the maximum action.

    Returns
    -------
    float
        The radial action scale in pc km/s.
    """
    return c_max * sigma_R**2 / kappa


def structural_slope(env: SolarNeighbourhood, c_max: float) -> float:
    """Structural slope ``a = J_R^max / h_Z`` in km/s.

    Parameters
    ----------
    env :
        The solar-neighbourhood inputs.
    c_max :
        Order-unity action-scale factor.

    Returns
    -------
    float
        The slope in km/s (action per unit length).
    """
    return radial_action_scale(env.sigma_R, env.kappa, c_max) / scale_height(env.sigma_z, env.sigma_dyn)


def slope_in_lsun_per_kpc(env: SolarNeighbourhood, c_max: float) -> float:
    """Structural slope converted to Palicio's ``L_sun/kpc`` units.

    Parameters
    ----------
    env :
        The solar-neighbourhood inputs.
    c_max :
        Order-unity action-scale factor.

    Returns
    -------
    float
        The slope in L_sun/kpc.
    """
    return structural_slope(env, c_max) / env.solar_angular_momentum


@dataclass(frozen=True)
class AVRExponents:
    """Radial and vertical age-velocity-dispersion exponents ``sigma ~ age^beta``.

    Attributes
    ----------
    beta_R :
        Radial AVR exponent.
    beta_z :
        Vertical AVR exponent.
    """

    beta_R: float
    beta_z: float

    @property
    def slope_exponent(self) -> float:
        """Exponent of the slope's age-running, ``2(beta_R - beta_z)``."""
        return 2.0 * (self.beta_R - self.beta_z)


def slope_age_factor(age_gyr: float, ref_gyr: float, avr: AVRExponents) -> float:
    """Slope ratio ``a(age) / a(ref) = (age/ref)^{2(beta_R - beta_z)}``.

    Parameters
    ----------
    age_gyr :
        Population age, in Gyr, strictly positive.
    ref_gyr :
        Reference age, in Gyr, strictly positive.
    avr :
        The radial and vertical AVR exponents.

    Returns
    -------
    float
        The slope ratio relative to the reference age.

    Raises
    ------
    ValueError
        If either age is not strictly positive.
    """
    if age_gyr <= 0.0 or ref_gyr <= 0.0:
        raise ValueError("ages must be positive")
    return float((age_gyr / ref_gyr) ** avr.slope_exponent)
