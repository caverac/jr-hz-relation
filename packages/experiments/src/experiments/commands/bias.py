"""``experiments bias`` -- print the provenance bias from the effective weight."""

from __future__ import annotations

import click

from experiments.form_factor import dispersion_ratio


@click.command("bias")
@click.option("--alpha", default=0.84, show_default=True, help="Spiral wavenumber alpha = k z0.")
@click.option("--strength", default=0.9, show_default=True, help="Spiral strength s = sigma_R^2/|Phi_s|.")
def bias(alpha: float, strength: float) -> None:
    """Print the predicted provenance bias at a given thickness and spiral strength."""
    ratio = dispersion_ratio(alpha, strength)
    click.echo(f"sigma_z,mig/sigma_z,all(alpha={alpha:.3f}, s={strength:.3f}) = {ratio:.4f}")
    click.echo(f"=> {100.0 * (1.0 - ratio):.1f}% colder migrators")
