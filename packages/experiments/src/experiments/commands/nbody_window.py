"""``experiments nbody-window`` -- summarize the tracked orbits over one time window."""

from __future__ import annotations

import time
from pathlib import Path

import click

from experiments.tracks import disk_rows
from experiments.windows import ARM_SCALE, K_GRID_SPEC, load_window, parse_grid, report, save_summary, summarize


@click.command("nbody-window")
@click.argument("data", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--start", type=float, required=True, help="Start of the window (run time units).")
@click.option("--length", default=0.3, show_default=True, help="Length of the window (run time units).")
@click.option("--k-grid", "k_grid", default=K_GRID_SPEC, show_default=True, help="Wavenumbers of F, start:stop:step.")
@click.option("--arm-scale", default=ARM_SCALE, show_default=True, help="sech^2 scale of the arms (kpc).")
def nbody_window(data: Path, start: float, length: float, k_grid: str, arm_scale: float) -> None:
    """Summarize every tracked particle of DATA over the window starting at ``--start``.

    The summary (window means, loop-integral actions and periods, and the razor-thin and
    layer form factors on the wavenumber grid) is written to
    ``DATA/analysis/windows/t_START.npz``, the input of ``nbody-migration``.
    """
    started = time.perf_counter()
    grid = parse_grid(k_grid)
    window = load_window(data, start, length)
    summary = summarize(window, grid, arm_scale)
    rows = disk_rows(data)
    output = data / "analysis" / "windows" / f"t_{start:.3f}.npz"
    save_summary(output, window, summary, grid, rows)
    for line in report(window, summary, rows):
        click.echo(line)
    click.echo(f"saved {output} in {time.perf_counter() - started:.1f} s")
