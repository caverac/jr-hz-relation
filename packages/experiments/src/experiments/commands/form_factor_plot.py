"""``experiments form-factor-plot`` -- the vertical form factor figure."""

from __future__ import annotations

import click

from experiments.figures import figure_form_factor


@click.command("form-factor-plot")
@click.option("--n-energies", default=60, show_default=True, help="Number of vertical-energy samples.")
def form_factor_plot(n_energies: int) -> None:
    """Plot the vertical form factor versus vertical action for several wavenumbers."""
    figure_form_factor(n_energies=n_energies)
