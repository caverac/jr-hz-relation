"""``experiments figures`` -- generate the full figure set into ``assets/figures``."""

from __future__ import annotations

import click

from experiments.figures import make_all_figures


@click.command("figures")
def figures() -> None:
    """Generate the full figure set (PNG + PDF) into ``assets/figures``."""
    make_all_figures()
