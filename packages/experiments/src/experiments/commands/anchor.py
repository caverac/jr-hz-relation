"""``experiments anchor`` -- spiral strength matching a target bias."""

from __future__ import annotations

import click

from experiments.form_factor import strength_matching_anchor


@click.command("anchor")
@click.option("--alpha", default=0.84, show_default=True, help="Spiral wavenumber alpha = k z0.")
@click.option("--target", required=True, type=float, help="Target dispersion ratio sigma_z,mig/sigma_z,all.")
def anchor(alpha: float, target: float) -> None:
    """Print the spiral strength that reproduces a target dispersion ratio."""
    strength = strength_matching_anchor(alpha, target)
    click.echo(f"spiral strength matching ratio {target:.2f} at alpha={alpha:.2f}: s={strength:.3f}")
