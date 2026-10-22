"""``experiments nbody-floor`` -- compare the dLz of a run with those of its control."""

from __future__ import annotations

from pathlib import Path

import click

from experiments.floor import load_run, parse_rings, ring_row
from experiments.migration import format_table
from experiments.tracks import disk_rows


@click.command("nbody-floor")
@click.argument("control", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("run", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--times", default="0.5,0.8", show_default=True, help="The two times, comma separated (run units).")
@click.option("--rings", default="3:12:1", show_default=True, help="Rings of the radius at the first time.")
@click.option("--z-bins", "z_bins", default=6, show_default=True, help="Quantile bins of |z| per ring.")
def nbody_floor(control: Path, run: Path, times: str, rings: str, z_bins: int) -> None:
    """Tabulate the variance of dLz in CONTROL against RUN between two times, per ring.

    Both directories are extractions whose tracks hold the same particles row by row. The
    control's variance is the floor of the run's: what the disk does to itself without the
    perturbers, plus the numerical noise.
    """
    first, second = (float(x) for x in times.split(","))
    rows = disk_rows(run)
    control_run = load_run(control, (first, second), rows)
    perturbed = load_run(run, (first, second), rows)
    click.echo(f"{control}: t = {control_run.first.time:.4f}; {run}: t = {perturbed.first.time:.4f}")
    table = [ring_row(control_run, perturbed, bounds, z_bins) for bounds in parse_rings(rings)]
    for line in format_table("Variance of dLz, control against run", table):
        click.echo(line)
