"""Independent validation of the vertical form factor with galpy.

:mod:`jr_hz_relation.form_factor` computes ``F(J_z, k) = <e^{-k|z|}>`` by a direct
scipy quadrature over the analytic isothermal-sheet orbit. This module recomputes
the *same* quantity by an entirely independent route: it integrates the vertical
orbit with galpy's own C orbit integrator inside galpy's C-implemented
:class:`~galpy.potential.IsothermalDiskPotential`, and time-averages ``e^{-k|z|}``
over an integer number of vertical periods. Because the vertical angle advances
uniformly in time, that time-average equals the angle-average that defines the form
factor, so the two numbers must agree -- a cross-check of the central object of the
paper that shares no code with the quadrature.

galpy's isothermal disk has the same functional form ``Phi(z) = 2 ln cosh(z / H)``
as the sheet of :mod:`jr_hz_relation.sheet` (with ``G = sigma_z = z0 = 1``), but its
scale height ``H`` follows galpy's own normalisation. ``H`` is therefore calibrated
once, at import, directly from galpy's potential -- no hard-coded constant -- and
used to rescale galpy's orbit back into the sheet units in which ``alpha = k z0``.
"""

from __future__ import annotations

import numpy as np
from galpy.orbit import Orbit
from galpy.potential import IsothermalDiskPotential, evaluatelinearPotentials

from jr_hz_relation.sheet import vertical_frequency

#: galpy's C-implemented self-gravitating isothermal disk, ``Phi(z) = 2 ln cosh(z/H)``.
_POTENTIAL = IsothermalDiskPotential(amp=1.0, sigma=1.0)


def _scale_height() -> float:
    """Calibrate galpy's disk scale height ``H`` against ``Phi = 2 ln cosh(z/H)``.

    The scale height is recovered from galpy's own potential by inverting
    ``Phi(z) = 2 ln cosh(z / H)`` at a reference height, so the validation carries
    no hand-tuned normalisation constant.

    Returns
    -------
    float
        The scale height ``H`` of galpy's :class:`IsothermalDiskPotential` in the
        units ``G = sigma_z = z0 = 1``.
    """
    reference = 1.0
    phi = float(evaluatelinearPotentials(_POTENTIAL, reference)) - float(evaluatelinearPotentials(_POTENTIAL, 0.0))
    return float(reference / np.arccosh(np.exp(phi / 2.0)))


#: galpy scale height in sheet units, calibrated from the potential at import.
_SCALE_HEIGHT = _scale_height()


def form_factor_orbit(energy: float, alpha: float, n_periods: int = 30, samples_per_period: int = 600) -> float:
    """Form factor ``F(E; alpha)`` from a galpy vertical-orbit integration.

    The vertical orbit of a star of energy ``E`` is integrated in galpy's isothermal
    disk and ``e^{-alpha|z|}`` is averaged over ``n_periods`` complete vertical
    periods. This reproduces :func:`jr_hz_relation.form_factor.vertical_form_factor`
    by an independent integrator and potential implementation.

    Parameters
    ----------
    energy :
        Vertical energy ``E``, strictly positive.
    alpha :
        Dimensionless spiral wavenumber ``alpha = k z0``, non-negative.
    n_periods :
        Number of complete vertical periods to average over.
    samples_per_period :
        Time samples per vertical period.

    Returns
    -------
    float
        The orbit-averaged form factor, to be compared with the quadrature value.

    Raises
    ------
    ValueError
        If ``alpha`` is negative.
    """
    if alpha < 0.0:
        raise ValueError("alpha must be non-negative")
    sheet_period = 2.0 * np.pi / vertical_frequency(energy)
    galpy_period = sheet_period * _SCALE_HEIGHT
    times = np.linspace(0.0, n_periods * galpy_period, n_periods * samples_per_period)
    orbit = Orbit([0.0, float(np.sqrt(2.0 * energy))])
    orbit.integrate(times, _POTENTIAL, method="dop853_c")
    heights = np.abs(orbit.x(times)) / _SCALE_HEIGHT
    return float(np.mean(np.exp(-alpha * heights)))
