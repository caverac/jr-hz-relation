"""Tests for the extraction of tracks and ring sums."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from conftest import SyntheticRun, build_run

from experiments.gadget import Snapshot, read_snapshot, write_snapshot
from experiments.tracks import RING_EDGES, Extraction, disk_rows, extract_run, parse_snapshots


def test_parse_snapshots() -> None:
    """Ranges and single numbers expand to a sorted list without duplicates."""
    assert parse_snapshots("5:8,3,0:12:5") == [0, 3, 5, 6, 7, 10]


def test_products(extracted: Path, synthetic_run: SyntheticRun) -> None:
    """Every snapshot has both products with the expected shapes and the frame data."""
    numbers = range(len(synthetic_run.times))
    assert all((extracted / "tracks" / f"snap_{n:04d}.npy").exists() for n in numbers)
    tracks = np.load(extracted / "tracks" / "snap_0003.npy")
    assert tracks.shape == (4000 + synthetic_run.n_perturbers, 6)
    assert np.isfinite(tracks).all()
    rings = np.load(extracted / "rings" / "snap_0003.npz")
    assert float(rings["time"][0]) == synthetic_run.times[3]
    assert np.array_equal(rings["edges"], RING_EDGES)
    names = [str(name) for name in rings["names"]]
    count = rings["values"][names.index("count")]
    assert count.sum() <= synthetic_run.n_disk
    assert np.allclose(rings["center"], 0.0, atol=0.5)
    assert disk_rows(extracted) == 4000


def test_extraction_resumes_and_skips_unreadable(tmp_path: Path, synthetic_run: SyntheticRun) -> None:
    """Finished snapshots are skipped on a rerun and an unreadable snapshot is reported."""
    output = tmp_path / "out"
    numbers = [0, 1]
    setup = Extraction(synthetic_run.directory, output, sample=100, seed=3)
    first = list(extract_run(setup, numbers))
    assert len(first) == 2 and first[0].startswith("snap_0000 t = 0.0000 done")
    assert not list(extract_run(setup, numbers))
    broken = tmp_path / "broken"
    broken.mkdir()
    (broken / "snap_000").write_bytes(b"")
    lines = list(extract_run(Extraction(broken, tmp_path / "other", sample=100, seed=3), [0]))
    assert lines[0].startswith("# snap_000 unreadable, skipped")


def test_missing_tracked_particles_are_reported(tmp_path: Path) -> None:
    """A snapshot that lacks some tracked particles yields a missing-count line and NaN rows."""
    run = build_run(tmp_path / "snapshots", seed=5, perturbers=2)
    output = tmp_path / "out"
    setup = Extraction(run.directory, output, sample=50, seed=1)
    list(extract_run(setup, [0]))
    full = read_snapshot(run.directory / "snap_001")
    keep = full.ids != np.load(output / "meta" / "tracked_ids.npy")[0]
    reduced = Snapshot(
        full.time,
        (0, 0, run.n_disk - 1, run.n_perturbers, 0, 0),
        full.positions[keep],
        full.velocities[keep],
        full.ids[keep],
    )
    write_snapshot(run.directory / "snap_001", reduced)
    lines = list(extract_run(setup, [1]))
    assert lines[0] == "# 1 tracked particles missing at t = 0.01"
    assert np.isnan(np.load(output / "tracks" / "snap_0001.npy")[0]).all()
