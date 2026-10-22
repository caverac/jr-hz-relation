r"""Extract tracked-particle time series and ring sums from a GADGET format 1 run.

Two products are written per snapshot. ``tracks/snap_NNNN.npy`` holds the positions and
velocities (six float32 columns) of a fixed random sample of disk particles followed by
every perturber, one row per tracked particle in the order of ``meta/tracked_ids.npy``.
``rings/snap_NNNN.npz`` holds sums over all disk particles in rings of width
:data:`RING_WIDTH`, as a ``names`` array and a ``values`` matrix with one row per name: the
count, $\sum \cos m\phi$ and $\sum \sin m\phi$ for $m = 1$ to :data:`HARMONICS`, and the
first two moments of $z$, $v_R$, $v_\phi$ and $v_z$; with them the ring ``edges``, the
snapshot ``time``, and the ``center`` and ``bulk`` velocity (medians of the tracked disk
sample) that were subtracted. Snapshots whose two products already exist are skipped, so
a stopped run can be resumed, and a snapshot that cannot be read (a failing drive) is
reported and skipped.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt

from experiments.gadget import PERTURBER_TYPE, Snapshot, read_snapshot

F32 = npt.NDArray[np.float32]
F64 = npt.NDArray[np.float64]
U32 = npt.NDArray[np.uint32]
I32 = npt.NDArray[np.int32]

#: Number of azimuthal harmonics summed per ring.
HARMONICS = 8
#: Ring width and outer edge of the ring sums (kpc).
RING_WIDTH = 0.25
RING_MAX = 20.0
RING_EDGES: F64 = np.arange(0.0, RING_MAX + 0.5 * RING_WIDTH, RING_WIDTH)
#: Disk particles processed per chunk when summing the rings.
CHUNK = 10_000_000


@dataclass(frozen=True)
class Extracted:
    """The tracks of one snapshot with the frame of its tracked disk and the missing count."""

    tracks: F32
    center: F64
    bulk: F64
    missing: int


def choose_tracked(snapshot: Snapshot, sample: int, seed: int) -> U32:
    """Choose a sorted random sample of disk ids and append every perturber id."""
    rng = np.random.default_rng(seed)
    disk_ids = snapshot.ids[: snapshot.n_disk]
    picked = np.sort(rng.choice(disk_ids, size=sample, replace=False))
    first = sum(snapshot.npart[:PERTURBER_TYPE])
    last = first + snapshot.npart[PERTURBER_TYPE]
    perturbers = np.sort(snapshot.ids[first:last])
    return np.concatenate([picked, perturbers]).astype(np.uint32)


def build_lookup(tracked: U32, max_id: int) -> I32:
    """Build the table from particle id to row in the tracks file, or -1 if the id is not tracked.

    The table covers the ids of the snapshot and the tracked ids, so a tracked id absent
    from the snapshot (a perturber of another run) is simply never found.
    """
    lookup = np.full(max(max_id, int(tracked.max())) + 1, -1, dtype=np.int32)
    lookup[tracked] = np.arange(len(tracked), dtype=np.int32)
    return lookup


def extract_tracks(snapshot: Snapshot, lookup: I32, n_tracked: int) -> F32:
    """Return the positions and velocities of the tracked particles, in tracked order."""
    slot = lookup[snapshot.ids]
    found = slot >= 0
    rows = slot[found]
    tracks = np.full((n_tracked, 6), np.nan, dtype=np.float32)
    tracks[rows, :3] = snapshot.positions[found]
    tracks[rows, 3:] = snapshot.velocities[found]
    return tracks


def chunk_weights(coords: F64, vels: F64) -> dict[str, F64]:
    """Return the per-particle quantities whose ring sums are stored, keyed by output name."""
    radius = np.maximum(np.hypot(coords[:, 0], coords[:, 1]), 1e-12)
    cos_phi, sin_phi = coords[:, 0] / radius, coords[:, 1] / radius
    v_r = vels[:, 0] * cos_phi + vels[:, 1] * sin_phi
    v_phi = vels[:, 1] * cos_phi - vels[:, 0] * sin_phi
    weights = {
        "z": coords[:, 2],
        "z2": coords[:, 2] ** 2,
        "abs_z": np.abs(coords[:, 2]),
        "v_r": v_r,
        "v_r2": v_r**2,
        "v_phi": v_phi,
        "v_phi2": v_phi**2,
        "v_z": vels[:, 2],
        "v_z2": vels[:, 2] ** 2,
    }
    phase = cos_phi + 1j * sin_phi
    harmonic = np.ones_like(phase)
    for m in range(1, HARMONICS + 1):
        harmonic = harmonic * phase
        weights[f"cos{m}"] = harmonic.real
        weights[f"sin{m}"] = harmonic.imag
    return weights


def ring_sums(snapshot: Snapshot, center: F64, bulk: F64) -> dict[str, F64]:
    """Sum the ring quantities over all disk particles, in chunks."""
    n_rings = len(RING_EDGES) - 1
    sums: dict[str, F64] = {"count": np.zeros(n_rings)}
    for start in range(0, snapshot.n_disk, CHUNK):
        stop = min(start + CHUNK, snapshot.n_disk)
        coords = np.asarray(snapshot.positions[start:stop], dtype=np.float64) - center
        vels = np.asarray(snapshot.velocities[start:stop], dtype=np.float64) - bulk
        ring = np.searchsorted(RING_EDGES, np.hypot(coords[:, 0], coords[:, 1]), side="right") - 1
        inside = (ring >= 0) & (ring < n_rings)
        ring = ring[inside]
        sums["count"] += np.bincount(ring, minlength=n_rings)
        for name, weight in chunk_weights(coords[inside], vels[inside]).items():
            sums[name] = sums.get(name, np.zeros(n_rings)) + np.bincount(ring, weights=weight, minlength=n_rings)
    return sums


def parse_snapshots(spec: str) -> list[int]:
    """Expand a comma-separated list of Python ranges into sorted snapshot numbers."""
    numbers: set[int] = set()
    for part in spec.split(","):
        bounds = [int(x) for x in part.split(":")]
        numbers.update(range(*bounds) if len(bounds) > 1 else bounds)
    return sorted(numbers)


def save_rings(path: Path, sums: dict[str, F64], snapshot_time: float, center: F64, bulk: F64) -> None:
    """Write the ring sums as a name array and a (name, ring) matrix, with the frame data."""
    names = sorted(sums)
    values = np.stack([sums[name] for name in names])
    np.savez(
        path,
        names=np.array(names),
        values=values,
        time=np.array([snapshot_time]),
        center=center,
        bulk=bulk,
        edges=RING_EDGES,
    )


def process(snapshot: Snapshot, lookup: I32, n_tracked: int, n_disk_tracked: int) -> Extracted:
    """Extract the tracks of one snapshot and the center and bulk velocity of its tracked disk."""
    tracks = extract_tracks(snapshot, lookup, n_tracked)
    missing = int(np.isnan(tracks[:, 0]).sum())
    center = np.nanmedian(tracks[:n_disk_tracked, :3], axis=0).astype(np.float64)
    bulk = np.nanmedian(tracks[:n_disk_tracked, 3:], axis=0).astype(np.float64)
    return Extracted(tracks, center, bulk, missing)


def tracked_lookup(path: Path, snapshot: Snapshot, sample: int, seed: int) -> I32:
    """Load the tracked ids, choosing them from this snapshot when the file does not exist yet.

    The number of disk rows is recorded next to the ids, in ``disk_rows.npy``, for the
    commands that read the tracks.
    """
    if not path.exists():
        np.save(path, choose_tracked(snapshot, sample, seed))
        np.save(path.parent / "disk_rows.npy", np.array(sample))
    return build_lookup(np.load(path), int(snapshot.ids.max()))


def disk_rows(data: Path) -> int:
    """Return the number of leading tracked rows that are disk particles in an extraction."""
    return int(np.load(data / "meta" / "disk_rows.npy"))


@dataclass(frozen=True)
class Extraction:
    """Where a run is read from and written to, and how its tracked sample is chosen."""

    run: Path
    output: Path
    sample: int = 1_000_000
    seed: int = 1


def extract_run(setup: Extraction, numbers: list[int]) -> Iterator[str]:
    """Extract the requested snapshots, skipping finished ones, and yield one progress line each."""
    for sub in ("tracks", "rings", "meta"):
        (setup.output / sub).mkdir(parents=True, exist_ok=True)
    tracked_path = setup.output / "meta" / "tracked_ids.npy"
    lookup: I32 | None = None
    for number in numbers:
        track_file = setup.output / "tracks" / f"snap_{number:04d}.npy"
        ring_file = setup.output / "rings" / f"snap_{number:04d}.npz"
        if track_file.exists() and ring_file.exists():
            continue
        started = time.perf_counter()
        try:
            snapshot = read_snapshot(setup.run / f"snap_{number:03d}")
        except (OSError, ValueError) as error:
            yield f"# snap_{number:03d} unreadable, skipped: {error}"
            continue
        if lookup is None:
            lookup = tracked_lookup(tracked_path, snapshot, setup.sample, setup.seed)
        n_tracked = int((lookup >= 0).sum())
        extracted = process(snapshot, lookup, n_tracked, n_tracked - snapshot.npart[PERTURBER_TYPE])
        if extracted.missing:
            yield f"# {extracted.missing} tracked particles missing at t = {snapshot.time}"
        np.save(track_file, extracted.tracks)
        sums = ring_sums(snapshot, extracted.center, extracted.bulk)
        save_rings(ring_file, sums, snapshot.time, extracted.center, extracted.bulk)
        yield f"snap_{number:04d} t = {snapshot.time:.4f} done in {time.perf_counter() - started:.1f} s"
