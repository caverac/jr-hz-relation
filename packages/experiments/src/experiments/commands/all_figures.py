"""``experiments figures`` -- generate the full figure set into ``assets/figures``."""

from __future__ import annotations

import click

from experiments._constants import TEST_PARTICLE_STORE
from experiments.figures import make_all_figures
from experiments.simulation import load_store


@click.command("figures")
def figures() -> None:
    """Generate the full figure set (PNG + PDF) into ``assets/figures``.

    The test-particle figure is plotted from the cached store
    (``assets/data/test-particle-data.json``); run ``test-particle-simulate`` first to
    (re)compute that data.
    """
    store = load_store(TEST_PARTICLE_STORE)
    series_a = [(p.x, p.bias_mean, p.bias_err) for p in store["series_a"]]
    series_b = [(p.x, p.bias_mean, p.bias_err) for p in store["series_b"]]
    make_all_figures(series_a, series_b)
