"""``experiments test-particle-simulate`` -- run sims and accumulate the JSON store."""

from __future__ import annotations

from pathlib import Path

import click

from experiments.simulation import (
    DEFAULT_ALPHAS,
    DEFAULT_COUNTS,
    SimConfig,
    load_store,
    merge_point,
    save_store,
    simulate_series_a,
    simulate_series_b,
)

_DEFAULT_STORE = "assets/data/test-particle-data.json"


@click.command("test-particle-simulate")
@click.option("--store", default=_DEFAULT_STORE, type=click.Path(), help="JSON store path.")
@click.option("--alpha", "alphas", multiple=True, type=float, help="Series-A thinness value(s) to add.")
@click.option("--count", "counts", multiple=True, type=int, help="Series-B pattern count(s) to add.")
@click.option("--n-part", default=3000, show_default=True, help="Particles per realization.")
@click.option("--n-seed", default=8, show_default=True, help="Seed realizations averaged per point.")
def test_particle_simulate(
    store: str,
    alphas: tuple[float, ...],
    counts: tuple[int, ...],
    n_part: int,
    n_seed: int,
) -> None:
    """Run test-particle simulations and merge the results into the JSON store.

    With no ``--alpha``/``--count`` the default full set is computed; otherwise only
    the requested points are run and merged, leaving existing points untouched. The
    store is rewritten after every point, so interrupted runs keep their progress.
    The integration time and step count are fixed at their validated defaults
    (:class:`~experiments.simulation.SimConfig`).
    """
    config = SimConfig(n_part=n_part, n_seed=n_seed)
    store_path = Path(store)
    data = load_store(store_path)
    requested = bool(alphas or counts)
    targets_a = list(alphas) if requested else list(DEFAULT_ALPHAS)
    targets_b = list(counts) if requested else list(DEFAULT_COUNTS)
    for alpha in targets_a:
        point = simulate_series_a(float(alpha), config)
        data["series_a"] = merge_point(data["series_a"], point)
        save_store(data, store_path)
        click.echo(f"A: alpha={point.x:.3f} bias={point.bias_mean:.4f}+/-{point.bias_err:.4f}")
    for count in targets_b:
        point = simulate_series_b(int(count), config)
        data["series_b"] = merge_point(data["series_b"], point)
        save_store(data, store_path)
        click.echo(f"B: M={int(point.x)} bias={point.bias_mean:.4f}+/-{point.bias_err:.4f}")
    click.echo(f"stored -> {store_path}")
