"""``experiments crossover`` -- bias from the trapping-to-diffusion crossover weight."""

from __future__ import annotations

import click

from experiments.crossover import crossover_dispersion_ratio


@click.command("crossover")
@click.option("--alpha", default=0.84, show_default=True, help="Spiral wavenumber alpha = k z0.")
@click.option("--overlap", default=2.0, show_default=True, help="Effective resonance overlap S0.")
def crossover(alpha: float, overlap: float) -> None:
    """Print the provenance bias from the trapping-to-diffusion crossover weight."""
    ratio = crossover_dispersion_ratio(alpha, overlap)
    click.echo(f"crossover bias(alpha={alpha:.3f}, S0={overlap:.3f}): ratio={ratio:.4f}")
    click.echo(f"=> {100.0 * (1.0 - ratio):.1f}% colder (between the 7% trapping floor and 24% diffusion ceiling)")
