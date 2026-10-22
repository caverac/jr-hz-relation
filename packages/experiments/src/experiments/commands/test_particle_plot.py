"""``experiments test-particle-plot`` -- plot the test-particle figure from the store."""

from __future__ import annotations

from pathlib import Path

import click

from experiments._constants import NBODY_BASELINES, TEST_PARTICLE_STORE
from experiments.figures import NbodyPoints, figure_test_particle
from experiments.migration import bias_points, load_tables
from experiments.simulation import load_store


def cached_nbody_points() -> list[NbodyPoints]:
    """Return the |dLz|-weighted bias per origin ring of every cached N-body baseline, labeled by model and baseline."""
    points = []
    for path in NBODY_BASELINES:
        if path.exists():
            tables = load_tables(path)
            label = rf"$\mathtt{{LD}}$ {tables['meta']['baseline_gyr']:.2f} Gyr"
            points.append((label, bias_points(tables)))
    return points


@click.command("test-particle-plot")
@click.option(
    "--store",
    default=str(TEST_PARTICLE_STORE),
    type=click.Path(exists=True),
    help="JSON store path.",
)
def test_particle_plot(store: str) -> None:
    """Plot the test-particle validation figure from the precomputed JSON store.

    The cached tables of the N-body test, when present under ``assets/data/nbody``,
    add the measured bias of its origin rings to the single-transient panel.
    """
    data = load_store(Path(store))
    series_a = [(p.x, p.bias_mean, p.bias_err) for p in data["series_a"]]
    series_b = [(p.x, p.bias_mean, p.bias_err) for p in data["series_b"]]
    figure_test_particle(series_a, series_b, cached_nbody_points())
