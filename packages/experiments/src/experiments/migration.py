r"""Test the form-factor prediction for migration between two orbit windows of a run.

The inputs are the per-particle summaries of an origin and a later window
(:mod:`experiments.windows`) and the spiral measurements (:mod:`experiments.spiral`). Each
disk particle gets an origin ring from the guiding radius $R_g(L_z)$ of the origin window on
the model rotation curve, and $\Delta L_z$ is the change of its window-mean angular momentum.
In every origin ring the test reports (the form factor is the razor-thin
$\langle e^{-k|z|}\rangle$ or, by default, the layer factor of :mod:`experiments.windows`):

1. the core test: the variance of $\Delta L_z$ in quantile bins of the form factor $F$ at the
   ring's wavenumber, the exponent $b$ of $\mathrm{Var}(\Delta L_z) \propto F^b$ (the
   prediction is $b = 2$), the exponent against $\langle|z|\rangle$ instead, the excess
   kurtosis and the mean of $\Delta L_z$, and the median relative changes of $J_R$ and $J_z$
   of the migrators against the rest; across rings, the scatter of the normalized variance
   about one power law in $F$ and about one in $\langle|z|\rangle$ says on which variable the
   rings collapse;
2. the bias per selection rule: $\sigma_{z,\rm mig}/\sigma_{z,\rm all}$ in the origin ring for
   the weights $|\Delta L_z|$ and $(\Delta L_z)^2$ and for the threshold $|\Delta L_z| > L_*$ at
   a quantile, next to the model values from reweighting the same particles by $F$, $F^2$ and
   $\mathrm{erfc}(\lambda/F)$ with $\lambda = L_*/\sqrt{2V_1}$, where $V_1$ is the variance
   of $\Delta L_z$ extrapolated to $F = 1$ with the exponent fixed at 2, plus the trapping
   weight $\sqrt F$, which has no measured counterpart;
3. inward against outward: the $J_z$ of the two groups at the origin (medians and the
   Kolmogorov-Smirnov distance), and at every destination ring the vertical dispersion of the
   arrivals relative to the non-migrators there, measured and predicted with $J_z$ conserved
   ($\langle v_z^2\rangle = J_z \nu_z$ with the arrival's own period at the destination) and
   with $\langle v_z^2\rangle$ conserved.

A sweep of the wavenumber of $F$ over the stored grid gives the exponent $b_k$ for every
$k$; a flat product $b_k k$ means that the variance follows $\exp(-2k_{\rm eff}\langle|z|\rangle)$
with one effective wavenumber, the signature that led to the layer form factor.

A dispersion is the root mean square over particles of the window mean of $v_z^2$. Migrators
are the particles with $|\Delta L_z| > L_*$, outward when the guiding radius grew. Units are
those of the run: kpc, km/s and kpc/(km/s) for time.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.stats import norm

from experiments._constants import TIME_UNIT_GYR
from experiments.spiral import Z_DISK, WindowModes, combined_wavenumber

F64 = npt.NDArray[np.float64]
B = npt.NDArray[np.bool_]
Row = dict[str, float | int | str]
Tables = dict[str, Any]

#: Default origin rings, quantile bins of F and migrator quantile.
RINGS_SPEC = "3:12:1"
F_BINS = 8
QUANTILE = 0.9


@dataclass(frozen=True)
class Spiral:
    """The rotation curve of the model and the modes of one spiral window."""

    rc_radius: F64
    v_circ: F64
    edges: F64  # ring edges of the ring sums
    modes: WindowModes
    harmonics: list[int]

    def guiding_radius(self, lz: F64) -> F64:
        """Return the radius of the circular orbit with the given angular momentum."""
        return np.asarray(np.interp(np.abs(lz), self.rc_radius * self.v_circ, self.rc_radius))

    def ring_wavenumber(self, bounds: tuple[float, float]) -> float:
        """Return the combined |k| of the chosen harmonics in a ring."""
        return combined_wavenumber(self.modes, self.edges, self.harmonics, bounds)


@dataclass(frozen=True)
class WindowValues:
    """Per-particle quantities of the disk sample in one window."""

    lz: F64
    r_g: F64
    abs_z: F64
    vz2: F64
    j_z: F64
    t_z: F64
    j_r: F64

    @classmethod
    def load(cls, path: Path, spiral: Spiral, form_key: str) -> tuple[WindowValues, F64, F64, float]:
        """Load the disk rows of a window summary; also return the form factors, the k grid and the start."""
        data = np.load(path)
        rows = slice(0, int(data["disk_rows"]))
        lz = np.asarray(data["lz"][rows], dtype=np.float64)
        values = cls(
            lz=lz,
            r_g=spiral.guiding_radius(lz),
            abs_z=np.asarray(data["abs_z"][rows], dtype=np.float64),
            vz2=np.asarray(data["vz2"][rows], dtype=np.float64),
            j_z=np.asarray(data["j_z"][rows], dtype=np.float64),
            t_z=np.asarray(data["t_z"][rows], dtype=np.float64),
            j_r=np.asarray(data["j_r"][rows], dtype=np.float64),
        )
        form = np.asarray(data[form_key][rows], dtype=np.float64)
        return values, form, np.asarray(data["k_grid"], dtype=np.float64), float(data["times"][0])


@dataclass(frozen=True)
class Particles:
    """The disk sample in the origin and the later window, with the origin form factors."""

    origin: WindowValues
    later: WindowValues
    form: F64  # (particles, wavenumbers), origin window
    k_grid: F64
    starts: tuple[float, float]  # first snapshot time of each window

    @property
    def delta_lz(self) -> F64:
        """Change of the window-mean angular momentum."""
        return np.asarray(self.later.lz - self.origin.lz)

    @property
    def outward(self) -> B:
        """Particles whose guiding radius grew."""
        return np.asarray(self.later.r_g > self.origin.r_g)

    @property
    def baseline(self) -> float:
        """Time between the two windows, in run units."""
        return self.starts[1] - self.starts[0]

    def form_at(self, k: float) -> F64:
        """Interpolate the form factor of every particle at one wavenumber, held at the ends of the grid."""
        k = float(np.clip(k, self.k_grid[0], self.k_grid[-1]))
        upper = int(np.clip(np.searchsorted(self.k_grid, k), 1, len(self.k_grid) - 1))
        weight = (k - self.k_grid[upper - 1]) / (self.k_grid[upper] - self.k_grid[upper - 1])
        return np.asarray((1.0 - weight) * self.form[:, upper - 1] + weight * self.form[:, upper])


@dataclass(frozen=True)
class Ring:
    """One origin ring with its selection, form factors and migration threshold."""

    inner: float
    outer: float
    k: float
    selected: B
    form: F64  # of the selected particles
    delta_lz: F64  # of the selected particles
    l_star: float

    @property
    def label(self) -> str:
        """Ring bounds as text."""
        return f"{self.inner:g} to {self.outer:g}"

    @property
    def migrating(self) -> B:
        """Selected particles that migrated."""
        return np.asarray(np.abs(self.delta_lz) > self.l_star)


def load_particles(origin: Path, later: Path, spiral: Spiral, form_key: str) -> Particles:
    """Load the disk rows of the two window summaries."""
    first, form, k_grid, start = WindowValues.load(origin, spiral, form_key)
    second, _, later_grid, later_start = WindowValues.load(later, spiral, form_key)
    if not np.array_equal(k_grid, later_grid):
        raise ValueError("the two windows use different wavenumber grids")
    return Particles(first, second, form, k_grid, (start, later_start))


def parse_harmonics(spec: str, amplitude: F64, centers: F64) -> list[int]:
    """Expand the harmonic spec: ``0`` the strongest in 3 to 12 kpc, ``m`` one harmonic, ``a:b`` the range to b - 1."""
    if ":" in spec:
        first, last = (int(x) for x in spec.split(":"))
        return list(range(first, last))
    m = int(spec)
    if m > 0:
        return [m]
    band = (centers >= 3.0) & (centers <= 12.0)
    return [int(np.argmax(amplitude[:, band].mean(axis=1))) + 1]


def load_spiral(path: Path, window: int, spec: str) -> Spiral:
    """Load the rotation curve and the modes of one spiral window, with the chosen harmonics."""
    data = np.load(path)
    amplitude = np.asarray(data["amplitude"][window], dtype=np.float64)
    edges = np.asarray(data["edges"], dtype=np.float64)
    harmonics = parse_harmonics(spec, amplitude, 0.5 * (edges[:-1] + edges[1:]))
    modes = WindowModes(
        bounds=(float(data["window_bounds"][window][0]), float(data["window_bounds"][window][1])),
        amplitude=amplitude,
        wavenumber=np.asarray(data["wavenumber"][window], dtype=np.float64),
        coherence=np.asarray(data["coherence"][window], dtype=np.float64),
        epsilon=np.asarray(data["epsilon"][window], dtype=np.float64),
        spectrogram=np.asarray(data["spectrogram"][window], dtype=np.float64),
    )
    return Spiral(
        rc_radius=np.asarray(data["rc_radius"], dtype=np.float64),
        v_circ=np.asarray(data["v_circ"], dtype=np.float64),
        edges=edges,
        modes=modes,
        harmonics=harmonics,
    )


def make_ring(particles: Particles, spiral: Spiral, bounds: tuple[float, float], quantile: float) -> Ring:
    """Select the particles whose origin guiding radius falls in the ring."""
    k = spiral.ring_wavenumber(bounds)
    form = particles.form_at(k)
    r_g = particles.origin.r_g
    selected = (r_g >= bounds[0]) & (r_g < bounds[1]) & np.isfinite(form)
    delta_lz = particles.delta_lz[selected]
    l_star = float(np.quantile(np.abs(delta_lz), quantile))
    return Ring(bounds[0], bounds[1], k, selected, form[selected], delta_lz, l_star)


def quantile_bins(key: F64, n_bins: int) -> npt.NDArray[np.int64]:
    """Return the bin index of every value in quantile bins of the key."""
    edges = np.quantile(key, np.linspace(0.0, 1.0, n_bins + 1))
    return np.asarray(np.clip(np.searchsorted(edges, key, side="right") - 1, 0, n_bins - 1), dtype=np.int64)


def binned_mean(index: npt.NDArray[np.int64], values: F64, n_bins: int) -> F64:
    """Return the mean of the values in each bin."""
    count = np.bincount(index, minlength=n_bins).astype(np.float64)
    return np.asarray(np.bincount(index, weights=values, minlength=n_bins) / count)


def binned_variance(key: F64, values: F64, n_bins: int) -> tuple[F64, F64, F64]:
    """Return the mean of the key, the variance of the values and the count in quantile bins of the key."""
    index = quantile_bins(key, n_bins)
    count = np.bincount(index, minlength=n_bins).astype(np.float64)
    mean_key = binned_mean(index, key, n_bins)
    variance = binned_mean(index, values**2, n_bins) - binned_mean(index, values, n_bins) ** 2
    return mean_key, variance, count


def positive(x: F64, y: F64) -> B:
    """Flag the points with finite, positive coordinates, the only ones a log fit can use."""
    return np.asarray(np.isfinite(x) & np.isfinite(y) & (x > 0.0) & (y > 0.0))


def power_law_fit(x: F64, y: F64, weights: F64, slope: float | None = None) -> tuple[float, float]:
    """Fit log y = a + b log x by weighted least squares; a given slope fixes b and fits a alone.

    Points with a nonpositive coordinate (an empty bin, a variance lost to rounding) are
    left out; with fewer than two points left the fit is NaN.
    """
    good = positive(x, y)
    if good.sum() < 2:
        return float("nan"), float("nan")
    log_x, log_y, weights = np.log(x[good]), np.log(y[good]), weights[good]
    if slope is None:
        slope = float(np.cov(log_x, log_y, aweights=weights)[0, 1] / np.cov(log_x, aweights=weights))
    intercept = float(np.average(log_y - slope * log_x, weights=weights))
    return slope, intercept


def kurtosis(values: F64) -> float:
    """Return the excess kurtosis."""
    centered = values - values.mean()
    return float(np.mean(centered**4) / np.mean(centered**2) ** 2 - 3.0)


def median_relative_change(before: F64, after: F64, mask: B) -> float:
    """Return the median of (after - before) / before over the masked particles with both finite."""
    finite = mask & np.isfinite(before) & np.isfinite(after) & (before > 0.0)
    return safe_median((after[finite] - before[finite]) / before[finite])


@dataclass(frozen=True)
class CoreResult:
    """The core-test row of a ring and its bins for the collapse test."""

    row: Row
    f_bins: F64
    z_bins: F64  # mean |z| in the F bins
    normalized: F64  # variance in the F bins over the ring variance
    variance: F64  # variance in the F bins
    count: F64  # particles in the F bins

    def record(self) -> dict[str, object]:
        """Return the bins of the ring as plain lists, for the JSON output."""
        return {
            "ring": self.row["ring"],
            "F": self.f_bins.tolist(),
            "abs_z": self.z_bins.tolist(),
            "variance": self.variance.tolist(),
            "count": self.count.tolist(),
        }


def action_changes(ring: Ring, particles: Particles) -> Row:
    """Return the median relative changes of J_R and J_z of the migrators and of the rest of a ring."""
    row: Row = {}
    for name in ("j_r", "j_z"):
        before = np.asarray(getattr(particles.origin, name)[ring.selected])
        after = np.asarray(getattr(particles.later, name)[ring.selected])
        row[f"d{name}_mig"] = median_relative_change(before, after, ring.migrating)
        row[f"d{name}_rest"] = median_relative_change(before, after, ~ring.migrating)
    return row


def core_test(ring: Ring, particles: Particles, n_bins: int) -> CoreResult:
    """Fit the variance of dLz against F and against |z| in a ring and compare the actions of migrators."""
    abs_z = particles.origin.abs_z[ring.selected]
    f_bins, f_var, f_count = binned_variance(ring.form, ring.delta_lz, n_bins)
    z_bins, z_var, z_count = binned_variance(abs_z, ring.delta_lz, n_bins)
    row: Row = {
        "ring": ring.label,
        "n": int(ring.selected.sum()),
        "k": ring.k,
        "exponent_F": power_law_fit(f_bins, f_var, f_count)[0],
        "exponent_z": power_law_fit(z_bins, z_var, z_count)[0],
        "sigma_dLz": float(np.std(ring.delta_lz)),
        "mean_dLz": float(np.mean(ring.delta_lz)),
        "kurtosis": kurtosis(ring.delta_lz),
        "L_star": ring.l_star,
    }
    row.update(action_changes(ring, particles))
    z_at_f = binned_mean(quantile_bins(ring.form, n_bins), abs_z, n_bins)
    return CoreResult(row, f_bins, z_at_f, f_var / np.var(ring.delta_lz), f_var, f_count)


def dispersion_ratio(vz2: F64, weights: F64) -> float:
    """Return the root of the weighted over the unweighted mean of v_z^2."""
    return float(np.sqrt(np.average(vz2, weights=weights) / np.mean(vz2)))


def sigma_at_unit_form(ring: Ring, n_bins: int) -> float:
    """Return the dispersion of dLz extrapolated to F = 1 with Var(dLz) proportional to F^2."""
    f_bins, f_var, f_count = binned_variance(ring.form, ring.delta_lz, n_bins)
    return float(np.exp(0.5 * power_law_fit(f_bins, f_var, f_count, slope=2.0)[1]))


def rule_rows(ring: Ring, particles: Particles, n_bins: int) -> list[Row]:
    """Return the measured and model dispersion ratios of the three selection rules, and the trapping model."""
    sigma_1 = sigma_at_unit_form(ring, n_bins)
    lam = ring.l_star / (np.sqrt(2.0) * sigma_1)
    vz2 = particles.origin.vz2[ring.selected]
    threshold_model = 2.0 * norm.sf(ring.l_star / (sigma_1 * ring.form))  # erfc(lambda / F)
    pairs = [
        ("|dLz| weight", np.abs(ring.delta_lz), "F", ring.form),
        ("dLz^2 weight", ring.delta_lz**2, "F^2", ring.form**2),
        ("|dLz| > L_*", ring.migrating.astype(np.float64), "erfc(lambda/F)", threshold_model),
        ("trapping (no overlap)", np.full(len(vz2), np.nan), "sqrt(F)", np.sqrt(ring.form)),
    ]
    rows: list[Row] = []
    for name, weight, label, model in pairs:
        measured = float("nan") if np.isnan(weight).any() else dispersion_ratio(vz2, weight)
        rows.append({"ring": ring.label, "rule": name, "measured": measured, "model": label})
        rows[-1]["model_ratio"] = dispersion_ratio(vz2, model)
    rows.append({"ring": ring.label, "rule": "sigma_1, lambda", "measured": sigma_1, "model": "", "model_ratio": lam})
    return rows


def ks_distance(a: F64, b: F64) -> float:
    """Return the Kolmogorov-Smirnov distance between two samples."""
    pooled = np.sort(np.concatenate([a, b]))
    cdf_a = np.searchsorted(np.sort(a), pooled, side="right") / len(a)
    cdf_b = np.searchsorted(np.sort(b), pooled, side="right") / len(b)
    return float(np.max(np.abs(cdf_a - cdf_b)))


def safe_median(values: F64) -> float:
    """Return the median of a sample, NaN when empty."""
    return float(np.median(values)) if len(values) else float("nan")


def origin_row(ring: Ring, particles: Particles) -> Row:
    """Compare the origin J_z of inward and outward migrators of a ring."""
    j_z = particles.origin.j_z[ring.selected]
    outward = particles.outward[ring.selected]
    inward_j = j_z[ring.migrating & ~outward & np.isfinite(j_z)]
    outward_j = j_z[ring.migrating & outward & np.isfinite(j_z)]
    both = bool(len(inward_j) and len(outward_j))
    return {
        "ring": ring.label,
        "n_in": len(inward_j),
        "n_out": len(outward_j),
        "median_Jz_all": safe_median(j_z[np.isfinite(j_z)]),
        "median_Jz_in": safe_median(inward_j),
        "median_Jz_out": safe_median(outward_j),
        "ks_in_out": ks_distance(inward_j, outward_j) if both else float("nan"),
    }


def finite_mean(values: F64) -> float:
    """Return the mean of the finite values, NaN when there is none."""
    finite = values[np.isfinite(values)]
    return float(np.mean(finite)) if len(finite) else float("nan")


def destination_row(particles: Particles, migrating: B, bounds: tuple[float, float]) -> Row:
    """Compare the arrivals in a destination ring with the non-migrators there."""
    there = (particles.later.r_g >= bounds[0]) & (particles.later.r_g < bounds[1])
    locals_vz2 = finite_mean(particles.later.vz2[there & ~migrating])
    row: Row = {"ring": f"{bounds[0]:g} to {bounds[1]:g}", "n_local": int((there & ~migrating).sum())}
    groups = (("in", there & migrating & ~particles.outward), ("out", there & migrating & particles.outward))
    for label, group in groups:
        conserved_jz = particles.origin.j_z[group] * 2.0 * np.pi / particles.later.t_z[group]
        row[f"n_{label}"] = int(group.sum())
        row[f"measured_{label}"] = float(np.sqrt(finite_mean(particles.later.vz2[group]) / locals_vz2))
        row[f"pred_Jz_{label}"] = float(np.sqrt(finite_mean(conserved_jz) / locals_vz2))
        row[f"pred_Ez_{label}"] = float(np.sqrt(finite_mean(particles.origin.vz2[group]) / locals_vz2))
    return row


def format_table(title: str, rows: list[Row], digits: int = 3) -> list[str]:
    """Format rows that share their keys as a markdown table."""
    lines = [f"\n### {title}\n"]
    keys = list(rows[0])
    lines.append("| " + " | ".join(keys) + " |")
    lines.append("|" + "---|" * len(keys))
    for row in rows:
        cells = (f"{v:.{digits}f}" if isinstance(v, float) else str(v) for v in row.values())
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def collapse_scatter(results: list[CoreResult]) -> dict[str, float]:
    """Return the rms residual of the log normalized variance about one power law in F and one in |z|."""
    variance = np.concatenate([r.normalized for r in results])
    weights = np.ones_like(variance)
    scatter = {}
    for name, key in (
        ("F", np.concatenate([r.f_bins for r in results])),
        ("z", np.concatenate([r.z_bins for r in results])),
    ):
        slope, intercept = power_law_fit(key, variance, weights)
        good = positive(key, variance)
        residual = np.log(variance[good]) - intercept - slope * np.log(key[good])
        scatter[name] = float(np.sqrt(np.mean(residual**2)))
    return scatter


def wavenumber_sweep(particles: Particles, rings: list[Ring], n_bins: int) -> list[Row]:
    """Return, per ring, the exponent of Var(dLz) against F_k for every wavenumber of the grid."""
    rows: list[Row] = []
    for ring in rings:
        row: Row = {"ring": ring.label}
        for index, k in enumerate(particles.k_grid):
            f_bins, f_var, f_count = binned_variance(particles.form[ring.selected, index], ring.delta_lz, n_bins)
            row[f"k={k:g}"] = power_law_fit(f_bins, f_var, f_count)[0]
        rows.append(row)
    return rows


def parse_rings(spec: str) -> list[tuple[float, float]]:
    """Expand ``inner:outer:width`` into ring bounds."""
    inner, outer, width = (float(x) for x in spec.split(":"))
    edges = np.arange(inner, outer + 0.5 * width, width)
    return [(float(a), float(b)) for a, b in zip(edges[:-1], edges[1:])]


def run(particles: Particles, rings: list[Ring], bounds: list[tuple[float, float]], n_bins: int) -> Tables:
    """Run the three comparisons and return their tables."""
    results = [core_test(ring, particles, n_bins) for ring in rings]
    migrating = np.zeros(len(particles.origin.lz), dtype=bool)
    for ring in rings:
        migrating[ring.selected] = ring.migrating
    return {
        "meta": {
            "origin_start": particles.starts[0],
            "later_start": particles.starts[1],
            "baseline": particles.baseline,
            "baseline_gyr": particles.baseline * TIME_UNIT_GYR,
        },
        "core": [r.row for r in results],
        "bins": [r.record() for r in results],
        "collapse": collapse_scatter(results),
        "rules": [row for ring in rings for row in rule_rows(ring, particles, n_bins)],
        "origin": [origin_row(ring, particles) for ring in rings],
        "destination": [destination_row(particles, migrating, b) for b in bounds],
    }


def report(tables: Tables) -> list[str]:
    """Format every table of a test as markdown."""
    lines = format_table("Core test per origin ring", tables["core"])
    scatter = tables["collapse"]
    lines.append(
        f"\ncollapse across rings: rms log residual {scatter['F']:.3f} about a power law in F, "
        f"{scatter['z']:.3f} about one in |z|"
    )
    lines += format_table("Bias per selection rule (sigma_z,mig / sigma_z,all at the origin)", tables["rules"])
    lines += format_table("Inward against outward at the origin", tables["origin"])
    lines += format_table("Arrivals against non-migrators at the destination (sigma_z ratios)", tables["destination"])
    if "sweep" in tables:
        lines += format_table("Exponent of Var(dLz) against F_k for every k of the grid", tables["sweep"], 2)
        products: list[Row] = []
        for row in tables["sweep"]:
            products.append({key: (value * float(key[2:]) if key != "ring" else value) for key, value in row.items()})
        lines += format_table("The product b_k k (flat when one effective wavenumber describes the ring)", products, 2)
    return lines


def save_tables(path: Path, tables: Tables) -> None:
    """Write the tables as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tables, indent=2), encoding="ascii")


def load_tables(path: Path) -> Tables:
    """Read the tables written by :func:`save_tables`."""
    loaded: Tables = json.loads(path.read_text(encoding="ascii"))
    return loaded


def bias_points(tables: Tables, rule: str = "|dLz| weight", scale_height: float = Z_DISK) -> list[tuple[float, float]]:
    """Return (alpha, ln ratio) per origin ring for one selection rule, with alpha the ring's k times the disk scale.

    These are the points that the test-particle figure overlays on its analytic curves.
    """
    measured = {str(row["ring"]): float(row["measured"]) for row in tables["rules"] if row["rule"] == rule}
    return [(float(row["k"]) * scale_height, float(np.log(measured[str(row["ring"])]))) for row in tables["core"]]
