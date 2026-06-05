"""``experiments resonance-overlap-plot`` -- bar-spiral Chirikov overlap versus strength."""

from __future__ import annotations

import click

from experiments.figures import figure_resonance_overlap


@click.command("resonance-overlap-plot")
@click.option("--n-strength", default=60, show_default=True, help="Number of spiral-strength samples.")
def resonance_overlap_plot(n_strength: int) -> None:
    """Plot the bar-spiral Chirikov overlap parameter versus spiral strength."""
    figure_resonance_overlap(n_strength=n_strength)
