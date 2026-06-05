"""Shared matplotlib style and the :func:`figure` decorator.

A figure-building function returns a :class:`~matplotlib.figure.Figure`; the
:func:`figure` decorator applies the shared house style, then writes the figure to
``assets/figures`` as **both** a ``.png`` (for the documentation site) and a
``.pdf`` (for the paper). The render is compared pixel-for-pixel against the
existing ``.png``; the files are rewritten only when the content actually changed,
so regenerating an unchanged figure produces no spurious diff.
"""

from __future__ import annotations

import functools
import io
from pathlib import Path
from typing import Any, Callable, TypeVar

import click
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator

from experiments._constants import ASSETS_FIG_DIR

# Shared serif/STIX figure style, matching the phspectra benchmark figures.
matplotlib.rcParams["font.family"] = "serif"
matplotlib.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif"]
matplotlib.rcParams["mathtext.fontset"] = "stix"

FigureFunc = TypeVar("FigureFunc", bound=Callable[..., Figure])

#: Defaults forwarded to ``fig.savefig`` for both the PNG and the PDF.
SAVEFIG_DEFAULTS: dict[str, Any] = {
    "dpi": 300,
    "bbox_inches": "tight",
    "facecolor": "white",
    "edgecolor": "none",
}


def configure_axes(axes: Axes) -> None:
    """Apply the shared tick style to *axes*.

    Draws inward major (length 6) and minor (length 3, gray) ticks on all four
    sides, adding an :class:`~matplotlib.ticker.AutoMinorLocator` on linear axes
    only (matplotlib places minor ticks on log axes automatically).

    Parameters
    ----------
    axes : Axes
        The axes to style.
    """
    if axes.get_xscale() == "linear":
        axes.xaxis.set_minor_locator(AutoMinorLocator())
    if axes.get_yscale() == "linear":
        axes.yaxis.set_minor_locator(AutoMinorLocator())
    axes.tick_params(which="minor", length=3, color="gray", direction="in")
    axes.tick_params(which="major", length=6, direction="in")
    axes.tick_params(top=True, right=True, which="both")


def _apply_house_style(fig: Figure) -> None:
    """Style every axes of *fig* and make any legends frameless.

    Parameters
    ----------
    fig : Figure
        The figure to finalise before saving.
    """
    for axes in fig.axes:
        configure_axes(axes)
        legend = axes.get_legend()
        if legend is not None:
            legend.set_frame_on(False)


def save_figure_set_if_changed(
    fig: Figure,
    png_path: Path,
    pdf_path: Path,
    **savefig_kwargs: Any,
) -> bool:
    """Write *fig* as a PNG and a PDF, but only if its content changed.

    The figure is rendered once to an in-memory PNG and compared pixel-for-pixel
    against ``png_path``. When the new render matches the existing PNG (and the PDF
    is also present) nothing is written; otherwise both files are (re)written, with
    the PNG reusing the render that was just compared.

    Parameters
    ----------
    fig : Figure
        Matplotlib figure to save.
    png_path : Path
        Output path for the documentation PNG.
    pdf_path : Path
        Output path for the paper PDF.
    **savefig_kwargs : Any
        Arguments forwarded to ``fig.savefig`` (e.g. *dpi*, *bbox_inches*).

    Returns
    -------
    bool
        ``True`` if the files were written, ``False`` if skipped (unchanged).
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", **savefig_kwargs)
    buf.seek(0)
    new_img = plt.imread(buf)

    if png_path.exists() and pdf_path.exists():
        existing_img = plt.imread(png_path)
        if new_img.shape == existing_img.shape and bool(np.array_equal(new_img, existing_img)):
            return False

    png_path.parent.mkdir(parents=True, exist_ok=True)
    png_path.write_bytes(buf.getvalue())
    fig.savefig(pdf_path, format="pdf", **savefig_kwargs)
    return True


def figure(name: str, **extra_kwargs: Any) -> Callable[[FigureFunc], FigureFunc]:
    """Save the returned :class:`Figure` to ``assets/figures`` if it changed.

    The decorated function must return a :class:`~matplotlib.figure.Figure`. The
    decorator applies the house style, writes ``<name>.png`` and ``<name>.pdf`` (via
    :func:`save_figure_set_if_changed`), reports the outcome, and closes the figure.

    Parameters
    ----------
    name : str
        Figure stem, e.g. ``"form-factor"`` (without extension).
    **extra_kwargs : Any
        Extra arguments forwarded to ``fig.savefig``, merged over
        :data:`SAVEFIG_DEFAULTS`.

    Returns
    -------
    Callable[[FigureFunc], FigureFunc]
        The decorator.
    """
    savefig_kwargs = {**SAVEFIG_DEFAULTS, **extra_kwargs}

    def decorator(func: FigureFunc) -> FigureFunc:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Figure:
            fig = func(*args, **kwargs)
            _apply_house_style(fig)
            png_path = ASSETS_FIG_DIR / f"{name}.png"
            pdf_path = ASSETS_FIG_DIR / f"{name}.pdf"
            if save_figure_set_if_changed(fig, png_path, pdf_path, **savefig_kwargs):
                click.echo(f"  saved {png_path} and {pdf_path}")
            else:
                click.echo(f"  unchanged {name}")
            plt.close(fig)
            return fig

        return wrapper  # type: ignore[return-value]

    return decorator
