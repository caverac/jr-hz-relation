"""Tests for the spiral measurements."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from conftest import SPIRAL_M

from experiments.spiral import (
    RotationCurve,
    WindowModes,
    combined_wavenumber,
    layer_factor,
    load_rings,
    local_maxima,
    measure_window,
    model_rotation_curve,
    parse_windows,
    per_particle,
    resonance_radius,
)


def test_layer_factor_limits() -> None:
    """The layer factor is one for a razor-thin perturbation and falls with the wavenumber."""
    values = layer_factor(np.array([0.0, 1.0, 4.0]))
    assert values[0] == pytest.approx(1.0)
    assert 1.0 > values[1] > values[2] > 0.0


def test_rotation_curve_is_physical() -> None:
    """The model circular speed rises through the disk and the epicyclic frequency exceeds omega."""
    curve = model_rotation_curve()
    assert curve.at("v_circ", np.array([8.0]))[0] == pytest.approx(178.8, abs=1.0)
    assert np.all(curve.kappa[10:] > curve.omega[10:])


def test_per_particle_handles_empty_rings() -> None:
    """Ring sums divided by zero counts give the chosen fill value."""
    assert np.allclose(per_particle(np.array([2.0, 3.0]), np.array([2.0, 0.0]), 0.0), [1.0, 0.0])
    assert np.isnan(per_particle(np.array([2.0]), np.array([0.0]))[0])


def test_local_maxima_orders_peaks() -> None:
    """Local maxima above the peak fraction come strongest first."""
    power = np.zeros((5, 5))
    power[1, 1] = 1.0
    power[3, 3] = 0.5
    power[4, 0] = 0.01
    assert local_maxima(power) == [(1, 1), (3, 3)]


def test_resonance_radius_bounds() -> None:
    """Pattern speeds outside the range of the frequency curve give NaN."""
    curve = RotationCurve(np.array([1.0, 2.0, 3.0]), np.ones(3), np.array([3.0, 2.0, 1.0]), np.ones(3))
    assert np.isnan(resonance_radius(curve, curve.omega, 0.5))
    assert np.isnan(resonance_radius(curve, curve.omega, 3.0))
    assert resonance_radius(curve, curve.omega, 1.5) == pytest.approx(2.5)


def test_parse_windows_default_is_whole_run() -> None:
    """An empty spec covers every snapshot, a spec expands to its windows."""
    times = np.array([0.0, 0.1, 0.2])
    assert parse_windows("", times)[0][0] == 0.0
    assert parse_windows("", times)[0][1] > 0.2
    assert parse_windows("0:0.1,0.1:0.3", times) == [(0.0, 0.1), (0.1, 0.3)]


def test_load_rings_requires_files(tmp_path: Path) -> None:
    """An empty directory is an error."""
    with pytest.raises(FileNotFoundError):
        load_rings(tmp_path)


def test_window_needs_two_snapshots(extracted: Path) -> None:
    """A window holding one snapshot is rejected."""
    rings = load_rings(extracted / "rings")
    with pytest.raises(ValueError, match="fewer than two"):
        measure_window(rings, model_rotation_curve(), (0.0, 0.005))


def test_imprinted_pattern_is_measured(spiral_file: Path) -> None:
    """The imprinted m = 5 pattern dominates at 4 to 8 kpc and its wavenumber is near the imprinted one."""
    data = np.load(spiral_file)
    amplitude = data["amplitude"][0]
    edges = data["edges"]
    centers = 0.5 * (edges[:-1] + edges[1:])
    band = (centers > 4.0) & (centers < 8.0)
    assert np.argmax(amplitude[:, band].mean(axis=1)) + 1 == SPIRAL_M
    assert data["window_bounds"].shape == (2, 2)
    modes = WindowModes(
        (0.0, 0.12),
        amplitude,
        data["wavenumber"][0],
        data["coherence"][0],
        data["epsilon"][0],
        data["spectrogram"][0],
    )
    assert combined_wavenumber(modes, edges, [SPIRAL_M], (4.0, 8.0)) == pytest.approx(2.0, abs=0.5)
