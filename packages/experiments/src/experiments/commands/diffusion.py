"""``experiments diffusion`` -- diffusive bias from the Balescu-Lenard weight."""

from __future__ import annotations

import click

from experiments.balescu_lenard import bl_dispersion_ratio


@click.command("diffusion")
@click.option("--alpha", default=0.84, show_default=True, help="Spiral wavenumber alpha = k z0.")
@click.option("--broadening", default=3.0, show_default=True, help="Resonance-broadening parameter b.")
def diffusion(alpha: float, broadening: float) -> None:
    """Print the diffusive provenance bias from the Balescu-Lenard weight."""
    ratio = bl_dispersion_ratio(alpha, broadening)
    click.echo(f"Balescu-Lenard bias(alpha={alpha:.3f}, b={broadening:.3f}): ratio={ratio:.4f}")
    click.echo(f"=> {100.0 * (1.0 - ratio):.1f}% colder (derived diffusive band ~19-24%; F^2 at b=0 to F^1.5)")
