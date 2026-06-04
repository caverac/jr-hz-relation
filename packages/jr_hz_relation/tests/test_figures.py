"""Tests for the publication figures."""

from pathlib import Path

from jr_hz_relation.figures import (
    figure_balescu_lenard,
    figure_crossover_bias,
    figure_finite_thickness,
    figure_form_factor,
    figure_form_factor_validation,
    figure_provenance_bias,
    figure_resonance_overlap,
    figure_trapped_weight,
    figure_trapping_cap,
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


def test_figure_resonance_overlap_writes_pdf(tmp_path: Path) -> None:
    """The resonance-overlap figure writes a non-empty PDF."""
    path = figure_resonance_overlap(tmp_path / "resonance-overlap.pdf", n_strength=8)
    assert path.exists() and path.stat().st_size > 0


def test_figure_trapped_weight_writes_pdf(tmp_path: Path) -> None:
    """The trapped-weight figure writes a non-empty PDF."""
    path = figure_trapped_weight(tmp_path / "trapped-weight.pdf", n_energy=8)
    assert path.exists() and path.stat().st_size > 0


def test_figure_trapping_cap_writes_pdf(tmp_path: Path) -> None:
    """The trapping-cap figure writes a non-empty PDF."""
    path = figure_trapping_cap(tmp_path / "trapping-cap.pdf", n_kappa=4, n_energy=8)
    assert path.exists() and path.stat().st_size > 0


def test_figure_crossover_bias_writes_pdf(tmp_path: Path) -> None:
    """The crossover-bias figure writes a non-empty PDF."""
    path = figure_crossover_bias(tmp_path / "crossover-bias.pdf", n_overlap=4, n_energy=8)
    assert path.exists() and path.stat().st_size > 0


def test_figure_finite_thickness_writes_pdf(tmp_path: Path) -> None:
    """The finite-thickness figure writes a non-empty PDF."""
    path = figure_finite_thickness(tmp_path / "finite-thickness.pdf", n_thickness=4)
    assert path.exists() and path.stat().st_size > 0


def test_figure_balescu_lenard_writes_pdf(tmp_path: Path) -> None:
    """The Balescu-Lenard figure writes a non-empty PDF."""
    path = figure_balescu_lenard(tmp_path / "balescu-lenard.pdf", n_b=4, n_energy=8)
    assert path.exists() and path.stat().st_size > 0


def test_make_all_figures_writes_the_set(tmp_path: Path) -> None:
    """The full set has all figures and they all exist on disk."""
    outdir = tmp_path / "figs"
    paths = make_all_figures(outdir)
    assert set(paths) == {
        "form-factor",
        "provenance-bias",
        "form-factor-validation",
        "resonance-overlap",
        "trapped-weight",
        "trapping-cap",
        "crossover-bias",
        "finite-thickness",
        "balescu-lenard",
    }
    assert all(path.exists() for path in paths.values())
