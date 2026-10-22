"""``experiments nbody-arms`` -- measure the vertical profile of the spiral arms."""

from __future__ import annotations

from pathlib import Path

import click

from experiments.arms import ArmSetup, accumulate, profile_rows, profile_table
from experiments.spiral import ARM_HARMONICS
from experiments.tracks import disk_rows


@click.command("nbody-arms")
@click.argument("data", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--start", type=float, required=True, help="Snapshots with start < t enter (run time units).")
@click.option("--length", default=0.3, show_default=True, help="Snapshots up to start + length enter.")
@click.option("--every", default=5, show_default=True, help="Use every n-th snapshot of the window.")
def nbody_arms(data: Path, start: float, length: float, every: int) -> None:
    """Tabulate the amplitude and phase lag of the m = 5 to 8 arms of DATA in bins of |z|.

    Each row gives, for one ring of the instantaneous radius and one harmonic, the arm's
    relative amplitude and its lag behind the midplane arm per |z| bin, the amplitude of the
    whole ring, and the sech^2 scales of the arm and of the disk.
    """
    sums, numbers = accumulate(data, ArmSetup(start, length, every, disk_rows(data)), ARM_HARMONICS)
    for line in profile_table(profile_rows(sums), numbers):
        click.echo(line)
