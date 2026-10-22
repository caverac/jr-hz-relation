r"""Shared paths for the ``experiments`` package.

The generated figure set lives in a single repository-level ``assets/figures``
directory rather than inside the LaTeX source tree. The paper (``packages/pre-print``)
copies in the ``.pdf`` files at build time and the documentation site
(``packages/docs``) consumes the ``.png`` files through a Docusaurus
``staticDirectories`` entry, so neither consumer owns the figures.
"""

from __future__ import annotations

from pathlib import Path

#: Repository root, four parents up from this file
#: (``packages/experiments/src/experiments/_constants.py``).
REPO_ROOT: Path = Path(__file__).resolve().parents[4]

#: Directory holding every generated figure (both ``.png`` and ``.pdf``).
ASSETS_FIG_DIR: Path = REPO_ROOT / "assets" / "figures"

#: Directory holding cached experiment data (e.g. the test-particle store).
ASSETS_DATA_DIR: Path = REPO_ROOT / "assets" / "data"

#: Cached test-particle orbit-integration store. Filled by the (expensive)
#: ``test-particle-simulate`` command and plotted (cheaply) by ``test-particle-plot``
#: and the full ``figures`` set.
TEST_PARTICLE_STORE: Path = ASSETS_DATA_DIR / "test-particle-data.json"

#: Time unit of the N-body runs in Gyr (kpc per km/s).
TIME_UNIT_GYR: float = 0.9778

#: Cached tables of the N-body migration test, one JSON file per baseline, written by
#: ``nbody-migration`` from the (local, 15 GB) extraction products and plotted by
#: ``nbody-plot`` and the full ``figures`` set.
NBODY_DATA_DIR: Path = ASSETS_DATA_DIR / "nbody"

#: The three baselines with the layer form factor, origin t = 0.5 against t = 1.0, 1.5 and 2.5.
NBODY_BASELINES: tuple[Path, ...] = tuple(
    NBODY_DATA_DIR / name for name in ("migration-0.5-1.0.json", "migration-0.5-1.5.json", "migration-0.5-2.5.json")
)

#: The first baseline with the razor-thin form factor at the m = 7 wavenumber.
NBODY_THIN: Path = NBODY_DATA_DIR / "migration-thin-0.5-1.0.json"
