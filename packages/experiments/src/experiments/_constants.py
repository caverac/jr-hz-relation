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
