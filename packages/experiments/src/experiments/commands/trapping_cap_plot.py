"""``experiments trapping-cap-plot`` -- single-resonance bias versus island width."""

from __future__ import annotations

import click

from experiments.figures import figure_trapping_cap


@click.command("trapping-cap-plot")
@click.option("--n-kappa", default=20, show_default=True, help="Number of island-width samples.")
@click.option("--n-energy", default=60, show_default=True, help="Number of vertical-energy quadrature points.")
def trapping_cap_plot(n_kappa: int, n_energy: int) -> None:
    """Plot the single-resonance bias versus island width, with the sqrt(F) cap."""
    figure_trapping_cap(n_kappa=n_kappa, n_energy=n_energy)
