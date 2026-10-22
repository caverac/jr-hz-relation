"""Click CLI group for the ``experiments`` analysis package.

Each subcommand lives in its own module under :mod:`experiments.commands`. Scalar
diagnostics print a single number; the ``*-plot`` commands each write one figure
(PNG + PDF) into ``assets/figures`` (with per-figure options), and ``figures``
writes the whole set. The ``nbody-*`` commands run the test of the model in a
self-consistent N-body disk, from the GADGET snapshots to the cached tables that
``nbody-plot`` draws::

    experiments form-factor --energy 1.0 --alpha 0.84
    experiments form-factor-plot --n-energies 60
    experiments figures
    experiments nbody-extract /path/to/simulations/run staging/run --snapshots 0:511:5,512:1020
    experiments nbody-spiral staging/run --windows 0.5:0.8 --output modes.npz
    experiments nbody-window staging/run --start 0.5
    experiments nbody-migration t_0.500.npz t_1.500.npz modes.npz --output tables.json
    experiments nbody-plot tables.json
"""

from __future__ import annotations

import click

from experiments.commands.age_running import age_running
from experiments.commands.all_figures import figures
from experiments.commands.anchor import anchor
from experiments.commands.balescu_lenard_plot import balescu_lenard_plot
from experiments.commands.bias import bias
from experiments.commands.crossover import crossover
from experiments.commands.crossover_bias_plot import crossover_bias_plot
from experiments.commands.diffusion import diffusion
from experiments.commands.finite_thickness_plot import finite_thickness_plot
from experiments.commands.form_factor import form_factor
from experiments.commands.form_factor_plot import form_factor_plot
from experiments.commands.nbody_arms import nbody_arms
from experiments.commands.nbody_extract import nbody_extract
from experiments.commands.nbody_floor import nbody_floor
from experiments.commands.nbody_migration import nbody_migration
from experiments.commands.nbody_plot import nbody_plot
from experiments.commands.nbody_spiral import nbody_spiral
from experiments.commands.nbody_window import nbody_window
from experiments.commands.overlap import overlap
from experiments.commands.provenance_bias_plot import provenance_bias_plot
from experiments.commands.resonance_overlap_plot import resonance_overlap_plot
from experiments.commands.slope import slope
from experiments.commands.test_particle_plot import test_particle_plot
from experiments.commands.test_particle_simulate import test_particle_simulate
from experiments.commands.thickness import thickness
from experiments.commands.trapped_weight_plot import trapped_weight_plot
from experiments.commands.trapping import trapping
from experiments.commands.trapping_cap_plot import trapping_cap_plot


@click.group()
def main() -> None:
    """Analysis CLI for the analytic provenance-bias / spiral J_R-h_Z paper."""


main.add_command(form_factor)
main.add_command(bias)
main.add_command(slope)
main.add_command(age_running)
main.add_command(anchor)
main.add_command(trapping)
main.add_command(crossover)
main.add_command(diffusion)
main.add_command(thickness)
main.add_command(overlap)
main.add_command(form_factor_plot)
main.add_command(provenance_bias_plot)
main.add_command(resonance_overlap_plot)
main.add_command(trapped_weight_plot)
main.add_command(trapping_cap_plot)
main.add_command(crossover_bias_plot)
main.add_command(finite_thickness_plot)
main.add_command(balescu_lenard_plot)
main.add_command(test_particle_simulate)
main.add_command(test_particle_plot)
main.add_command(nbody_extract)
main.add_command(nbody_spiral)
main.add_command(nbody_window)
main.add_command(nbody_migration)
main.add_command(nbody_floor)
main.add_command(nbody_arms)
main.add_command(nbody_plot)
main.add_command(figures)
