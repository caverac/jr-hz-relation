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

from jr_hz_relation.balescu_lenard import diffusion_weight
from jr_hz_relation.crossover import crossover_weight
from jr_hz_relation.form_factor import dispersion_ratio, strength_matching_anchor, vertical_form_factor
from jr_hz_relation.overlap import milky_way_overlap
from jr_hz_relation.sheet import vertical_action, vertical_frequency
from jr_hz_relation.thickness import softened_dispersion_ratio
from jr_hz_relation.trapping import trapped_fraction
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


def figure_trapped_weight(path: Path, n_energy: int = 60) -> Path:
    r"""Plot the exact trapped weight versus vertical action for several island widths.

    The normalised trapped weight ``W/W_0`` interpolates between the dilute
    ``\sqrt{F}`` law (narrow islands) and a flat, saturated profile (wide islands)
    as the island-width parameter ``kappa`` grows.

    Parameters
    ----------
    path :
        Output PDF path.
    n_energy :
        Number of vertical-energy samples.

    Returns
    -------
    pathlib.Path
        The written path.
    """
    energies = np.linspace(0.05, 4.0, n_energy)
    actions = np.array([vertical_action(float(e)) for e in energies])
    forms = np.array([vertical_form_factor(float(e), MW_ALPHA) for e in energies])
    fig = Figure(figsize=(6.0, 4.0))
    axes = fig.add_subplot(1, 1, 1)
    for kappa, colour in ((0.3, "C0"), (1.0, "C1"), (3.0, "C3")):
        weight = np.array([trapped_fraction(float(value), kappa) for value in forms])
        axes.plot(actions, weight / weight[0], "-", color=colour, label=rf"$\kappa={kappa:g}$")
    axes.plot(actions, np.sqrt(forms), "k--", label=r"$\sqrt{F}$ (dilute limit)")
    axes.set_xlabel(r"vertical action $J_z$ (sheet units)")
    axes.set_ylabel(r"trapped weight $W/W_0$")
    axes.set_ylim(0.0, 1.02)
    axes.legend()
    return _save(fig, path)


def figure_trapping_cap(path: Path, n_kappa: int = 20, n_energy: int = 60) -> Path:
    r"""Plot the provenance bias from the exact trapped fraction versus island width.

    The single-resonance bias rises to the ``\sqrt{F}`` cap as ``kappa -> 0`` and
    falls toward zero for wide islands; the measured bias lies above the cap,
    showing single-resonance trapping cannot reproduce it.

    Parameters
    ----------
    path :
        Output PDF path.
    n_kappa :
        Number of island-width samples.
    n_energy :
        Number of vertical-energy quadrature points.

    Returns
    -------
    pathlib.Path
        The written path.
    """
    energies = np.linspace(1e-3, 12.0, n_energy)
    forms = np.array([vertical_form_factor(float(e), MW_ALPHA) for e in energies])
    base = np.exp(-energies) * (2.0 * np.pi / np.array([vertical_frequency(float(e)) for e in energies]))

    def _bias(kappa: float) -> float:
        """Percentage migrator coldness for island-width ``kappa`` at the MW thickness."""
        weight = np.array([trapped_fraction(float(value), kappa) for value in forms])
        mean_all = np.trapezoid(energies * base, energies) / np.trapezoid(base, energies)
        mean_mig = np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies)
        return float(100.0 * (1.0 - np.sqrt(mean_mig / mean_all)))

    kappas = np.logspace(-1.0, 1.0, n_kappa)
    fig = Figure(figsize=(6.0, 4.0))
    axes = fig.add_subplot(1, 1, 1)
    axes.semilogx(kappas, [_bias(float(k)) for k in kappas], "C2-o", markersize=3, label="single-resonance trapping")
    axes.axhline(_bias(1e-3), color="0.4", linestyle=":", label=r"$\sqrt{F}$ cap")
    axes.axhline(100.0 * (1.0 - MEASURED_RATIO), color="k", linestyle="--", label="measured (Vera-Ciro+2016)")
    axes.set_xlabel(r"island-width parameter $\kappa$")
    axes.set_ylabel(r"migrator coldness $1-\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$ (\%)")
    axes.legend()
    return _save(fig, path)


def figure_crossover_bias(path: Path, n_overlap: int = 24, n_energy: int = 120) -> Path:
    r"""Plot the provenance bias across the trapping-to-diffusion overlap transition.

    The bias from the crossover weight ``W = F^{p(S_0 \sqrt{F})}`` rises from the
    ``\sqrt{F}`` trapping floor toward the ``F^2`` diffusion ceiling as the effective
    overlap ``S_0`` grows; the measured value is reached near the overlap expected
    once transient spirals supplement the bar and spiral.

    Parameters
    ----------
    path :
        Output PDF path.
    n_overlap :
        Number of overlap-strength samples.
    n_energy :
        Number of vertical-energy quadrature points.

    Returns
    -------
    pathlib.Path
        The written path.
    """
    energies = np.linspace(1e-3, 12.0, n_energy)
    forms = np.array([vertical_form_factor(float(e), MW_ALPHA) for e in energies])
    base = np.exp(-energies) * (2.0 * np.pi / np.array([vertical_frequency(float(e)) for e in energies]))

    def _bias(overlap_strength: float) -> float:
        """Percentage migrator coldness at overlap ``overlap_strength``."""
        weight = np.array([crossover_weight(float(value), overlap_strength) for value in forms])
        mean_all = np.trapezoid(energies * base, energies) / np.trapezoid(base, energies)
        mean_mig = np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies)
        return float(100.0 * (1.0 - np.sqrt(mean_mig / mean_all)))

    overlaps = np.linspace(0.0, 4.0, n_overlap)
    fig = Figure(figsize=(6.0, 4.0))
    axes = fig.add_subplot(1, 1, 1)
    axes.plot(overlaps, [_bias(float(s)) for s in overlaps], "C4-o", markersize=3, label="overlap crossover")
    axes.axhline(_bias(0.0), color="0.4", linestyle=":", label=r"$\sqrt{F}$ trapping floor")
    axes.axhline(_bias(50.0), color="0.6", linestyle=":", label=r"$F^2$ diffusion ceiling")
    axes.axhline(100.0 * (1.0 - MEASURED_RATIO), color="k", linestyle="--", label="measured (Vera-Ciro+2016)")
    axes.axvspan(0.9, 1.1, color="0.9", label="bar+spiral overlap")
    axes.set_xlabel(r"effective resonance overlap $S_0$")
    axes.set_ylabel(r"migrator coldness $1-\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$ (\%)")
    axes.legend()
    return _save(fig, path)


def figure_finite_thickness(path: Path, n_thickness: int = 20) -> Path:
    """Plot the single-resonance bias versus spiral thickness with finite-thickness F.

    The razor-thin form factor softens as the spiral acquires a finite vertical scale
    ``h=h_s/z_0``, weakening the bias by an order-unity factor in the Milky-Way
    regime ``h`` ~ 0.5--1.

    Parameters
    ----------
    path :
        Output PDF path.
    n_thickness :
        Number of spiral-thickness samples.

    Returns
    -------
    pathlib.Path
        The written path.
    """
    thicknesses = np.linspace(0.0, 1.5, n_thickness)
    biases = np.array([100.0 * (1.0 - softened_dispersion_ratio(MW_ALPHA, float(h))) for h in thicknesses])
    fig = Figure(figsize=(6.0, 4.0))
    axes = fig.add_subplot(1, 1, 1)
    axes.plot(thicknesses, biases, "C5-o", markersize=3, label="single-resonance bias")
    axes.axvspan(0.5, 1.0, color="0.9", label="spiral thickness (MW)")
    axes.set_xlabel(r"spiral thickness $h=h_s/z_0$")
    axes.set_ylabel(r"migrator coldness $1-\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$ (\%)")
    axes.legend()
    return _save(fig, path)


def figure_balescu_lenard(path: Path, n_b: int = 24, n_energy: int = 120) -> Path:
    r"""Plot the diffusive provenance bias versus the resonance-broadening parameter.

    The Balescu-Lenard weight ``W=F^2/(1+b\sqrt{F})`` pins the diffusive bias to a
    narrow band between the ``F^2`` and ``F^{3/2}`` limits, nearly independent of the
    broadening ``b``; the measured value sits inside it.

    Parameters
    ----------
    path :
        Output PDF path.
    n_b :
        Number of broadening-parameter samples.
    n_energy :
        Number of vertical-energy quadrature points.

    Returns
    -------
    pathlib.Path
        The written path.
    """
    energies = np.linspace(1e-3, 12.0, n_energy)
    forms = np.array([vertical_form_factor(float(e), MW_ALPHA) for e in energies])
    base = np.exp(-energies) * (2.0 * np.pi / np.array([vertical_frequency(float(e)) for e in energies]))

    def _bias(broadening: float) -> float:
        """Percentage migrator coldness at broadening ``broadening``."""
        weight = np.array([diffusion_weight(float(value), broadening) for value in forms])
        mean_all = np.trapezoid(energies * base, energies) / np.trapezoid(base, energies)
        mean_mig = np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies)
        return float(100.0 * (1.0 - np.sqrt(mean_mig / mean_all)))

    broadenings = np.linspace(0.0, 20.0, n_b)
    fig = Figure(figsize=(6.0, 4.0))
    axes = fig.add_subplot(1, 1, 1)
    axes.axhspan(_bias(1e6), _bias(0.0), color="0.92", label=r"diffusive band ($F^{3/2}$ to $F^2$)")
    axes.plot(broadenings, [_bias(float(b)) for b in broadenings], "C6-o", markersize=3, label="resonance-broadened")
    axes.axhline(100.0 * (1.0 - MEASURED_RATIO), color="k", linestyle="--", label="measured (Vera-Ciro+2016)")
    axes.set_xlabel(r"broadening parameter $b$")
    axes.set_ylabel(r"migrator coldness $1-\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$ (\%)")
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
        "trapped-weight": figure_trapped_weight(outdir / "trapped-weight.pdf"),
        "trapping-cap": figure_trapping_cap(outdir / "trapping-cap.pdf"),
        "crossover-bias": figure_crossover_bias(outdir / "crossover-bias.pdf"),
        "finite-thickness": figure_finite_thickness(outdir / "finite-thickness.pdf"),
        "balescu-lenard": figure_balescu_lenard(outdir / "balescu-lenard.pdf"),
    }
