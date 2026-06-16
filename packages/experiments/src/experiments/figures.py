"""Publication figures for the provenance-bias analysis.

Each function builds one figure with matplotlib's object-oriented API (no global
pyplot state) and returns it. The :func:`~experiments._plotting.figure` decorator
applies the shared house style and writes the figure to ``assets/figures`` as both a
``.png`` (documentation) and a ``.pdf`` (paper), only when the content changed.
:func:`make_all_figures` builds the full set.
"""

from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure

from experiments._plotting import figure
from experiments.balescu_lenard import diffusion_weight
from experiments.crossover import crossover_weight
from experiments.form_factor import dispersion_ratio, vertical_form_factor
from experiments.overlap import milky_way_overlap
from experiments.sheet import vertical_action, vertical_frequency
from experiments.thickness import softened_dispersion_ratio
from experiments.trapping import trapped_fraction, trapping_dispersion_ratio

#: k z0 for the Milky Way (lambda_R ~ 3 kpc, z0 ~ 0.4 kpc).
MW_ALPHA: float = 0.84

#: Physical range of the dimensionless spiral strength s = sigma_R^2 / |Phi_s| for
#: |Phi_s| ~ 1-3% of V_c^2: used to bound the predicted bias instead of anchoring to
#: any external value.
PHYSICAL_STRENGTH: tuple[float, float] = (0.8, 2.0)


@figure("form-factor")
def figure_form_factor(n_energies: int = 60) -> Figure:
    """Plot the vertical form factor ``F`` versus vertical action for several ``k``.

    Parameters
    ----------
    n_energies :
        Number of vertical-energy samples.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    energies = np.linspace(0.001, 4.0, n_energies)
    actions = np.array([vertical_action(float(e)) for e in energies])
    fig = Figure(figsize=(3.8, 3.3))
    axes = fig.add_subplot(1, 1, 1)
    for alpha, linestyle in ((0.5, "-"), (MW_ALPHA, "--"), (2.0, ":")):
        form = np.array([vertical_form_factor(float(e), alpha) for e in energies])
        axes.plot(actions, form, linestyle=linestyle, label=rf"$\alpha = {alpha:g}$", color="#000000", linewidth=1.5)
    axes.set_xlabel(r"$J_z$")
    axes.set_ylabel(r"$F(J_z,k)$")
    axes.set_ylim(0.0, 1.02)
    axes.legend()
    return fig


@figure("provenance-bias")
def figure_provenance_bias(n_alpha: int = 16) -> Figure:
    """Plot the predicted migrator coldness versus disc thickness for physical spiral strengths.

    The bias is shown as a band over the physical spiral-strength range
    :data:`PHYSICAL_STRENGTH`, not anchored to any external value.

    Parameters
    ----------
    n_alpha :
        Number of thickness samples.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    s_low, s_high = PHYSICAL_STRENGTH
    alphas = np.linspace(0.2, 1.8, n_alpha)
    bias_weak = np.array([float(np.log(dispersion_ratio(float(a), s_low))) for a in alphas])
    bias_strong = np.array([float(np.log(dispersion_ratio(float(a), s_high))) for a in alphas])
    fig = Figure(figsize=(3.8, 3.3))
    axes = fig.add_subplot(1, 1, 1)
    axes.fill_between(alphas, bias_weak, bias_strong, color="0.9")
    axes.plot(alphas, bias_weak, "k-", linewidth=1.5, label=rf"$s={s_low:g}$")
    axes.plot(alphas, bias_strong, "k--", linewidth=1.5, label=rf"$s={s_high:g}$")
    axes.axvline(MW_ALPHA, color="#808080", linestyle=":", linewidth=1.5, label=r"Milky Way ($\alpha=0.84$)")
    axes.set_xlabel(r"$\alpha$")
    axes.set_ylabel(r"$\ln\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$")
    axes.legend()
    return fig


@figure("resonance-overlap")
def figure_resonance_overlap(n_strength: int = 60) -> Figure:
    """Plot the bar-spiral Chirikov overlap parameter versus spiral strength.

    The Milky Way bar-spiral corotation overlap ``S`` is shown for vertically cold
    (``F=1``) and hot (``F=0.5``) stars; ``S=1`` marks the onset of diffusive
    churning. Cold stars cross the threshold at lower strength, so the diffusive
    regime is biased toward them.

    Parameters
    ----------
    n_strength :
        Number of spiral-strength samples.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    strengths = np.linspace(0.005, 0.05, n_strength)
    fig = Figure(figsize=(3.8, 3.3))
    axes = fig.add_subplot(1, 1, 1)
    for form, linestyle, label in ((1.0, "-", "vertically cold"), (0.5, "--", "vertically hot")):
        overlaps = np.array([milky_way_overlap(float(s), form_factor=form) for s in strengths])
        axes.plot(strengths, overlaps, linestyle, color="#000000", linewidth=1.5, label=rf"$F={form:g}$ ({label})")
    axes.axhline(1.0, color="#808080", linestyle=":", linewidth=1.5, label="overlap threshold")
    axes.axvspan(0.01, 0.03, color="0.85", linewidth=0.0)
    axes.text(0.02, 1.3, "physical\nstrength", ha="center", va="center", color="0.35")
    axes.set_xlabel(r"$\epsilon$")
    axes.set_ylabel(r"$S$")
    axes.legend()
    return fig


@figure("trapped-weight")
def figure_trapped_weight(n_energy: int = 60) -> Figure:
    r"""Plot the exact trapped weight versus vertical action for several island widths.

    The normalised trapped weight ``W/W_0`` interpolates between the dilute
    ``\sqrt{F}`` law (narrow islands) and a flat, saturated profile (wide islands)
    as the island-width parameter ``kappa`` grows.

    Parameters
    ----------
    n_energy :
        Number of vertical-energy samples.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    energies = np.linspace(0.05, 4.0, n_energy)
    actions = np.array([vertical_action(float(e)) for e in energies])
    forms = np.array([vertical_form_factor(float(e), MW_ALPHA) for e in energies])
    fig = Figure(figsize=(3.8, 3.3))
    axes = fig.add_subplot(1, 1, 1)
    for kappa, linestyle in ((0.3, "--"), (1.0, "-."), (3.0, ":")):
        weight = np.array([trapped_fraction(float(value), kappa) for value in forms])
        axes.plot(actions, weight / weight[0], linestyle, color="#000000", label=rf"$\kappa={kappa:g}$", linewidth=1.5)
    axes.plot(actions, np.sqrt(forms), "k-", label=r"$\sqrt{F}$ (dilute limit)", linewidth=2.0)
    axes.set_xlabel(r"$J_z$")
    axes.set_ylabel(r"$W/W_0$")
    axes.set_ylim(0.0, 1.02)
    axes.legend()
    return fig


@figure("trapping-cap")
def figure_trapping_cap(n_kappa: int = 20, n_energy: int = 60) -> Figure:
    r"""Plot the provenance bias from the exact trapped fraction versus island width.

    The single-resonance bias rises to the ``\sqrt{F}`` cap as ``kappa -> 0`` and
    falls toward zero for wide islands, so single-resonance trapping is bounded by
    the cap for any spiral strength.

    Parameters
    ----------
    n_kappa :
        Number of island-width samples.
    n_energy :
        Number of vertical-energy quadrature points.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    energies = np.linspace(1e-3, 12.0, n_energy)
    forms = np.array([vertical_form_factor(float(e), MW_ALPHA) for e in energies])
    base = np.exp(-energies) * (2.0 * np.pi / np.array([vertical_frequency(float(e)) for e in energies]))

    def _bias(kappa: float) -> float:
        """Percentage migrator coldness for island-width ``kappa`` at the MW thickness."""
        weight = np.array([trapped_fraction(float(value), kappa) for value in forms])
        mean_all = np.trapezoid(energies * base, energies) / np.trapezoid(base, energies)
        mean_mig = np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies)
        return float(np.log(np.sqrt(mean_mig / mean_all)))

    kappas = np.logspace(-1.0, 1.0, n_kappa)
    fig = Figure(figsize=(3.8, 3.3))
    axes = fig.add_subplot(1, 1, 1)
    axes.semilogx(
        kappas,
        [_bias(float(k)) for k in kappas],
        "k-",
        markersize=3,
        label="single-resonance trapping",
        linewidth=1.5,
    )
    axes.axhline(_bias(1e-3), color="#808080", linestyle=":", label=r"$\sqrt{F}$ cap", linewidth=1.5)
    axes.set_xlabel(r"$\kappa$")
    axes.set_ylabel(r"$\ln\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$")
    axes.legend()
    return fig


@figure("crossover-bias")
def figure_crossover_bias(n_overlap: int = 24, n_energy: int = 120) -> Figure:
    r"""Plot the provenance bias across the trapping-to-diffusion overlap transition.

    The bias from the crossover weight ``W = F^{p(S_0 \sqrt{F})}`` rises from the
    ``\sqrt{F}`` trapping floor toward the ``F^2`` diffusion ceiling as the effective
    overlap ``S_0`` grows; the bar-spiral overlap region (where transient spirals
    supplement the bar and spiral) is shaded.

    Parameters
    ----------
    n_overlap :
        Number of overlap-strength samples.
    n_energy :
        Number of vertical-energy quadrature points.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    energies = np.linspace(1e-3, 12.0, n_energy)
    forms = np.array([vertical_form_factor(float(e), MW_ALPHA) for e in energies])
    base = np.exp(-energies) * (2.0 * np.pi / np.array([vertical_frequency(float(e)) for e in energies]))

    def _bias(overlap_strength: float) -> float:
        """Log dispersion ratio ln(sigma_mig/sigma_all) at overlap ``overlap_strength``."""
        weight = np.array([crossover_weight(float(value), overlap_strength) for value in forms])
        mean_all = np.trapezoid(energies * base, energies) / np.trapezoid(base, energies)
        mean_mig = np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies)
        return float(np.log(np.sqrt(mean_mig / mean_all)))

    overlaps = np.linspace(0.0, 4.0, n_overlap)
    fig = Figure(figsize=(3.8, 3.3))
    axes = fig.add_subplot(1, 1, 1)
    axes.plot(overlaps, [_bias(float(s)) for s in overlaps], "k-", linewidth=1.5, label="overlap crossover")
    axes.axhline(_bias(0.0), color="#808080", linestyle=":", linewidth=1.5, label=r"$\sqrt{F}$ trapping floor")
    axes.axhline(_bias(50.0), color="#808080", linestyle="--", linewidth=1.5, label=r"$F^2$ diffusion ceiling")
    axes.axvspan(0.9, 1.1, color="0.9", label="bar+spiral overlap")
    axes.set_xlabel(r"$S_0$")
    axes.set_ylabel(r"$\ln\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$")
    axes.legend()
    return fig


@figure("finite-thickness")
def figure_finite_thickness(n_thickness: int = 20) -> Figure:
    """Plot the single-resonance bias versus spiral thickness with finite-thickness F.

    The razor-thin form factor softens as the spiral acquires a finite vertical scale
    ``h=h_s/z_0``, weakening the bias by an order-unity factor in the Milky-Way
    regime ``h`` ~ 0.5--1.

    Parameters
    ----------
    n_thickness :
        Number of spiral-thickness samples.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    thicknesses = np.linspace(0.0, 1.5, n_thickness)
    biases = np.array([float(np.log(softened_dispersion_ratio(MW_ALPHA, float(h)))) for h in thicknesses])
    fig = Figure(figsize=(3.8, 3.3))
    axes = fig.add_subplot(1, 1, 1)
    axes.plot(thicknesses, biases, "k-", linewidth=1.5, label="single-resonance bias")
    axes.axvspan(0.5, 1.0, color="0.9", label="spiral thickness (Milky Way)")
    axes.set_xlabel(r"$h$")
    axes.set_ylabel(r"$\ln\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$")
    axes.legend()
    return fig


@figure("balescu-lenard")
def figure_balescu_lenard(n_b: int = 24, n_energy: int = 120) -> Figure:
    r"""Plot the diffusive provenance bias versus the resonance-broadening parameter.

    The Balescu-Lenard weight ``W=F^2/(1+b\sqrt{F})`` pins the diffusive bias to a
    narrow band between the ``F^2`` and ``F^{3/2}`` limits, nearly independent of the
    broadening ``b``.

    Parameters
    ----------
    n_b :
        Number of broadening-parameter samples.
    n_energy :
        Number of vertical-energy quadrature points.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    energies = np.linspace(1e-3, 12.0, n_energy)
    forms = np.array([vertical_form_factor(float(e), MW_ALPHA) for e in energies])
    base = np.exp(-energies) * (2.0 * np.pi / np.array([vertical_frequency(float(e)) for e in energies]))

    def _bias(broadening: float) -> float:
        """Log dispersion ratio ln(sigma_mig/sigma_all) at broadening ``broadening``."""
        weight = np.array([diffusion_weight(float(value), broadening) for value in forms])
        mean_all = np.trapezoid(energies * base, energies) / np.trapezoid(base, energies)
        mean_mig = np.trapezoid(energies * base * weight, energies) / np.trapezoid(base * weight, energies)
        return float(np.log(np.sqrt(mean_mig / mean_all)))

    broadenings = np.linspace(0.0, 20.0, n_b)
    fig = Figure(figsize=(3.8, 3.3))
    axes = fig.add_subplot(1, 1, 1)
    bias_f2 = _bias(0.0)  # b -> 0: W = F^2
    bias_f32 = _bias(1e6)  # b -> inf: W ~ F^{3/2}
    axes.plot(broadenings, [_bias(float(b)) for b in broadenings], "k-", linewidth=1.5, label="resonance-broadened")
    axes.axhline(bias_f2, color="#808080", linestyle="--", linewidth=1.5, label=r"$F^2$ limit ($b\to0$)")
    axes.axhline(bias_f32, color="#808080", linestyle=":", linewidth=1.5, label=r"$F^{3/2}$ limit ($b\to\infty$)")
    axes.set_xlabel(r"$b$")
    axes.set_ylabel(r"$\ln\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$")
    axes.legend()
    return fig


@figure("test-particle-bias")
def figure_test_particle(
    series_a: list[tuple[float, float, float]],
    series_b: list[tuple[float, float, float]],
    n_curve: int = 60,
) -> Figure:
    """Plot the test-particle validation (two panels) from precomputed store data.

    Parameters
    ----------
    series_a :
        Single-transient points ``(alpha, bias_mean, bias_err)``.
    series_b :
        Resonance-overlap points ``(count, bias_mean, bias_err)``.
    n_curve :
        Number of points in the analytic single-resonance curve.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    grid = np.linspace(0.1, 1.5, n_curve)
    analytic = np.array([np.log(trapping_dispersion_ratio(float(a), 1e-3)) for a in grid])
    # The store already holds the log dispersion ratio ln(sigma_mig/sigma_all) and its
    # standard error, so the points are plotted directly.
    alphas = np.array([p[0] for p in series_a])
    mean_a = np.array([p[1] for p in series_a])
    err_a = np.array([p[2] for p in series_a])
    counts = np.array([p[0] for p in series_b])
    mean_b = np.array([p[1] for p in series_b])
    err_b = np.array([p[2] for p in series_b])
    fig = Figure(figsize=(8.0, 3.5))
    left = fig.add_subplot(1, 2, 1)
    right = fig.add_subplot(1, 2, 2, sharey=left)
    left.plot(grid, analytic, "k-", linewidth=1.5, label="analytic single-resonance")
    left.errorbar(
        alphas,
        mean_a,
        yerr=err_a,
        fmt="o",
        color="#000000",
        markerfacecolor="white",
        markersize=5,
        capsize=3,
        label="test particles",
    )
    left.set_xlabel(r"$\alpha$")
    left.set_ylabel(r"$\ln\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$")
    left.legend()
    right.errorbar(
        counts,
        mean_b,
        yerr=err_b,
        fmt="o",
        color="#000000",
        markerfacecolor="white",
        markersize=5,
        capsize=3,
    )
    right.set_xlabel(r"$M$")
    right.tick_params(labelleft=False)
    return fig


def make_all_figures(
    series_a: list[tuple[float, float, float]],
    series_b: list[tuple[float, float, float]],
) -> dict[str, Figure]:
    """Build and save the full figure set to ``assets/figures``.

    Every figure is analytic except ``test-particle-bias``, which only *plots* the
    cached orbit-integration results passed in as ``series_a``/``series_b`` -- a cheap
    operation. The expensive simulation that fills that cache is the separate
    ``test-particle-simulate`` command; loading the cache is the caller's job (see the
    ``figures`` command), keeping this module free of the simulation machinery.

    Parameters
    ----------
    series_a :
        Cached single-transient points ``(alpha, bias_mean, bias_err)``.
    series_b :
        Cached overlap points ``(count, bias_mean, bias_err)``.

    Returns
    -------
    dict[str, matplotlib.figure.Figure]
        Mapping from figure name to the built figure.
    """
    return {
        "form-factor": figure_form_factor(),
        "provenance-bias": figure_provenance_bias(),
        "resonance-overlap": figure_resonance_overlap(),
        "trapped-weight": figure_trapped_weight(),
        "trapping-cap": figure_trapping_cap(),
        "crossover-bias": figure_crossover_bias(),
        "finite-thickness": figure_finite_thickness(),
        "balescu-lenard": figure_balescu_lenard(),
        "test-particle-bias": figure_test_particle(series_a, series_b),
    }
