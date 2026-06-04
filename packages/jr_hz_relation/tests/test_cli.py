"""Tests for the command-line interface."""

from pathlib import Path

from jr_hz_relation.cli import build_parser, main


def test_build_parser_returns_parser() -> None:
    """The parser is constructed with a command destination."""
    parser = build_parser()
    assert parser.prog == "jr-hz-relation"


def test_form_factor_command() -> None:
    """The form-factor subcommand runs and returns success."""
    assert main(["form-factor", "--energy", "1.0", "--alpha", "0.84"]) == 0


def test_bias_command() -> None:
    """The bias subcommand runs and returns success."""
    assert main(["bias", "--alpha", "0.84", "--strength", "0.9"]) == 0


def test_slope_command() -> None:
    """The slope subcommand runs and returns success."""
    assert main(["slope", "--c-max", "1.0"]) == 0


def test_age_running_command() -> None:
    """The age-running subcommand runs and returns success."""
    assert main(["age-running", "--age", "8", "--ref", "1"]) == 0


def test_anchor_command() -> None:
    """The anchor subcommand runs and returns success."""
    assert main(["anchor", "--alpha", "0.84", "--target", "0.80"]) == 0


def test_trapping_command() -> None:
    """The trapping subcommand runs and returns success."""
    assert main(["trapping", "--alpha", "0.84", "--island-width", "1.0"]) == 0


def test_crossover_command() -> None:
    """The crossover subcommand runs and returns success."""
    assert main(["crossover", "--alpha", "0.84", "--overlap", "2.0"]) == 0


def test_thickness_command() -> None:
    """The thickness subcommand runs and returns success."""
    assert main(["thickness", "--alpha", "0.84", "--thickness", "0.5"]) == 0


def test_diffusion_command() -> None:
    """The diffusion subcommand runs and returns success."""
    assert main(["diffusion", "--alpha", "0.84", "--broadening", "3.0"]) == 0


def test_overlap_command() -> None:
    """The overlap subcommand runs and returns success."""
    assert main(["overlap", "--strength", "0.02", "--form-factor", "1.0"]) == 0


def test_figures_command(tmp_path: Path) -> None:
    """The figures subcommand writes the figure set and returns success."""
    assert main(["figures", "--outdir", str(tmp_path)]) == 0
    assert (tmp_path / "form-factor.pdf").exists()


def test_no_command_prints_help() -> None:
    """Invoking with no subcommand prints help and returns a non-zero code."""
    assert main([]) == 1
