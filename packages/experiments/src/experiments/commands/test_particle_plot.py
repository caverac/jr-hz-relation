"""``experiments test-particle-plot`` -- plot the test-particle figure from the store."""

from __future__ import annotations

from pathlib import Path

import click

from experiments._constants import TEST_PARTICLE_STORE
from experiments.figures import figure_test_particle
from experiments.simulation import load_store


@click.command("test-particle-plot")
@click.option(
    "--store",
    default=str(TEST_PARTICLE_STORE),
    type=click.Path(exists=True),
    help="JSON store path.",
)
def test_particle_plot(store: str) -> None:
    """Plot the test-particle validation figure from the precomputed JSON store."""
    data = load_store(Path(store))
    series_a = [(p.x, p.bias_mean, p.bias_err) for p in data["series_a"]]
    series_b = [(p.x, p.bias_mean, p.bias_err) for p in data["series_b"]]
    figure_test_particle(series_a, series_b)
