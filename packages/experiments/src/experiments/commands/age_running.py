"""``experiments age-running`` -- print the slope age-running factor."""

from __future__ import annotations

import click

from experiments.slope import AVRExponents, slope_age_factor


@click.command("age-running")
@click.option("--age", default=8.0, show_default=True, help="Population age (Gyr).")
@click.option("--ref", default=1.0, show_default=True, help="Reference age (Gyr).")
@click.option("--beta-r", "beta_r", default=0.35, show_default=True, help="Radial AVR exponent.")
@click.option("--beta-z", "beta_z", default=0.50, show_default=True, help="Vertical AVR exponent.")
def age_running(age: float, ref: float, beta_r: float, beta_z: float) -> None:
    """Print the slope age-running factor between two ages."""
    avr = AVRExponents(beta_r, beta_z)
    factor = slope_age_factor(age, ref, avr)
    click.echo(f"2(beta_R - beta_z) = {avr.slope_exponent:+.3f}")
    click.echo(f"a({age:g} Gyr)/a({ref:g} Gyr) = {factor:.3f}")
