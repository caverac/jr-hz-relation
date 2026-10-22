"""``experiments overlap`` -- the Milky Way bar-spiral Chirikov overlap parameter."""

from __future__ import annotations

import click

from experiments.overlap import MW_BAR_PATTERN_SPEED, MW_SPIRAL_PATTERN_SPEED, corotation_radius, overlap_parameter


@click.command("overlap")
@click.option("--strength", default=0.02, show_default=True, help="Fractional spiral strength epsilon.")
@click.option("--form-factor", "form_factor", default=1.0, show_default=True, help="Vertical form factor F.")
@click.option(
    "--bar-speed", "bar_speed", default=MW_BAR_PATTERN_SPEED, show_default=True, help="Bar Omega_p (km/s/kpc)."
)
@click.option(
    "--spiral-speed",
    "spiral_speed",
    default=MW_SPIRAL_PATTERN_SPEED,
    show_default=True,
    help="Spiral Omega_p (km/s/kpc).",
)
def overlap(strength: float, form_factor: float, bar_speed: float, spiral_speed: float) -> None:
    """Print the Milky Way bar-spiral Chirikov overlap parameter.

    The bar and spiral pattern speeds set the two corotation radii on the flat rotation
    curve; the spiral must corotate outside the bar.
    """
    inner, outer = corotation_radius(bar_speed), corotation_radius(spiral_speed)
    value = overlap_parameter(inner, outer, strength, form_factor=form_factor)
    regime = "overlap (diffusive)" if value >= 1.0 else "regular (trapping)"
    click.echo(f"R_CR bar = {inner:.2f} kpc, R_CR spiral = {outer:.2f} kpc")
    click.echo(f"S(eps={strength:.3f}, F={form_factor:.2f}) = {value:.3f} -> {regime}")
