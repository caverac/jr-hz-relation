"""Shared fixtures for the experiments test suite."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")


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
