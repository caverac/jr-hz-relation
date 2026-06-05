"""Click CLI group for the ``experiments`` analysis package.

Each subcommand lives in its own module under :mod:`experiments.commands`. Scalar
diagnostics print a single number; the ``*-plot`` commands each write one figure
(PNG + PDF) into ``assets/figures`` (with per-figure options), and ``figures``
writes the whole set::

    experiments form-factor --energy 1.0 --alpha 0.84
    experiments form-factor-plot --n-energies 60
    experiments figures
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
main.add_command(figures)
