"""Tests for the click command-line interface."""

import json
from pathlib import Path

from click.testing import CliRunner, Result

from experiments.cli import main


def _run(*args: str) -> Result:
    """Invoke the CLI with the given arguments and return the result."""
    return CliRunner().invoke(main, list(args))


def test_help_lists_commands() -> None:
    """The group ``--help`` succeeds and lists a known command."""
    result = _run("--help")
    assert result.exit_code == 0
    assert "form-factor" in result.output


def test_form_factor_command() -> None:
    """The form-factor scalar command runs and returns success."""
    assert _run("form-factor", "--energy", "1.0", "--alpha", "0.84").exit_code == 0


def test_bias_command() -> None:
    """The bias scalar command runs and returns success."""
    assert _run("bias", "--alpha", "0.84", "--strength", "0.9").exit_code == 0


def test_slope_command() -> None:
    """The slope scalar command runs and returns success."""
    assert _run("slope", "--c-max", "1.0").exit_code == 0


def test_age_running_command() -> None:
    """The age-running scalar command runs and returns success."""
    assert _run("age-running", "--age", "8", "--ref", "1").exit_code == 0


def test_anchor_command() -> None:
    """The anchor scalar command runs and returns success."""
    assert _run("anchor", "--alpha", "0.84", "--target", "0.80").exit_code == 0


def test_trapping_command() -> None:
    """The trapping scalar command runs and returns success."""
    assert _run("trapping", "--alpha", "0.84", "--island-width", "1.0").exit_code == 0


def test_crossover_command() -> None:
    """The crossover scalar command runs and returns success."""
    assert _run("crossover", "--alpha", "0.84", "--overlap", "2.0").exit_code == 0


def test_diffusion_command() -> None:
    """The diffusion scalar command runs and returns success."""
    assert _run("diffusion", "--alpha", "0.84", "--broadening", "3.0").exit_code == 0


def test_thickness_command() -> None:
    """The thickness scalar command runs and returns success."""
    assert _run("thickness", "--alpha", "0.84", "--thickness", "0.5").exit_code == 0


def test_overlap_command() -> None:
    """The overlap scalar command runs and returns success."""
    assert _run("overlap", "--strength", "0.02", "--form-factor", "1.0").exit_code == 0


def _assert_figure_written(fig_dir: Path, stem: str) -> None:
    """Assert both the PNG and the PDF for *stem* exist under *fig_dir*."""
    assert (fig_dir / f"{stem}.png").exists()
    assert (fig_dir / f"{stem}.pdf").exists()


def test_form_factor_plot(assets_fig_dir: Path) -> None:
    """The form-factor-plot command writes its PNG and PDF."""
    result = _run("form-factor-plot", "--n-energies", "8")
    assert result.exit_code == 0
    _assert_figure_written(assets_fig_dir, "form-factor")


def test_provenance_bias_plot(assets_fig_dir: Path) -> None:
    """The provenance-bias-plot command writes its PNG and PDF."""
    result = _run("provenance-bias-plot", "--n-alpha", "5")
    assert result.exit_code == 0
    _assert_figure_written(assets_fig_dir, "provenance-bias")


def test_resonance_overlap_plot(assets_fig_dir: Path) -> None:
    """The resonance-overlap-plot command writes its PNG and PDF."""
    result = _run("resonance-overlap-plot", "--n-strength", "8")
    assert result.exit_code == 0
    _assert_figure_written(assets_fig_dir, "resonance-overlap")


def test_trapped_weight_plot(assets_fig_dir: Path) -> None:
    """The trapped-weight-plot command writes its PNG and PDF."""
    result = _run("trapped-weight-plot", "--n-energy", "8")
    assert result.exit_code == 0
    _assert_figure_written(assets_fig_dir, "trapped-weight")


def test_trapping_cap_plot(assets_fig_dir: Path) -> None:
    """The trapping-cap-plot command writes its PNG and PDF."""
    result = _run("trapping-cap-plot", "--n-kappa", "4", "--n-energy", "8")
    assert result.exit_code == 0
    _assert_figure_written(assets_fig_dir, "trapping-cap")


def test_crossover_bias_plot(assets_fig_dir: Path) -> None:
    """The crossover-bias-plot command writes its PNG and PDF."""
    result = _run("crossover-bias-plot", "--n-overlap", "4", "--n-energy", "8")
    assert result.exit_code == 0
    _assert_figure_written(assets_fig_dir, "crossover-bias")


def test_finite_thickness_plot(assets_fig_dir: Path) -> None:
    """The finite-thickness-plot command writes its PNG and PDF."""
    result = _run("finite-thickness-plot", "--n-thickness", "4")
    assert result.exit_code == 0
    _assert_figure_written(assets_fig_dir, "finite-thickness")


def test_balescu_lenard_plot(assets_fig_dir: Path) -> None:
    """The balescu-lenard-plot command writes its PNG and PDF."""
    result = _run("balescu-lenard-plot", "--n-b", "4", "--n-energy", "8")
    assert result.exit_code == 0
    _assert_figure_written(assets_fig_dir, "balescu-lenard")


def test_figures_writes_the_full_set(assets_fig_dir: Path) -> None:
    """The figures command writes every figure in the set as PNG and PDF."""
    result = _run("figures")
    assert result.exit_code == 0
    for stem in (
        "form-factor",
        "provenance-bias",
        "resonance-overlap",
        "trapped-weight",
        "trapping-cap",
        "crossover-bias",
        "finite-thickness",
        "balescu-lenard",
    ):
        _assert_figure_written(assets_fig_dir, stem)


def test_test_particle_simulate(tmp_path: Path) -> None:
    """The simulate command runs a tiny point and writes the JSON store."""
    store = tmp_path / "data.json"
    result = _run(
        "test-particle-simulate",
        "--store",
        str(store),
        "--alpha",
        "0.5",
        "--count",
        "1",
        "--n-part",
        "6",
        "--n-seed",
        "1",
    )
    assert result.exit_code == 0
    assert store.exists()


def test_test_particle_plot(assets_fig_dir: Path, tmp_path: Path) -> None:
    """The plot command reads a store and writes the figure."""
    store = tmp_path / "data.json"
    store.write_text(
        json.dumps(
            {
                "series_a": [{"x": 0.4, "bias_mean": 0.05, "bias_err": 0.01, "n_part": 10, "n_seed": 2}],
                "series_b": [{"x": 1.0, "bias_mean": 0.06, "bias_err": 0.01, "n_part": 10, "n_seed": 2}],
            }
        )
    )
    result = _run("test-particle-plot", "--store", str(store))
    assert result.exit_code == 0
    _assert_figure_written(assets_fig_dir, "test-particle-bias")
