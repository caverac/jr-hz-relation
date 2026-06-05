"""Tests for the shared plotting helpers and the ``@figure`` decorator."""

from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure

from experiments._plotting import configure_axes, figure, save_figure_set_if_changed


def _make_figure(value: float = 0.0) -> Figure:
    """Build a minimal one-axes figure plotting a flat line at *value*."""
    fig = Figure(figsize=(2.0, 2.0))
    axes = fig.add_subplot(1, 1, 1)
    axes.plot([0.0, 1.0], [value, value])
    return fig


class TestConfigureAxes:
    """Tests for :func:`configure_axes`."""

    def test_linear(self) -> None:
        """A default (linear) axes is styled without changing its scale."""
        fig = _make_figure()
        axes = fig.axes[0]
        configure_axes(axes)
        assert axes.get_xscale() == "linear"
        assert axes.get_yscale() == "linear"

    def test_log(self) -> None:
        """A log-scaled axes is styled without an AutoMinorLocator error."""
        fig = _make_figure()
        axes = fig.axes[0]
        axes.set_xscale("log")
        axes.set_yscale("log")
        configure_axes(axes)
        assert axes.get_xscale() == "log"
        assert axes.get_yscale() == "log"


class TestSaveFigureSetIfChanged:
    """Tests for :func:`save_figure_set_if_changed`."""

    def test_new_writes_both(self, tmp_path: Path) -> None:
        """A new figure writes both the PNG and the PDF and returns True."""
        png, pdf = tmp_path / "fig.png", tmp_path / "fig.pdf"
        assert save_figure_set_if_changed(_make_figure(), png, pdf) is True
        assert png.exists()
        assert pdf.exists()

    def test_unchanged_skips(self, tmp_path: Path) -> None:
        """An identical re-render returns False and rewrites nothing."""
        png, pdf = tmp_path / "fig.png", tmp_path / "fig.pdf"
        save_figure_set_if_changed(_make_figure(), png, pdf)
        assert save_figure_set_if_changed(_make_figure(), png, pdf) is False

    def test_changed_rewrites(self, tmp_path: Path) -> None:
        """A different figure returns True and rewrites the files."""
        png, pdf = tmp_path / "fig.png", tmp_path / "fig.pdf"
        save_figure_set_if_changed(_make_figure(0.0), png, pdf)
        assert save_figure_set_if_changed(_make_figure(1.0), png, pdf) is True

    def test_missing_pdf_rewrites(self, tmp_path: Path) -> None:
        """When the PDF is absent the set is rewritten even if the PNG matches."""
        png, pdf = tmp_path / "fig.png", tmp_path / "fig.pdf"
        save_figure_set_if_changed(_make_figure(), png, pdf)
        pdf.unlink()
        assert save_figure_set_if_changed(_make_figure(), png, pdf) is True
        assert pdf.exists()

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Missing parent directories are created automatically."""
        png, pdf = tmp_path / "sub" / "fig.png", tmp_path / "sub" / "fig.pdf"
        assert save_figure_set_if_changed(_make_figure(), png, pdf) is True
        assert png.exists()


class TestFigureDecorator:
    """Tests for the :func:`figure` decorator."""

    def test_saves_png_and_pdf(self, assets_fig_dir: Path) -> None:
        """The decorator saves both outputs and returns the figure."""

        @figure("decorated")
        def build() -> Figure:
            return _make_figure()

        result = build()
        assert isinstance(result, Figure)
        assert (assets_fig_dir / "decorated.png").exists()
        assert (assets_fig_dir / "decorated.pdf").exists()

    def test_unchanged_second_call(self, assets_fig_dir: Path) -> None:
        """A second identical call hits the 'unchanged' branch and reports it."""

        @figure("decorated")
        def build() -> Figure:
            return _make_figure()

        build()
        result = build()
        assert isinstance(result, Figure)
