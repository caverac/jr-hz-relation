"""Publication figures (PDF) for the provenance-bias analysis.

Each function builds one figure with matplotlib's object-oriented API (no global
pyplot state) and writes a PDF. Resolution arguments have publication defaults but
can be reduced for fast tests. :func:`make_all_figures` writes the full set.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from jr_hz_relation.form_factor import dispersion_ratio, strength_matching_anchor, vertical_form_factor
from jr_hz_relation.overlap import milky_way_overlap
from jr_hz_relation.sheet import vertical_action
from jr_hz_relation.validate import form_factor_orbit

#: k z0 for the Milky Way (lambda_R ~ 3 kpc, z0 ~ 0.4 kpc).
MW_ALPHA: float = 0.84

#: Measured migrator coldness sigma_z,mig / sigma_z,all (Vera-Ciro+2016 Fig. 4).
MEASURED_RATIO: float = 0.80


def _save(fig: Figure, path: Path) -> Path:
    """Attach an Agg canvas and write the figure to ``path`` as PDF."""
    FigureCanvasAgg(fig)
    fig.savefig(path, format="pdf", bbox_inches="tight")
    return path


def figure_form_factor(path: Path, n_energies: int = 60) -> Path:
    """Plot the vertical form factor ``F`` versus vertical action for several ``k``.

    Parameters
    ----------
    path :
        Output PDF path.
    n_energies :
        Number of vertical-energy samples.

    Returns
    -------
    pathlib.Path
        The written path.
    """
    energies = np.linspace(0.02, 4.0, n_energies)
    actions = np.array([vertical_action(float(e)) for e in energies])
    fig = Figure(figsize=(6.0, 4.0))
    axes = fig.add_subplot(1, 1, 1)
    for alpha, colour in ((0.5, "C0"), (MW_ALPHA, "C1"), (2.0, "C3")):
        form = np.array([vertical_form_factor(float(e), alpha) for e in energies])
        axes.plot(actions, form, "-", color=colour, label=rf"$\alpha=k z_0={alpha:g}$")
    axes.set_xlabel(r"vertical action $J_z$ (sheet units)")
    axes.set_ylabel(r"form factor $F(J_z,k)=\langle e^{-k|z|}\rangle$")
    axes.set_ylim(0.0, 1.02)
    axes.legend()
    return _save(fig, path)


def figure_provenance_bias(path: Path, n_alpha: int = 16) -> Path:
    """Plot the predicted migrator coldness versus disc thickness, with the MW anchor.

    Parameters
    ----------
    path :
        Output PDF path.
    n_alpha :
        Number of thickness samples.

    Returns
    -------
    pathlib.Path
        The written path.
    """
    s_anchor = strength_matching_anchor(MW_ALPHA, MEASURED_RATIO)
    alphas = np.linspace(0.2, 1.8, n_alpha)
    bias = np.array([1.0 - dispersion_ratio(float(a), s_anchor) for a in alphas])
    fig = Figure(figsize=(6.0, 4.0))
    axes = fig.add_subplot(1, 1, 1)
    axes.plot(alphas, 100.0 * bias, "-", color="C0", label=rf"prediction ($s={s_anchor:.2f}$)")
    axes.plot(
        [MW_ALPHA],
        [100.0 * (1.0 - MEASURED_RATIO)],
        "k*",
        markersize=13,
        label="Milky Way (Vera-Ciro+2016)",
    )
    axes.set_xlabel(r"disc thickness $\alpha = k\,h_Z$")
    axes.set_ylabel(r"migrator coldness $1-\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$ (\%)")
    axes.legend()
    return _save(fig, path)


def figure_form_factor_validation(
    path: Path, n_curve: int = 80, n_markers: int = 10, n_periods: int = 15, samples_per_period: int = 300
) -> Path:
    """Overplot galpy's orbit-integrated form factor on the quadrature curve.

    The analytic quadrature ``F`` is drawn as a smooth curve (cheap), and galpy's
    independent orbit-average is overplotted as markers at a coarser set of vertical
    actions (each marker is one galpy integration); the lower panel shows the
    galpy-minus-quadrature residual -- a cross-check of the central object of the
    paper that shares no code with the quadrature.

    Parameters
    ----------
    path :
        Output PDF path.
    n_curve :
        Number of vertical-energy samples for the quadrature curves.
    n_markers :
        Number of vertical-energy samples for the galpy markers and residual.
    n_periods :
        Vertical periods averaged per galpy orbit.
    samples_per_period :
        Time samples per vertical period in the galpy integration.

    Returns
    -------
    pathlib.Path
        The written path.
    """
    energies = np.linspace(0.05, 4.0, n_curve)
    marks = np.linspace(0.1, 3.8, n_markers)
    mark_actions = np.array([vertical_action(float(e)) for e in marks])
    fig = Figure(figsize=(6.0, 5.0))
    top = fig.add_subplot(2, 1, 1)
    bottom = fig.add_subplot(2, 1, 2, sharex=top)

    def _series(alpha: float, colour: str) -> None:
        """Plot one ``alpha`` series: quadrature curve, galpy markers, residual."""
        actions = np.array([vertical_action(float(e)) for e in energies])
        curve = np.array([vertical_form_factor(float(e), alpha) for e in energies])
        quad = np.array([vertical_form_factor(float(e), alpha) for e in marks])
        orbit = np.array([form_factor_orbit(float(e), alpha, n_periods, samples_per_period) for e in marks])
        top.plot(actions, curve, "-", color=colour, label=rf"$\alpha={alpha:g}$")
        top.plot(mark_actions, orbit, "o", color=colour, markersize=4, fillstyle="none")
        bottom.plot(mark_actions, orbit - quad, "o-", color=colour, markersize=3)

    for alpha, colour in ((0.5, "C0"), (MW_ALPHA, "C1"), (2.0, "C3")):
        _series(alpha, colour)
    top.plot([], [], "k-", label="quadrature")
    top.plot([], [], "ko", fillstyle="none", label="galpy orbit")
    top.set_ylabel(r"form factor $F(J_z,k)=\langle e^{-k|z|}\rangle$")
    top.set_ylim(0.0, 1.02)
    top.legend(fontsize=7, ncol=3)
    bottom.set_xlabel(r"vertical action $J_z$ (sheet units)")
    bottom.set_ylabel(r"galpy $-$ quadrature")
    bottom.axhline(0.0, color="0.6", linewidth=0.8)
    return _save(fig, path)


def figure_resonance_overlap(path: Path, n_strength: int = 60) -> Path:
    """Plot the bar-spiral Chirikov overlap parameter versus spiral strength.

    The Milky Way bar-spiral corotation overlap ``S`` is shown for vertically cold
    (``F=1``) and hot (``F=0.5``) stars; ``S=1`` marks the onset of diffusive
    churning. Cold stars cross the threshold at lower strength, so the diffusive
    regime is biased toward them.

    Parameters
    ----------
    path :
        Output PDF path.
    n_strength :
        Number of spiral-strength samples.

    Returns
    -------
    pathlib.Path
        The written path.
    """
    strengths = np.linspace(0.005, 0.05, n_strength)
    fig = Figure(figsize=(6.0, 4.0))
    axes = fig.add_subplot(1, 1, 1)
    for form, colour, label in ((1.0, "C0", "vertically cold"), (0.5, "C3", "vertically hot")):
        overlaps = np.array([milky_way_overlap(float(s), form_factor=form) for s in strengths])
        axes.plot(strengths, overlaps, "-", color=colour, label=rf"$F={form:g}$ ({label})")
    axes.axhline(1.0, color="0.4", linestyle="--", label="overlap threshold")
    axes.axvspan(0.01, 0.03, color="0.85", label="physical strength")
    axes.set_xlabel(r"spiral strength $\epsilon=|\Phi_s|/V_c^2$")
    axes.set_ylabel(r"Chirikov overlap $S$ (bar--spiral corotation)")
    axes.legend()
    return _save(fig, path)


def make_all_figures(outdir: Path) -> dict[str, Path]:
    """Write the full figure set to ``outdir`` and return a name-to-path mapping.

    Parameters
    ----------
    outdir :
        Directory to write the PDFs into (created if missing).

    Returns
    -------
    dict[str, pathlib.Path]
        Mapping from figure name to written path.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    return {
        "form-factor": figure_form_factor(outdir / "form-factor.pdf"),
        "provenance-bias": figure_provenance_bias(outdir / "provenance-bias.pdf"),
        "form-factor-validation": figure_form_factor_validation(outdir / "form-factor-validation.pdf"),
        "resonance-overlap": figure_resonance_overlap(outdir / "resonance-overlap.pdf"),
    }
