"""Tests for the ``nbody-*`` commands and the figures they draw."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner
from conftest import invoke

from experiments.cli import main
from experiments.figures import make_nbody_figures
from experiments.migration import load_tables


def _assert_figure_written(fig_dir: Path, stem: str) -> None:
    """Assert both the PNG and the PDF for *stem* exist under *fig_dir*."""
    assert (fig_dir / f"{stem}.png").exists()
    assert (fig_dir / f"{stem}.pdf").exists()


def test_spiral_report(extracted: Path) -> None:
    """The spiral command reports the rotation check, the amplitudes and the combined wavenumbers."""
    output = invoke("nbody-spiral", str(extracted), "--windows", "0:0.12", "--min-amplitude", "3")
    assert "Circular speed: model against the Jeans estimate" in output
    assert "density amplitude a_m (percent)" in output
    assert "Combined wavenumber of m = 5, 6, 7, 8" in output
    assert "spectrogram peaks" not in output


def test_migration_variants(window_files: tuple[Path, Path], spiral_file: Path) -> None:
    """The migration command accepts the thin form factor, a single harmonic, the strongest one and the sweep."""
    origin, later = (str(path) for path in window_files)
    output = invoke("nbody-migration", origin, later, str(spiral_file), "--form", "thin", "--harmonics", "7")
    assert "thin form factor, wavenumber of m = 7" in output
    output = invoke("nbody-migration", origin, later, str(spiral_file), "--harmonics", "0", "--k-sweep")
    assert "wavenumber of m = 5 from spiral window 0" in output
    assert "The product b_k k" in output


def test_floor_command(extracted: Path, control_extracted: Path) -> None:
    """The floor command tabulates the two variances per ring."""
    output = invoke("nbody-floor", str(control_extracted), str(extracted), "--times", "0,0.2", "--rings", "4:6:1")
    assert "Variance of dLz, control against run" in output
    assert "| 4 to 5 |" in output and "| 5 to 6 |" in output


def test_arms_command(extracted: Path) -> None:
    """The arms command tabulates the profile of every ring and harmonic."""
    output = invoke("nbody-arms", str(extracted), "--start", "0", "--length", "0.12", "--every", "3")
    assert "Projected arm amplitude" in output
    assert "| 11 to 12 | 8 |" in output


def test_plot_command(assets_fig_dir: Path, tables_file: Path) -> None:
    """The plot command writes the four figures from given tables, with and without the thin run."""
    invoke("nbody-plot", str(tables_file), str(tables_file), "--thin", str(tables_file))
    for stem in ("nbody-variance", "nbody-exponents", "nbody-rules", "nbody-destination"):
        _assert_figure_written(assets_fig_dir, stem)


def test_plot_command_defaults(assets_fig_dir: Path, tables_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Without arguments the cached baselines are used, and their absence is an error."""
    monkeypatch.setattr("experiments.commands.nbody_plot.NBODY_BASELINES", (tables_file,))
    monkeypatch.setattr("experiments.commands.nbody_plot.NBODY_THIN", tables_file.parent / "missing.json")
    invoke("nbody-plot")
    _assert_figure_written(assets_fig_dir, "nbody-exponents")
    monkeypatch.setattr("experiments.commands.nbody_plot.NBODY_BASELINES", (tables_file.parent / "missing.json",))
    result = CliRunner().invoke(main, ["nbody-plot"])
    assert result.exit_code != 0
    assert "no tables given" in result.output


def test_figures_with_and_without_cached_tables(tables_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The figures command draws the N-body figures only when the cached tables exist."""
    calls: list[tuple[int, bool]] = []
    monkeypatch.setattr("experiments.commands.all_figures.make_all_figures", lambda *_: {})
    monkeypatch.setattr(
        "experiments.commands.all_figures.make_nbody_figures",
        lambda baselines, thin: calls.append((len(baselines), thin is not None)),
    )
    monkeypatch.setattr("experiments.commands.all_figures.NBODY_BASELINES", (tables_file, tables_file))
    monkeypatch.setattr("experiments.commands.all_figures.NBODY_THIN", tables_file)
    invoke("figures")
    assert calls == [(2, True)]
    missing = tables_file.parent / "missing.json"
    monkeypatch.setattr("experiments.commands.all_figures.NBODY_BASELINES", (missing,))
    monkeypatch.setattr("experiments.commands.all_figures.NBODY_THIN", missing)
    assert "skipped the nbody-* figures" in invoke("figures")
    assert calls == [(2, True)]


def test_test_particle_plot_without_cache(
    assets_fig_dir: Path, tables_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The test-particle figure is drawn with and without cached N-body points."""
    store = tables_file.parent / "store.json"
    store.write_text('{"series_a": [], "series_b": []}', encoding="ascii")
    monkeypatch.setattr("experiments.commands.test_particle_plot.NBODY_BASELINES", (tables_file,))
    invoke("test-particle-plot", "--store", str(store))
    _assert_figure_written(assets_fig_dir, "test-particle-bias")
    monkeypatch.setattr("experiments.commands.test_particle_plot.NBODY_BASELINES", (tables_file.parent / "no.json",))
    invoke("test-particle-plot", "--store", str(store))


def test_nbody_figures_from_tables(assets_fig_dir: Path, tables_file: Path) -> None:
    """The four N-body figures are built from the tables without the razor-thin run."""
    figures = make_nbody_figures([load_tables(tables_file)])
    assert sorted(figures) == ["nbody-destination", "nbody-exponents", "nbody-rules", "nbody-variance"]
    _assert_figure_written(assets_fig_dir, "nbody-variance")
