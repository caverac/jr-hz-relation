"""``experiments thickness`` -- single-resonance bias with the finite-thickness F."""

from __future__ import annotations

import click

from experiments.thickness import softened_dispersion_ratio


@click.command("thickness")
@click.option("--alpha", default=0.84, show_default=True, help="Spiral wavenumber alpha = k z0.")
@click.option("--thickness", "spiral_thickness", default=0.5, show_default=True, help="Spiral-to-disc thickness h.")
def thickness(alpha: float, spiral_thickness: float) -> None:
    """Print the single-resonance bias with the finite-thickness form factor."""
    ratio = softened_dispersion_ratio(alpha, spiral_thickness)
    click.echo(f"finite-thickness bias(alpha={alpha:.3f}, h={spiral_thickness:.3f}): ratio={ratio:.4f}")
    click.echo(f"=> {100.0 * (1.0 - ratio):.1f}% colder (razor-thin h=0 gives ~7%; softens as the spiral thickens)")
