"""``experiments trapping`` -- bias from the exact corotation trapped fraction."""

from __future__ import annotations

import click

from experiments.trapping import trapping_dispersion_ratio


@click.command("trapping")
@click.option("--alpha", default=0.84, show_default=True, help="Spiral wavenumber alpha = k z0.")
@click.option("--island-width", "island_width", default=1.0, show_default=True, help="Island-width parameter kappa.")
def trapping(alpha: float, island_width: float) -> None:
    """Print the provenance bias from the exact corotation trapped fraction."""
    ratio = trapping_dispersion_ratio(alpha, island_width)
    click.echo(f"trapped-fraction bias(alpha={alpha:.3f}, kappa={island_width:.3f}): ratio={ratio:.4f}")
    click.echo(f"=> {100.0 * (1.0 - ratio):.1f}% colder (single-resonance; capped near 7% at the MW thickness)")
