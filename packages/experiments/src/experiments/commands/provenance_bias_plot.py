"""``experiments provenance-bias-plot`` -- migrator coldness versus disc thickness."""

from __future__ import annotations

import click

from experiments.figures import figure_provenance_bias


@click.command("provenance-bias-plot")
@click.option("--n-alpha", default=16, show_default=True, help="Number of thickness samples.")
def provenance_bias_plot(n_alpha: int) -> None:
    """Plot the predicted migrator coldness versus disc thickness."""
    figure_provenance_bias(n_alpha=n_alpha)
