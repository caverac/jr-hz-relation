"""Tests for the migration test between two windows."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from experiments.migration import (
    Particles,
    Ring,
    WindowValues,
    bias_points,
    destination_row,
    finite_mean,
    format_table,
    ks_distance,
    kurtosis,
    load_particles,
    load_spiral,
    load_tables,
    origin_row,
    parse_harmonics,
    parse_rings,
    power_law_fit,
    report,
    safe_median,
)


def _values(n: int, r_g: float) -> WindowValues:
    """Build window values for ``n`` particles at one guiding radius."""
    ones = np.ones(n)
    return WindowValues(lz=ones, r_g=np.full(n, r_g), abs_z=ones, vz2=ones, j_z=ones, t_z=ones, j_r=ones)


def _particles(n: int, outward: bool) -> Particles:
    """Build particles that all moved from 5 to 6 kpc (outward) or from 6 to 5 kpc (inward)."""
    origin, later = (5.5, 6.5) if outward else (6.5, 5.5)
    return Particles(_values(n, origin), _values(n, later), np.ones((n, 2)), np.array([1.0, 2.0]), (0.0, 1.0))


def _ring(n: int) -> Ring:
    """Build a ring selecting every particle, all of them migrating."""
    return Ring(5.0, 6.0, 2.0, np.ones(n, dtype=bool), np.ones(n), np.full(n, 10.0), 1.0)


def test_parse_helpers() -> None:
    """Harmonic and ring specs expand as documented."""
    amplitude = np.array([[0.1, 0.1], [0.3, 0.3], [0.2, 0.2]])
    centers = np.array([4.0, 5.0])
    assert parse_harmonics("5:9", amplitude, centers) == [5, 6, 7, 8]
    assert parse_harmonics("7", amplitude, centers) == [7]
    assert parse_harmonics("0", amplitude, centers) == [2]
    assert parse_rings("3:5:1") == [(3.0, 4.0), (4.0, 5.0)]


def test_statistics() -> None:
    """The small statistics behave on known inputs."""
    assert kurtosis(np.array([-1.0, 1.0, -1.0, 1.0])) == pytest.approx(-2.0)
    assert ks_distance(np.array([0.0, 1.0]), np.array([0.0, 1.0])) == 0.0
    assert ks_distance(np.array([0.0, 1.0]), np.array([2.0, 3.0])) == 1.0
    assert np.isnan(safe_median(np.array([])))
    assert safe_median(np.array([1.0, 3.0])) == 2.0
    assert np.isnan(finite_mean(np.array([np.nan])))
    slope, intercept = power_law_fit(np.array([1.0, 2.0, 4.0]), np.array([2.0, 8.0, 32.0]), np.ones(3))
    assert slope == pytest.approx(2.0) and intercept == pytest.approx(np.log(2.0))
    assert power_law_fit(np.array([1.0, 2.0]), np.array([1.0, 1.0]), np.ones(2), slope=1.0)[0] == 1.0
    assert np.isnan(power_law_fit(np.array([1.0, 2.0]), np.array([1.0, 0.0]), np.ones(2))[0])


def test_form_at_interpolates_and_clamps() -> None:
    """The form factor is interpolated inside the grid and held at its ends outside."""
    particles = Particles(_values(1, 5.5), _values(1, 5.5), np.array([[0.8, 0.4]]), np.array([1.0, 2.0]), (0.0, 1.0))
    assert particles.form_at(1.5)[0] == pytest.approx(0.6)
    assert particles.form_at(0.2)[0] == pytest.approx(0.8)
    assert particles.form_at(9.0)[0] == pytest.approx(0.4)


def test_origin_row_one_sided() -> None:
    """A ring whose migrators all go one way has no KS distance."""
    row = origin_row(_ring(4), _particles(4, outward=True))
    assert row["n_in"] == 0 and row["n_out"] == 4
    assert np.isnan(float(row["ks_in_out"]))
    assert np.isnan(float(row["median_Jz_in"]))


def test_destination_row_without_arrivals() -> None:
    """A destination ring without arrivals of one kind reports NaN ratios for it."""
    particles = _particles(4, outward=False)
    migrating = np.ones(4, dtype=bool)
    row = destination_row(particles, migrating, (5.0, 6.0))
    assert row["n_in"] == 4 and row["n_out"] == 0
    assert row["n_local"] == 0
    assert np.isnan(float(row["measured_out"]))


def test_format_and_report(tables_file: Path) -> None:
    """The markdown tables and the report carry every section, including a sweep."""
    lines = format_table("Title", [{"a": 1, "b": 0.5}], 1)
    assert lines[1] == "| a | b |" and lines[-1] == "| 1 | 0.5 |"
    tables = load_tables(tables_file)
    tables["sweep"] = [{"ring": "3 to 4", "k=1": 2.0, "k=2": 1.0}]
    text = "\n".join(report(tables))
    assert "collapse across rings" in text
    assert "The product b_k k" in text
    assert "| 3 to 4 | 2.00 | 2.00 |" in text


def test_bias_points(tables_file: Path) -> None:
    """Every origin ring gives one (alpha, ln ratio) point with alpha from the ring's wavenumber."""
    tables = load_tables(tables_file)
    points = bias_points(tables)
    assert len(points) == 9
    assert points[0][0] == pytest.approx(float(tables["core"][0]["k"]) * 0.313)
    assert all(np.isfinite(bias) for _, bias in points)


def test_tables_contents(tables_file: Path) -> None:
    """The migration tables hold nine origin rings with finite exponents and the metadata."""
    tables = load_tables(tables_file)
    assert tables["meta"]["baseline"] == pytest.approx(0.2)
    assert tables["meta"]["form"] == "layer" and tables["meta"]["harmonics"] == [5, 6, 7, 8]
    assert [row["ring"] for row in tables["core"]][:2] == ["3 to 4", "4 to 5"]
    assert len(tables["core"]) == 9
    assert all(np.isfinite(row["exponent_F"]) for row in tables["core"])
    assert len(tables["rules"]) == 45
    assert tables["collapse"]["F"] > 0.0


def test_load_particles_rejects_different_grids(
    tmp_path: Path, window_files: tuple[Path, Path], spiral_file: Path
) -> None:
    """Two windows with different wavenumber grids cannot be compared."""
    spiral = load_spiral(spiral_file, 0, "5")
    data = dict(np.load(window_files[1]))
    data["k_grid"] = data["k_grid"][:-1]
    data["form_layer"] = data["form_layer"][:, :-1]
    other = tmp_path / "other.npz"
    np.savez(other, **data)
    with pytest.raises(ValueError, match="different wavenumber grids"):
        load_particles(window_files[0], other, spiral, "form_layer")
