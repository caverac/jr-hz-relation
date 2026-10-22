"""``experiments nbody-plot`` -- draw the figures of the N-body test from its cached tables."""

from __future__ import annotations

from pathlib import Path

import click

from experiments._constants import NBODY_BASELINES, NBODY_THIN
from experiments.figures import make_nbody_figures
from experiments.migration import load_tables


@click.command("nbody-plot")
@click.argument("tables", nargs=-1, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--thin",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Tables of the razor-thin run for the exponent figure (default: the cached one, if present).",
)
def nbody_plot(tables: tuple[Path, ...], thin: Path | None) -> None:
    """Write the N-body figures (variance, exponents, rules, destination) into ``assets/figures``.

    TABLES are JSON files written by ``nbody-migration``, one per baseline; without them the
    three cached baselines under ``assets/data/nbody`` are used. The rules and destination
    figures show the longest baseline.
    """
    paths = list(tables) or [path for path in NBODY_BASELINES if path.exists()]
    if not paths:
        raise click.UsageError("no tables given and none cached under assets/data/nbody")
    thin_path = thin if thin is not None else (NBODY_THIN if NBODY_THIN.exists() else None)
    baselines = [load_tables(path) for path in paths]
    make_nbody_figures(baselines, load_tables(thin_path) if thin_path is not None else None)
