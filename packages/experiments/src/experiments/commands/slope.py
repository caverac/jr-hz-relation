"""``experiments slope`` -- print the structural J_R-h_Z slope."""

from __future__ import annotations

import click

from experiments.slope import SolarNeighbourhood, slope_in_lsun_per_kpc


@click.command("slope")
@click.option("--c-max", "c_max", default=1.0, show_default=True, help="Action conversion factor c_max.")
def slope(c_max: float) -> None:
    """Print the structural slope in L_sun/kpc for the default solar neighbourhood."""
    env = SolarNeighbourhood()
    value = slope_in_lsun_per_kpc(env, c_max)
    click.echo(f"structural slope (c_max={c_max:.2f}) = {value:.3e} L_sun/kpc")
    click.echo("Palicio+2024 measured = 3.69e-2 L_sun/kpc")
