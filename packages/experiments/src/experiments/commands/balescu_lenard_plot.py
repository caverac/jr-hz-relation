"""``experiments balescu-lenard-plot`` -- diffusive bias versus broadening parameter."""

from __future__ import annotations

import click

from experiments.figures import figure_balescu_lenard


@click.command("balescu-lenard-plot")
@click.option("--n-b", default=24, show_default=True, help="Number of broadening-parameter samples.")
@click.option("--n-energy", default=120, show_default=True, help="Number of vertical-energy quadrature points.")
def balescu_lenard_plot(n_b: int, n_energy: int) -> None:
    """Plot the diffusive provenance bias versus the resonance-broadening parameter."""
    figure_balescu_lenard(n_b=n_b, n_energy=n_energy)
