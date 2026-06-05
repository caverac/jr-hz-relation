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
