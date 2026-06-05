"""``experiments trapped-weight-plot`` -- the exact trapped weight versus action."""

from __future__ import annotations

import click

from experiments.figures import figure_trapped_weight


@click.command("trapped-weight-plot")
@click.option("--n-energy", default=60, show_default=True, help="Number of vertical-energy samples.")
def trapped_weight_plot(n_energy: int) -> None:
    """Plot the exact trapped weight versus vertical action for several island widths."""
    figure_trapped_weight(n_energy=n_energy)
