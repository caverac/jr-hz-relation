"""An analytic provenance bias and the spiral J_R-h_Z relation."""

from experiments.form_factor import (
    capture_weight,
    dispersion_ratio,
    strength_matching_anchor,
    vertical_form_factor,
)
from experiments.sheet import (
    NU_MAX,
    RHO0,
    density,
    potential,
    turning_point,
    vertical_action,
    vertical_frequency,
)
from experiments.slope import (
    AVRExponents,
    SolarNeighbourhood,
    radial_action_scale,
    scale_height,
    slope_age_factor,
    slope_in_lsun_per_kpc,
    structural_slope,
)

__version__ = "0.1.0"

__all__ = [
    "AVRExponents",
    "NU_MAX",
    "RHO0",
    "SolarNeighbourhood",
    "capture_weight",
    "density",
    "dispersion_ratio",
    "potential",
    "radial_action_scale",
    "scale_height",
    "slope_age_factor",
    "slope_in_lsun_per_kpc",
    "strength_matching_anchor",
    "structural_slope",
    "turning_point",
    "vertical_action",
    "vertical_form_factor",
    "vertical_frequency",
    "__version__",
]
