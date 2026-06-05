"""``experiments overlap`` -- the Milky Way bar-spiral Chirikov overlap parameter."""

from __future__ import annotations

import click

from experiments.overlap import milky_way_overlap


@click.command("overlap")
@click.option("--strength", default=0.02, show_default=True, help="Fractional spiral strength epsilon.")
@click.option("--form-factor", "form_factor", default=1.0, show_default=True, help="Vertical form factor F.")
def overlap(strength: float, form_factor: float) -> None:
    """Print the Milky Way bar-spiral Chirikov overlap parameter."""
    value = milky_way_overlap(strength, form_factor=form_factor)
    regime = "overlap (diffusive)" if value >= 1.0 else "regular (trapping)"
    click.echo(f"S(eps={strength:.3f}, F={form_factor:.2f}) = {value:.3f} -> {regime}")
