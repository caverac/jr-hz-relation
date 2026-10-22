"""Tests for the GADGET format 1 reader and writer."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
import pytest

from experiments.gadget import HEADER_BYTES, Snapshot, read_snapshot, write_snapshot


def _snapshot(n_disk: int = 5, n_perturbers: int = 2) -> Snapshot:
    """Build a tiny snapshot with sequential ids."""
    total = n_disk + n_perturbers
    return Snapshot(
        time=0.25,
        npart=(0, 0, n_disk, n_perturbers, 0, 0),
        positions=np.arange(3 * total, dtype=np.float32).reshape(total, 3),
        velocities=-np.arange(3 * total, dtype=np.float32).reshape(total, 3),
        ids=np.arange(total, dtype=np.uint32),
    )


def test_roundtrip(tmp_path: Path) -> None:
    """A written snapshot reads back with the same header fields and blocks."""
    path = tmp_path / "snap_000"
    write_snapshot(path, _snapshot())
    read = read_snapshot(path)
    assert read.time == 0.25
    assert read.npart == (0, 0, 5, 2, 0, 0)
    assert read.n_disk == 5
    assert np.array_equal(read.positions, _snapshot().positions)
    assert np.array_equal(read.velocities, _snapshot().velocities)
    assert np.array_equal(read.ids, _snapshot().ids)


def test_bad_header_marker(tmp_path: Path) -> None:
    """A file that does not start with the header marker is rejected."""
    path = tmp_path / "snap_000"
    path.write_bytes(bytes(4 + HEADER_BYTES + 64))
    with pytest.raises(ValueError, match="not a little-endian GADGET"):
        read_snapshot(path)


def test_truncated_header(tmp_path: Path) -> None:
    """A file shorter than a header block is rejected rather than crashing the unpacking."""
    path = tmp_path / "snap_000"
    path.write_bytes(b"\x00\x01")
    with pytest.raises(ValueError, match="shorter than a header"):
        read_snapshot(path)


def _corrupt_marker(path: Path, offset: int) -> None:
    """Overwrite the 4-byte marker at ``offset`` with a wrong value."""
    raw = bytearray(path.read_bytes())
    struct.pack_into("<i", raw, offset, 7)
    path.write_bytes(bytes(raw))


def test_bad_position_marker(tmp_path: Path) -> None:
    """A position block whose marker does not match the particle count is rejected."""
    path = tmp_path / "snap_000"
    write_snapshot(path, _snapshot())
    _corrupt_marker(path, 4 + HEADER_BYTES + 4)
    with pytest.raises(ValueError, match="position block"):
        read_snapshot(path)


def test_bad_id_marker(tmp_path: Path) -> None:
    """An id block whose marker is not 4 bytes per particle is rejected."""
    path = tmp_path / "snap_000"
    snapshot = _snapshot()
    write_snapshot(path, snapshot)
    total = sum(snapshot.npart)
    blocks = 4 + HEADER_BYTES + 4
    _corrupt_marker(path, blocks + 2 * (4 + 12 * total + 4))
    with pytest.raises(ValueError, match="id block"):
        read_snapshot(path)
