"""``experiments nbody-extract`` -- extract tracks and ring sums from a GADGET run."""

from __future__ import annotations

from pathlib import Path

import click

from experiments.tracks import Extraction, extract_run, parse_snapshots


@click.command("nbody-extract")
@click.argument("run", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("output", type=click.Path(file_okay=False, path_type=Path))
@click.option("--snapshots", default="0:511:5,512:1020", show_default=True, help="Snapshot numbers as Python ranges.")
@click.option("--sample", default=1_000_000, show_default=True, help="Number of disk particles to track.")
@click.option("--seed", default=1, show_default=True, help="Seed of the disk sample.")
def nbody_extract(run: Path, output: Path, snapshots: str, sample: int, seed: int) -> None:
    """Extract the tracks and the ring sums of the requested snapshots of RUN into OUTPUT.

    RUN holds the ``snap_NNN`` files of a GADGET format 1 run; OUTPUT receives ``tracks/``,
    ``rings/`` and ``meta/``. Snapshots whose two products exist are skipped, so a stopped
    extraction resumes where it stopped; a snapshot that cannot be read is reported and
    skipped. The snapshot list uses Python range syntax, so ``0:511:5`` is 0, 5, ..., 510.
    """
    for line in extract_run(Extraction(run, output, sample, seed), parse_snapshots(snapshots)):
        click.echo(line)
