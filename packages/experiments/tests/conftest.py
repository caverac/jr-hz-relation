"""Shared fixtures for the experiments test suite.

The N-body fixtures build a small synthetic GADGET run: a disk in solid-body rotation with
an imprinted m = 5 spiral, vertical and radial oscillations, and a slow drift of the radius
whose size falls with the vertical amplitude, so that the whole ``nbody-*`` chain runs in
seconds and the variance of the angular-momentum change depends on the form factor.
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import pytest
from click.testing import CliRunner

from experiments.cli import main
from experiments.gadget import Snapshot, write_snapshot

matplotlib.use("Agg")

N_DISK = 6000
N_PERTURBERS = 8
N_SNAPSHOTS = 32
TIME_STEP = 0.01
OMEGA = 30.0  # solid-body angular speed (km/s/kpc)
NU_Z = 2.0 * np.pi / 0.05  # vertical frequency: period 0.05 time units
KAPPA = 2.0 * np.pi / 0.08  # radial frequency: period 0.08 time units
SPIRAL_M = 5
SPIRAL_K = 2.0  # radial wavenumber of the imprinted pattern (1/kpc)
SPIRAL_CONTRAST = 0.4


@dataclass(frozen=True)
class SyntheticRun:
    """Where a synthetic run lives and how it was built."""

    directory: Path
    n_disk: int
    n_perturbers: int
    times: tuple[float, ...]


@dataclass(frozen=True)
class Orbits:
    """The parameters of every synthetic disk orbit."""

    radius: np.ndarray
    phase: np.ndarray
    drift: np.ndarray
    z_amplitude: np.ndarray
    z_phase: np.ndarray
    r_amplitude: np.ndarray
    r_phase: np.ndarray

    def at(self, t: float) -> tuple[np.ndarray, np.ndarray]:
        """Return the (n, 3) positions and velocities of the disk at time t."""
        radius = self.radius * (1.0 + self.drift * t) + self.r_amplitude * np.cos(KAPPA * t + self.r_phase)
        radius_dot = self.radius * self.drift - self.r_amplitude * KAPPA * np.sin(KAPPA * t + self.r_phase)
        phi = self.phase + OMEGA * t
        z = self.z_amplitude * np.cos(NU_Z * t + self.z_phase)
        v_z = -self.z_amplitude * NU_Z * np.sin(NU_Z * t + self.z_phase)
        positions = np.stack([radius * np.cos(phi), radius * np.sin(phi), z], axis=1)
        v_x = radius_dot * np.cos(phi) - radius * OMEGA * np.sin(phi)
        v_y = radius_dot * np.sin(phi) + radius * OMEGA * np.cos(phi)
        return positions, np.stack([v_x, v_y, v_z], axis=1)


def spiral_azimuths(rng: np.random.Generator, radius: np.ndarray) -> np.ndarray:
    """Draw azimuths whose density follows 1 + contrast cos(m phi + k R), by rejection."""
    phi = np.zeros(len(radius))
    pending = np.ones(len(radius), dtype=bool)
    while pending.any():
        candidates = rng.uniform(0.0, 2.0 * np.pi, int(pending.sum()))
        density = 1.0 + SPIRAL_CONTRAST * np.cos(SPIRAL_M * candidates + SPIRAL_K * radius[pending])
        accepted = rng.uniform(0.0, 1.0 + SPIRAL_CONTRAST, len(candidates)) < density
        indices = np.flatnonzero(pending)[accepted]
        phi[indices] = candidates[accepted]
        pending[indices] = False
    return phi


def draw_orbits(rng: np.random.Generator, n_disk: int) -> Orbits:
    """Draw the orbit parameters of the synthetic disk."""
    radius = np.minimum(0.5 + rng.exponential(4.0, n_disk), 14.0)
    z_amplitude = np.abs(rng.normal(0.0, 0.3, n_disk))
    drift = 0.3 * np.exp(-SPIRAL_K * z_amplitude) * rng.normal(0.0, 1.0, n_disk)
    return Orbits(
        radius=radius,
        phase=spiral_azimuths(rng, radius),
        drift=drift,
        z_amplitude=z_amplitude,
        z_phase=rng.uniform(0.0, 2.0 * np.pi, n_disk),
        r_amplitude=np.abs(rng.normal(0.0, 0.15, n_disk)),
        r_phase=rng.uniform(0.0, 2.0 * np.pi, n_disk),
    )


def build_run(directory: Path, seed: int = 0, id_offset: int = 0, perturbers: int = N_PERTURBERS) -> SyntheticRun:
    """Write the snapshots of a synthetic run; ``id_offset`` shifts every id, as the control runs do."""
    rng = np.random.default_rng(seed)
    orbits = draw_orbits(rng, N_DISK)
    disk_ids = rng.permutation(N_DISK).astype(np.uint32) + np.uint32(id_offset)
    perturber_radius = rng.uniform(6.0, 8.0, perturbers)
    perturber_phase = rng.uniform(0.0, 2.0 * np.pi, perturbers)
    perturber_ids = (N_DISK + np.arange(perturbers) + id_offset).astype(np.uint32)
    directory.mkdir(parents=True, exist_ok=True)
    times = tuple(round(index * TIME_STEP, 6) for index in range(N_SNAPSHOTS))
    for number, t in enumerate(times):
        positions, velocities = orbits.at(t)
        phi = perturber_phase + OMEGA * t
        extra = np.stack([perturber_radius * np.cos(phi), perturber_radius * np.sin(phi), np.zeros(perturbers)], axis=1)
        extra_v = np.stack([-perturber_radius * OMEGA * np.sin(phi), perturber_radius * OMEGA * np.cos(phi)], axis=1)
        extra_v = np.concatenate([extra_v, np.zeros((perturbers, 1))], axis=1)
        snapshot = Snapshot(
            time=t,
            npart=(0, 0, N_DISK, perturbers, 0, 0),
            positions=np.concatenate([positions, extra]).astype(np.float32),
            velocities=np.concatenate([velocities, extra_v]).astype(np.float32),
            ids=np.concatenate([disk_ids, perturber_ids]).astype(np.uint32),
        )
        write_snapshot(directory / f"snap_{number:03d}", snapshot)
    return SyntheticRun(directory, N_DISK, perturbers, times)


def invoke(*args: str) -> str:
    """Invoke the CLI, assert success and return its output."""
    result = CliRunner().invoke(main, list(args))
    trace = "".join(traceback.format_exception(*result.exc_info)) if result.exc_info else ""
    assert result.exit_code == 0, f"{result.output}\n{trace}"
    return result.output


@pytest.fixture()
def assets_fig_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the generated-figure directory to a temporary path.

    The :func:`~experiments._plotting.figure` decorator resolves output paths
    against ``ASSETS_FIG_DIR``; patching it keeps tests from writing into the real
    ``assets/figures`` directory.

    Returns
    -------
    pathlib.Path
        The temporary figure directory.
    """
    fig_dir = tmp_path / "figures"
    monkeypatch.setattr("experiments._constants.ASSETS_FIG_DIR", fig_dir)
    monkeypatch.setattr("experiments._plotting.ASSETS_FIG_DIR", fig_dir)
    return fig_dir


@pytest.fixture(scope="session")
def synthetic_run(tmp_path_factory: pytest.TempPathFactory) -> SyntheticRun:
    """Build the synthetic perturbed run once per session."""
    return build_run(tmp_path_factory.mktemp("run") / "snapshots")


@pytest.fixture(scope="session")
def extracted(synthetic_run: SyntheticRun, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Extract every snapshot of the synthetic run with the CLI and return the data directory."""
    data = tmp_path_factory.mktemp("data") / "run"
    invoke("nbody-extract", str(synthetic_run.directory), str(data), "--snapshots", "0:32", "--sample", "4000")
    return data


@pytest.fixture(scope="session")
def control_extracted(extracted: Path, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Extract a control run with 1-based ids and no perturbers, tracking the same particles."""
    run = build_run(tmp_path_factory.mktemp("control") / "snapshots", id_offset=1, perturbers=0)
    data = tmp_path_factory.mktemp("control-data") / "control"
    (data / "meta").mkdir(parents=True)
    np.save(data / "meta" / "tracked_ids.npy", np.load(extracted / "meta" / "tracked_ids.npy") + np.uint32(1))
    np.save(data / "meta" / "disk_rows.npy", np.load(extracted / "meta" / "disk_rows.npy"))
    invoke("nbody-extract", str(run.directory), str(data), "--snapshots", "0:32")
    return data


@pytest.fixture(scope="session")
def spiral_file(extracted: Path) -> Path:
    """Measure the spiral in two windows of the extracted run and return the modes file."""
    output = extracted / "analysis" / "modes.npz"
    invoke("nbody-spiral", str(extracted), "--windows", "0:0.12,0.2:0.32", "--output", str(output))
    return output


@pytest.fixture(scope="session")
def window_files(extracted: Path) -> tuple[Path, Path]:
    """Summarize the origin and the later window of the extracted run."""
    for start in ("0.0", "0.2"):
        invoke("nbody-window", str(extracted), "--start", start, "--length", "0.12")
    windows = extracted / "analysis" / "windows"
    return windows / "t_0.000.npz", windows / "t_0.200.npz"


@pytest.fixture(scope="session")
def tables_file(window_files: tuple[Path, Path], spiral_file: Path) -> Path:
    """Run the migration test between the two windows and return its JSON tables."""
    output = spiral_file.parent / "migration.json"
    invoke("nbody-migration", str(window_files[0]), str(window_files[1]), str(spiral_file), "--output", str(output))
    return output
