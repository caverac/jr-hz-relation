"""``experiments figures`` -- generate the full figure set into ``assets/figures``."""

from __future__ import annotations

import click

from experiments._constants import NBODY_BASELINES, NBODY_THIN, TEST_PARTICLE_STORE
from experiments.commands.test_particle_plot import cached_nbody_points
from experiments.figures import make_all_figures, make_nbody_figures
from experiments.migration import load_tables
from experiments.simulation import load_store


@click.command("figures")
def figures() -> None:
    """Generate the full figure set (PNG + PDF) into ``assets/figures``.

    The test-particle figure is plotted from the cached store
    (``assets/data/test-particle-data.json``); run ``test-particle-simulate`` first to
    (re)compute that data. The N-body figures are plotted from the cached tables under
    ``assets/data/nbody`` when they exist, and the same tables add the N-body points to
    the test-particle figure; ``nbody-migration`` writes them.
    """
    store = load_store(TEST_PARTICLE_STORE)
    series_a = [(p.x, p.bias_mean, p.bias_err) for p in store["series_a"]]
    series_b = [(p.x, p.bias_mean, p.bias_err) for p in store["series_b"]]
    make_all_figures(series_a, series_b, cached_nbody_points())
    nbody = [load_tables(path) for path in NBODY_BASELINES if path.exists()]
    if nbody:
        make_nbody_figures(nbody, load_tables(NBODY_THIN) if NBODY_THIN.exists() else None)
    else:
        click.echo("  no cached N-body tables under assets/data/nbody; skipped the nbody-* figures")
