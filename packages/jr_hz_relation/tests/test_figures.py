"""Tests for the publication figures."""

from pathlib import Path

from jr_hz_relation.figures import (
    figure_form_factor,
    figure_form_factor_validation,
    figure_provenance_bias,
    make_all_figures,
)


def test_figure_form_factor_writes_pdf(tmp_path: Path) -> None:
    """The form-factor figure writes a non-empty PDF."""
    path = figure_form_factor(tmp_path / "form-factor.pdf", n_energies=8)
    assert path.exists() and path.stat().st_size > 0


def test_figure_provenance_bias_writes_pdf(tmp_path: Path) -> None:
    """The provenance-bias figure writes a non-empty PDF."""
    path = figure_provenance_bias(tmp_path / "provenance-bias.pdf", n_alpha=5)
    assert path.exists() and path.stat().st_size > 0


def test_figure_form_factor_validation_writes_pdf(tmp_path: Path) -> None:
    """The galpy validation figure writes a non-empty PDF."""
    path = figure_form_factor_validation(
        tmp_path / "form-factor-validation.pdf", n_curve=8, n_markers=3, n_periods=8, samples_per_period=150
    )
    assert path.exists() and path.stat().st_size > 0


def test_make_all_figures_writes_the_set(tmp_path: Path) -> None:
    """The full set has all figures and they all exist on disk."""
    outdir = tmp_path / "figs"
    paths = make_all_figures(outdir)
    assert set(paths) == {"form-factor", "provenance-bias", "form-factor-validation"}
    assert all(path.exists() for path in paths.values())
