"""``experiments nbody-migration`` -- test the form-factor prediction between two windows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click

from experiments.migration import (
    F_BINS,
    QUANTILE,
    RINGS_SPEC,
    load_particles,
    load_spiral,
    make_ring,
    parse_rings,
    report,
    run,
    save_tables,
    wavenumber_sweep,
)


@dataclass(frozen=True)
class MigrationOptions:
    """The options of the command that do not name a file."""

    spiral_window: int
    harmonics: str
    form: str
    k_sweep: bool
    output: Path | None


@click.command("nbody-migration")
@click.argument("origin", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("later", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("spiral", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--spiral-window", default=0, show_default=True, help="Index of the spiral window whose k is used.")
@click.option("--harmonics", default="5:9", show_default=True, help="0 the strongest, m one, a:b the range to b - 1.")
@click.option("--form", type=click.Choice(("thin", "layer")), default="layer", show_default=True, help="Form factor.")
@click.option("--k-sweep", is_flag=True, help="Also tabulate the exponent against F_k for every k of the grid.")
@click.option("--output", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Save the tables (json).")
def nbody_migration(origin: Path, later: Path, spiral: Path, **options: Any) -> None:
    """Compare the orbits of ORIGIN with those of LATER using the wavenumbers of SPIRAL.

    ORIGIN and LATER are window summaries of ``nbody-window`` and SPIRAL the modes saved by
    ``nbody-spiral``. The tables are the core test (variance of dLz against F per origin
    ring), the bias per selection rule, the inward against outward comparison at the origin
    and the arrivals against the locals at the destination. The rings are 3 to 12 kpc in
    steps of 1, with 8 quantile bins of F and the migrator threshold at the 90th percentile.
    """
    settings = MigrationOptions(**options)
    modes = load_spiral(spiral, settings.spiral_window, settings.harmonics)
    particles = load_particles(origin, later, modes, "form" if settings.form == "thin" else "form_layer")
    bounds = parse_rings(RINGS_SPEC)
    rings = [make_ring(particles, modes, b, QUANTILE) for b in bounds]
    chosen = ", ".join(str(m) for m in modes.harmonics)
    click.echo(f"{len(particles.origin.lz)} disk particles, {settings.form} form factor,", nl=False)
    click.echo(f" wavenumber of m = {chosen} from spiral window {settings.spiral_window}")
    tables = run(particles, rings, bounds, F_BINS)
    tables["meta"]["form"] = settings.form
    tables["meta"]["harmonics"] = modes.harmonics
    tables["meta"]["spiral_window"] = settings.spiral_window
    if settings.k_sweep:
        tables["sweep"] = wavenumber_sweep(particles, rings, F_BINS)
    for line in report(tables):
        click.echo(line)
    if settings.output is not None:
        save_tables(settings.output, tables)
        click.echo(f"saved {settings.output}")
