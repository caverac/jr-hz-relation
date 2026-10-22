"""Read and write little-endian GADGET format 1 snapshots that carry no mass block.

A format 1 file is a sequence of Fortran-style blocks, each bracketed by a 4-byte length
marker: the 256-byte header, then the positions, the velocities and the ids of every
particle, ordered by particle type. Only the particle numbers per type and the time are
read from the header. The masses must all be in the header, so the files carry no mass
block; the writer builds such files for the synthetic runs of the test suite.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt

F32 = npt.NDArray[np.float32]
U32 = npt.NDArray[np.uint32]

#: Size of the header block in bytes.
HEADER_BYTES = 256
#: The leading header fields: six particle numbers, six masses and the time.
HEADER_FORMAT = "<6I6dd"
#: Offset of the first position byte: header marker, header, end marker, position marker.
POSITIONS_OFFSET = 4 + HEADER_BYTES + 4 + 4
#: GADGET particle type of the disk and of the perturbers in the runs of this project.
DISK_TYPE = 2
PERTURBER_TYPE = 3


@dataclass(frozen=True)
class Snapshot:
    """The header fields of a GADGET format 1 file and its particle blocks."""

    time: float
    npart: tuple[int, ...]
    positions: F32
    velocities: F32
    ids: U32

    @property
    def n_disk(self) -> int:
        """Number of disk particles, which come first in the file."""
        return self.npart[DISK_TYPE]


def read_header(raw: bytes, path: Path) -> tuple[tuple[int, ...], float]:
    """Return the particle numbers and the time of a header block, marker included."""
    if len(raw) < 4 + HEADER_BYTES:
        raise ValueError(f"{path} is shorter than a header block")
    if struct.unpack("<i", raw[:4]) != (HEADER_BYTES,):
        raise ValueError(f"{path} is not a little-endian GADGET format 1 file")
    header_end = 4 + struct.calcsize(HEADER_FORMAT)
    fields = struct.unpack(HEADER_FORMAT, raw[4:header_end])
    return tuple(int(n) for n in fields[0:6]), float(fields[12])


def read_snapshot(path: Path) -> Snapshot:
    """Read the header and the position, velocity and id blocks of a snapshot."""
    with path.open("rb") as stream:
        npart, snapshot_time = read_header(stream.read(4 + HEADER_BYTES), path)
        total = sum(npart)
        stream.seek(POSITIONS_OFFSET - 4)
        (marker,) = struct.unpack("<i", stream.read(4))
        if marker != 12 * total:
            raise ValueError(f"{path}: position block of {marker} bytes does not match {total} particles")
        positions = np.fromfile(stream, dtype="<f4", count=3 * total).reshape(total, 3)
        stream.seek(8, 1)
        velocities = np.fromfile(stream, dtype="<f4", count=3 * total).reshape(total, 3)
        stream.seek(4, 1)
        (marker,) = struct.unpack("<i", stream.read(4))
        if marker != 4 * total:
            raise ValueError(f"{path}: id block of {marker} bytes is not 4 bytes per particle")
        ids = np.fromfile(stream, dtype="<u4", count=total)
    return Snapshot(snapshot_time, npart, positions, velocities, ids)


def _block(payload: bytes) -> bytes:
    """Bracket a payload with its 4-byte length markers."""
    marker = struct.pack("<i", len(payload))
    return marker + payload + marker


def write_snapshot(path: Path, snapshot: Snapshot) -> None:
    """Write a snapshot as a format 1 file, with unit masses in the header for every populated type."""
    masses = tuple(1.0 if n else 0.0 for n in snapshot.npart)
    header = struct.pack(HEADER_FORMAT, *snapshot.npart, *masses, snapshot.time)
    header += bytes(HEADER_BYTES - len(header))
    with path.open("wb") as stream:
        stream.write(_block(header))
        stream.write(_block(np.ascontiguousarray(snapshot.positions, dtype="<f4").tobytes()))
        stream.write(_block(np.ascontiguousarray(snapshot.velocities, dtype="<f4").tobytes()))
        stream.write(_block(np.ascontiguousarray(snapshot.ids, dtype="<u4").tobytes()))
