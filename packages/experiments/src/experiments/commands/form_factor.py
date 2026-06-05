"""``experiments form-factor`` -- print the vertical form factor F(E, alpha)."""

from __future__ import annotations

import click

from experiments.form_factor import vertical_form_factor


@click.command("form-factor")
@click.option("--energy", default=1.0, show_default=True, help="Vertical energy E.")
@click.option("--alpha", default=0.84, show_default=True, help="Spiral wavenumber alpha = k z0.")
def form_factor(energy: float, alpha: float) -> None:
    """Print the vertical form factor at a given energy and wavenumber."""
    value = vertical_form_factor(energy, alpha)
    click.echo(f"F(E={energy:.3f}, alpha={alpha:.3f}) = {value:.4f}")
