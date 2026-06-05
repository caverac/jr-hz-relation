"""``experiments finite-thickness-plot`` -- single-resonance bias versus spiral thickness."""

from __future__ import annotations

import click

from experiments.figures import figure_finite_thickness


@click.command("finite-thickness-plot")
@click.option("--n-thickness", default=20, show_default=True, help="Number of spiral-thickness samples.")
def finite_thickness_plot(n_thickness: int) -> None:
    """Plot the single-resonance bias versus spiral thickness with the finite-thickness F."""
    figure_finite_thickness(n_thickness=n_thickness)
