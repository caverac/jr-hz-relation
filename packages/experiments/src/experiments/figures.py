"""Publication figures for the provenance-bias analysis.

Each function builds one figure with matplotlib's object-oriented API (no global
pyplot state) and returns it. The :func:`~experiments._plotting.figure` decorator
applies the shared house style and writes the figure to ``assets/figures`` as both a
``.png`` (documentation) and a ``.pdf`` (paper), only when the content changed.
:func:`make_all_figures` builds the full set.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib import colormaps
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm
from matplotlib.figure import Figure

from experiments._plotting import figure
from experiments.balescu_lenard import diffusion_weight
from experiments.crossover import crossover_weight
from experiments.form_factor import dispersion_ratio, vertical_form_factor
from experiments.overlap import milky_way_overlap
from experiments.sheet import vertical_action, vertical_frequency
from experiments.spiral import model_rotation_curve
from experiments.thickness import power_weight_dispersion_ratio, softened_dispersion_ratio
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


#: The measured bias of the N-body origin rings for one baseline: a label and ``(alpha, ln ratio)`` points.
NbodyPoints = tuple[str, list[tuple[float, float]]]
#: Vertical scale of the arms of the N-body disk in disk scale heights, the measured 0.25 over 0.313 kpc.
ARM_THICKNESS: float = 0.8
#: Line styles and markers of the three baselines of the N-body test.
BASELINE_STYLES: tuple[str, ...] = ("-", "--", "-.")
BASELINE_MARKERS: tuple[str, ...] = ("s", "^", "D")


def _single_transient_panel(
    axes: Axes, series_a: list[tuple[float, float, float]], nbody: list[NbodyPoints], n_curve: int
) -> None:
    """Draw the analytic weights, the test particles and the N-body rings against the thinness alpha."""
    grid = np.linspace(0.1, 1.5, n_curve)
    curves = (
        ("-", r"$W \propto \sqrt{F}$", [trapping_dispersion_ratio(float(a), 1e-3) for a in grid]),
        ("--", r"$W \propto F$", [power_weight_dispersion_ratio(float(a), 1.0) for a in grid]),
        (
            "-.",
            rf"$W \propto F$, arm $h = {ARM_THICKNESS:g}$",
            [power_weight_dispersion_ratio(float(a), 1.0, ARM_THICKNESS) for a in grid],
        ),
    )
    for style, label, ratios in curves:
        axes.plot(grid, np.log(ratios), style, color="#000000", linewidth=1.5, label=label)
    # The store already holds the log dispersion ratio ln(sigma_mig/sigma_all) and its
    # standard error, so the points are plotted directly.
    axes.errorbar(
        [p[0] for p in series_a],
        [p[1] for p in series_a],
        yerr=[p[2] for p in series_a],
        fmt="o",
        color="#000000",
        markerfacecolor="white",
        markersize=5,
        capsize=3,
        label="test particles",
    )
    for index, (label, points) in enumerate(nbody):
        marker = BASELINE_MARKERS[index % len(BASELINE_MARKERS)]
        axes.plot([p[0] for p in points], [p[1] for p in points], marker, color="#000000", markersize=4, label=label)
    axes.set_xlabel(r"$\alpha$")
    axes.set_ylabel(r"$\ln\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$")


@figure("test-particle-bias")
def figure_test_particle(
    series_a: list[tuple[float, float, float]],
    series_b: list[tuple[float, float, float]],
    nbody: list[NbodyPoints] | None = None,
    n_curve: int = 60,
) -> Figure:
    """Plot the test-particle validation (two panels) from precomputed store data.

    The single-transient panel also carries the bias of the N-body origin rings for the
    same ``|dL_z|`` weight, placed at the ring's ``alpha = k z_0``, and the analytic
    weights of the two regimes; the legend of both panels is drawn in the
    resonance-overlap panel, which has the room for it.

    Parameters
    ----------
    series_a :
        Single-transient points ``(alpha, bias_mean, bias_err)``.
    series_b :
        Resonance-overlap points ``(count, bias_mean, bias_err)``.
    nbody :
        Per baseline, a label and the ``(alpha, ln ratio)`` of the N-body origin rings.
    n_curve :
        Number of points in the analytic curves.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    fig = Figure(figsize=(8.0, 3.5))
    left = fig.add_subplot(1, 2, 1)
    right = fig.add_subplot(1, 2, 2, sharey=left)
    _single_transient_panel(left, series_a, nbody or [], n_curve)
    right.errorbar(
        [p[0] for p in series_b],
        [p[1] for p in series_b],
        yerr=[p[2] for p in series_b],
        fmt="o",
        color="#000000",
        markerfacecolor="white",
        markersize=5,
        capsize=3,
    )
    right.set_xlabel(r"$M$")
    right.tick_params(labelleft=False)
    # The legend of both panels sits in the right one, which has the room for it.
    handles, labels = left.get_legend_handles_labels()
    right.legend(handles, labels, loc="lower left")
    return fig


#: Colormap of the origin rings of the N-body test.
RING_COLORMAP = "coolwarm"
#: The three selection rules of the N-body test with their model weights, as stored in the tables.
NBODY_RULES: tuple[tuple[str, str], ...] = (
    ("|dLz| weight", r"$|\Delta L_z|$ weight, model $F$"),
    ("dLz^2 weight", r"$(\Delta L_z)^2$ weight, model $F^2$"),
    ("|dLz| > L_*", r"$|\Delta L_z| > L_*$, model $\mathrm{erfc}(\lambda/F)$"),
)

NbodyTables = dict[str, Any]


def _ring_center(label: str) -> float:
    """Return the center of a ring from its ``inner to outer`` label."""
    inner, outer = (float(x) for x in label.split(" to "))
    return 0.5 * (inner + outer)


def _baseline_label(tables: NbodyTables) -> str:
    """Return the baseline of a test in Gyr as a legend label."""
    return f"{tables['meta']['baseline_gyr']:.2f} Gyr"


def _ring_edges(tables: NbodyTables) -> list[float]:
    """Return the radial edges of the origin rings, from the ``inner to outer`` labels."""
    bounds = [[float(x) for x in bins["ring"].split(" to ")] for bins in tables["bins"]]
    return [bounds[0][0]] + [outer for _, outer in bounds]


def _variance_panel(axes: Axes, tables: NbodyTables, colors: list[Any], legend: bool) -> None:
    """Draw the log of the normalized variance against the log of the normalized form factor of every ring.

    Both quantities are natural logarithms on linear axes, so the $F^2$ prediction is the
    line of slope 2 through the origin; it spans the range of the data and the legend names
    it.
    """
    for bins, color in zip(tables["bins"], colors):
        form, variance = bins["F"], bins["variance"]
        x = np.log(np.asarray(form) / form[-1])
        y = np.log(np.asarray(variance) / variance[-1])
        axes.plot(x, y, color=color, linewidth=1.5)
    x_min = min(np.log(bins["F"][0] / bins["F"][-1]) for bins in tables["bins"])
    axes.plot([x_min, 0.0], [2.0 * x_min, 0.0], "-", color="#000000", linewidth=2.0, label="$F^2$")
    if legend:
        axes.legend(loc="lower right")
    axes.text(0.05, 0.93, _baseline_label(tables), transform=axes.transAxes, ha="left", va="top")


@figure("nbody-variance")
def figure_nbody_variance(baselines: list[NbodyTables]) -> Figure:
    """Plot the variance of dLz against the layer form factor per origin ring, one panel per baseline.

    Both axes are normalized to the thinnest bin of each ring, so the $F^2$ law of the model
    is the same line for every ring and the panels test the exponent alone. The rings are
    colored by origin radius, with the color bar in the fourth panel.

    Parameters
    ----------
    baselines :
        Tables of the migration test, one per baseline, as written by ``nbody-migration``.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    edges = _ring_edges(baselines[0])
    cmap = colormaps[RING_COLORMAP]
    norm = BoundaryNorm(edges, cmap.N)
    colors = [cmap(norm(0.5 * (inner + outer))) for inner, outer in zip(edges[:-1], edges[1:])]
    fig = Figure(figsize=(8.0, 5.4))
    panels = fig.subplots(2, 2, sharex=True, sharey=True)
    # The color bar takes the top-right panel, so that the bottom row carries the x labels
    # and the shared axes leave no gap for labels between the rows.
    for index, (axes, tables) in enumerate(zip((panels[0, 0], panels[1, 0], panels[1, 1]), baselines)):
        _variance_panel(axes, tables, colors, legend=index == 0)
    for axes in (panels[0, 0], panels[1, 0]):
        axes.set_ylabel(r"$\ln \mathrm{Var}(\Delta L_z) / \mathrm{Var}_{\max}(\Delta L_z)$")
    for axes in (panels[1, 0], panels[1, 1]):
        axes.set_xlabel(r"$\ln F / F_{\max}$")
    spare = panels[0, 1]
    spare.axis("off")
    colorbar = fig.colorbar(
        ScalarMappable(norm=norm, cmap=cmap), cax=spare.inset_axes((0.2, 0.08, 0.1, 0.84)), ticks=edges
    )
    colorbar.set_label("$R_g$ (kpc)")
    return fig


@figure("nbody-exponents")
def figure_nbody_exponents(baselines: list[NbodyTables], thin: NbodyTables | None = None) -> Figure:
    """Plot the exponent of Var(dLz) against F and the spread of dLz per origin ring for every baseline.

    The spread is drawn as the variance of ``dLz`` in units of the squared angular momentum
    ``L_c = R_g V_c(R_g)`` of the circular orbit at the ring, on the model rotation curve.

    Parameters
    ----------
    baselines :
        Tables of the migration test with the layer form factor, one per baseline.
    thin :
        Tables of the same test with the razor-thin form factor, drawn for comparison.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    fig = Figure(figsize=(3.8, 5.6))
    top, bottom = fig.subplots(2, 1, sharex=True)
    curve = model_rotation_curve()
    for index, tables in enumerate(baselines):
        radii = np.array([_ring_center(row["ring"]) for row in tables["core"]])
        circular = radii * curve.at("v_circ", radii)
        style = BASELINE_STYLES[index % len(BASELINE_STYLES)]
        exponents = [row["exponent_F"] for row in tables["core"]]
        top.plot(radii, exponents, style, color="#000000", label=_baseline_label(tables))
        variance = np.array([row["sigma_dLz"] ** 2 for row in tables["core"]])
        bottom.plot(radii, variance / circular**2, style, color="#000000")
    if thin is not None:
        thin_radii = [_ring_center(row["ring"]) for row in thin["core"]]
        exponents = [row["exponent_F"] for row in thin["core"]]
        label = rf"$e^{{-k|z|}}$, {_baseline_label(thin)}"
        top.plot(thin_radii, exponents, "o", color="#000000", markerfacecolor="white", label=label)
    top.axhline(2.0, color="#808080", linestyle=":", linewidth=1.5)
    top.set_ylabel("$b$")
    top.legend()
    bottom.set_ylabel(r"$\mathrm{Var}(\Delta L_z)/L_c^2$")
    bottom.set_xlabel("$R_g$ (kpc)")
    return fig


def _label_panel(axes: Axes, label: str) -> None:
    """Write a panel label at the top left, adding headroom above the data so that nothing is covered."""
    low, high = axes.get_ylim()
    axes.set_ylim(low, high + 0.35 * (high - low))
    axes.text(0.03, 0.93, label, transform=axes.transAxes, ha="left", va="top")


@figure("nbody-rules")
def figure_nbody_rules(tables: NbodyTables) -> Figure:
    """Plot the measured and model dispersion ratios of the three selection rules against origin radius.

    Parameters
    ----------
    tables :
        Tables of the migration test for one baseline.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    fig = Figure(figsize=(3.8, 7.4))
    panels = fig.subplots(len(NBODY_RULES), 1, sharex=True)
    for axes, (rule, label) in zip(panels, NBODY_RULES):
        rows = [row for row in tables["rules"] if row["rule"] == rule]
        radii = [_ring_center(row["ring"]) for row in rows]
        axes.plot(radii, np.log([row["model_ratio"] for row in rows]), "-", color="#000000", label="model")
        axes.plot(radii, np.log([row["measured"] for row in rows]), "o", color="#000000", label="measured")
        axes.axhline(0.0, color="#808080", linestyle=":", linewidth=1.5)
        axes.set_ylabel(r"$\ln\sigma_{z,\mathrm{mig}}/\sigma_{z,\mathrm{all}}$")
        _label_panel(axes, label)
    panels[-1].set_xlabel("$R_g$ (kpc)")
    panels[0].legend(loc="upper right")
    return fig


@figure("nbody-destination")
def figure_nbody_destination(tables: NbodyTables) -> Figure:
    """Plot the dispersion of the arrivals over the non-migrators of the destination ring, inward and outward.

    Parameters
    ----------
    tables :
        Tables of the migration test for one baseline.

    Returns
    -------
    matplotlib.figure.Figure
        The built figure.
    """
    fig = Figure(figsize=(3.8, 5.6))
    panels = fig.subplots(2, 1, sharex=True)
    rows = tables["destination"]
    radii = [_ring_center(row["ring"]) for row in rows]
    for axes, direction in zip(panels, ("in", "out")):
        predicted_jz = [row[f"pred_Jz_{direction}"] for row in rows]
        predicted_ez = [row[f"pred_Ez_{direction}"] for row in rows]
        axes.plot(radii, np.log(predicted_jz), "-", color="#000000", label="$J_z$ conserved")
        axes.plot(radii, np.log(predicted_ez), "--", color="#000000", label=r"$\langle v_z^2 \rangle$ conserved")
        measured = np.log([row[f"measured_{direction}"] for row in rows])
        axes.plot(radii, measured, "o", color="#000000", label="measured")
        axes.axhline(0.0, color="#808080", linestyle=":", linewidth=1.5)
        axes.set_ylabel(r"$\ln\sigma_{z,\mathrm{arr}}/\sigma_{z,\mathrm{loc}}$")
        _label_panel(axes, "inward" if direction == "in" else "outward")
    panels[-1].set_xlabel("$R_g$ (kpc)")
    panels[1].legend(loc="upper right")
    return fig


def make_nbody_figures(baselines: list[NbodyTables], thin: NbodyTables | None = None) -> dict[str, Figure]:
    """Build and save the four figures of the N-body test from its cached tables.

    The rules and destination figures show the longest baseline.

    Parameters
    ----------
    baselines :
        Tables of the migration test with the layer form factor, one per baseline.
    thin :
        Tables of the same test with the razor-thin form factor, for the exponent figure.

    Returns
    -------
    dict[str, matplotlib.figure.Figure]
        Mapping from figure name to the built figure.
    """
    longest = max(baselines, key=lambda tables: float(tables["meta"]["baseline_gyr"]))
    return {
        "nbody-variance": figure_nbody_variance(baselines),
        "nbody-exponents": figure_nbody_exponents(baselines, thin),
        "nbody-rules": figure_nbody_rules(longest),
        "nbody-destination": figure_nbody_destination(longest),
    }


def make_all_figures(
    series_a: list[tuple[float, float, float]],
    series_b: list[tuple[float, float, float]],
    nbody: list[NbodyPoints] | None = None,
) -> dict[str, Figure]:
    """Build and save the analytic figure set to ``assets/figures``.

    Every figure is analytic except ``test-particle-bias``, which only *plots* the
    cached orbit-integration results passed in as ``series_a``/``series_b`` and the
    cached N-body points -- a cheap operation. The expensive steps that fill those
    caches are the separate ``test-particle-simulate`` and ``nbody-*`` commands; loading
    the caches is the caller's job (see the ``figures`` command), keeping this module
    free of the simulation machinery. The N-body figures are built by
    :func:`make_nbody_figures` from their own cache.

    Parameters
    ----------
    series_a :
        Cached single-transient points ``(alpha, bias_mean, bias_err)``.
    series_b :
        Cached overlap points ``(count, bias_mean, bias_err)``.
    nbody :
        Per baseline, a label and the ``(alpha, ln ratio)`` of the N-body origin rings.

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
        "test-particle-bias": figure_test_particle(series_a, series_b, nbody),
    }
