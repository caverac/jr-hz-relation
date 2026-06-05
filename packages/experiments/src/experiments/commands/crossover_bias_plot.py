"""``experiments crossover-bias-plot`` -- bias across the overlap transition."""

from __future__ import annotations

import click

from experiments.figures import figure_crossover_bias


@click.command("crossover-bias-plot")
@click.option("--n-overlap", default=24, show_default=True, help="Number of overlap-strength samples.")
@click.option("--n-energy", default=120, show_default=True, help="Number of vertical-energy quadrature points.")
def crossover_bias_plot(n_overlap: int, n_energy: int) -> None:
    """Plot the provenance bias across the trapping-to-diffusion overlap transition."""
    figure_crossover_bias(n_overlap=n_overlap, n_energy=n_energy)
