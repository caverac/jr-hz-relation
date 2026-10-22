"""``experiments nbody-spiral`` -- measure the spiral patterns of an extracted run."""

from __future__ import annotations

from pathlib import Path

import click

from experiments.spiral import load_rings, measure_window, model_rotation_curve, parse_windows, report, save_modes


@click.command("nbody-spiral")
@click.argument("data", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--windows", default="", help="Time windows as start:end,start:end (default: the whole run).")
@click.option("--min-amplitude", default=0.02, show_default=True, help="Report harmonics whose a_m exceeds this.")
@click.option("--output", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Save the modes (npz).")
def nbody_spiral(data: Path, windows: str, min_amplitude: float, output: Path | None) -> None:
    """Print the amplitudes, wavenumbers, strengths and pattern speeds of the spiral in DATA.

    DATA is an extraction directory holding ``rings/``. The report starts with the model
    circular speed against the Jeans estimate from the ring sums, then gives per window the
    density amplitude of every harmonic, and for every harmonic above ``--min-amplitude`` its
    wavenumber, pitch angle and strength at the report radii and its spectrogram peaks with
    their resonance radii; it ends with the combined wavenumber of m = 5 to 8 per ring and
    window, the input of ``nbody-migration``.
    """
    rings = load_rings(data / "rings")
    curve = model_rotation_curve()
    modes = [measure_window(rings, curve, bounds) for bounds in parse_windows(windows, rings.times)]
    for line in report(rings, curve, modes, min_amplitude):
        click.echo(line)
    if output is not None:
        save_modes(output, rings, curve, modes)
        click.echo(f"saved {output}")
