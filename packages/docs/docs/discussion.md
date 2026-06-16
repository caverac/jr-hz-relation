---
sidebar_position: 5
title: 6. Discussion
---

# 6. Discussion — how the pieces fit together

**Goal of this section.** Step back and see the whole argument as one structure,
distinguish it from a result it is often confused with, lay out the honest caveats,
and state the clean prediction that could falsify it.

## One object, three faces

The thread running through every section is a single analytic object — the **vertical
form factor** $F(k\,h_Z)$ — and three things that looked unrelated turn out to be tied
together by it. $F$ is the *common thread*, not the sole determinant of each: as noted
below, the bias magnitude and the slope each draw on their own additional physics.

1. **The provenance bias.** [Section 3](/theory/corotation-hamiltonian) showed $F$ is
   the exact vertical Fourier coefficient of the spiral at corotation (Equation 4), so
   the pendulum well that traps migrating stars is deeper for cold stars by exactly
   $\sqrt F$. That is the provenance bias at the single-resonance level — its origin;
   the observed magnitude additionally needs the regime physics of point 2.
2. **The vertical selectivity of capture.** [Section 4](/theory/resonance-overlap)
   showed the same $F$ controls when resonances overlap, so cold stars enter the
   diffusive churning regime first — the bias steepens from $F^{1/2}$ toward $F^2$.
3. **The spiral $J_R^{\max}$–$h_Z$ relation.** $F$ depends on wavenumber and thickness
   only through $\alpha=k\,h_Z$ — the same disk thickness that anchors the Palicio et
   al. (2024) relation. [Section 5](/results/provenance-bias) derives that relation's
   slope from a structural anisotropy factor $\pi G\Sigma/\kappa\,(\sigma_R/\sigma_z)^2$
   (the form factor does not enter the slope directly); $F$'s role is to select the
   cold-migrator population that defines $J_R^{\max}$, tying the two observables to one
   thickness. The model predicts the slope flattens with age.

What was *already known* going in: the radial twin of $F$ — the classical Daniel &
Wyse (2015) in-plane selectivity (our $G$-factor); the $e^{-k|z|}$ fall-off of a thin
spiral (Binney & Tremaine 2008); and the bias itself, seen in simulations (Vera-Ciro
et al. 2016; Mikkola et al. 2020). **What was missing — and what this paper supplies —
is the vertical extension** that turns the verbal "cold stars couple more readily"
into Equations 4–5 and connects it to the measured slope.

One thing $F$ is *not*: it should not be conflated with the finite-thickness
reduction factors of classical density-wave theory (Toomre 1964), which weaken a
self-gravitating disk's **collective** response to a density wave. $F$ is instead the
orbit-average of an *externally imposed* spiral felt by a **single** star at fixed
$J_z$ — a test-particle coupling, not a modification of the self-gravitating response.
Both involve the disk's vertical structure, but they act on different objects.

## Selectivity is not the same as fate

There is a closely related result that is easy to conflate with this one. Roškar et
al. (2013) showed, from conservation of the vertical action, that when a star migrates
*outward* its scale height grows as

$$
\frac{h_{Z,f}}{h_{Z,i}} = \exp\!\left(\frac{\Delta R}{2 R_d}\right),
$$

with $R_d$ the disk scale length. That law governs the **fate** of a star *after* it
has migrated — what happens to its vertical structure once it lands.

The form factor governs something different: the **selectivity** of capture — *which*
stars get picked up to migrate at all. The two are distinct and complementary, and
only the latter produces the provenance bias. Keeping them separate is important: a
population can be reshaped both by *who migrates* (selectivity) and by *what migration
does to them* (fate), and this paper is entirely about the former.

## The two regimes are two ends of one axis

The form factor distinguishes two dynamical regimes that are really the two limits of
a single weight $W(J_z)=F^p$:

- **Single-resonance trapping**, $p=1/2$ — the clean pendulum of
  [Section 3](/theory/corotation-hamiltonian). Floors the bias near $-7\%$ (weaker with
  finite arm thickness).
- **Resonance-overlap diffusion**, $p\to2$ — the inhomogeneous Balescu–Lenard
  description of secular evolution in tightly wound disks (Fouvry et al. 2015), whose
  linear-response complement is the perturbed distribution function of Monari, Famaey &
  Siebert (2016). Gives a near-parameter-free $-20$ to $-27\%$.

A fully rigorous treatment would compute $W(J_z)$ as the phase-space trapped fraction
*across* the overlap transition, rather than in its two limits as we do here — a
worthwhile but separate calculation, which we defer.

## Caveats — what bounds the calculation

Honesty about the limits of the argument:

- **Finite arm thickness.** The $e^{-k|z|}$ kernel is the razor-thin leading term; at
  the Galactic $\alpha\sim1$ the finite-thickness softening (Equation 2) is an
  order-unity correction. We carried it for an exponential arm profile; a
  self-consistent profile would refine the number but not the picture.
- **Pattern-speed separation.** The overlap parameter (Equation 8) depends on the
  bar–spiral pattern-speed gap. The well-separated values we adopted are
  *conservative*; the Milky Way's recurrent transient spirals add more resonances,
  which only *increases* the overlap and the bias.
- **The bias magnitude is not yet robustly measured.** Vera-Ciro et al. (2016)
  establish the cold-migrator preference *qualitatively* — there is no published
  migrator dispersion offset $\sigma_z^{\rm mig}/\sigma_z^{\rm all}$ to match against.
  Our conclusions therefore rest on the **regime ordering** — single-resonance
  trapping floors near $-7\%$, the diffusive regime predicts $-20$ to $-27\%$ — and on
  that qualitative cold-migrator preference, *not* on a precise value.

## The clean, testable prediction

The strongest forward-looking result is the **age-running of the slope**
(Equation 13): the $J_R^{\max}$–$h_Z$ relation should flatten with population age, with
exponent $2(\beta_R-\beta_z)\approx-0.3$, so an $8\,$Gyr population has roughly half
the slope of a $1\,$Gyr population. To our knowledge this is an **untested and clean
prediction** for current Gaia–APOGEE–LAMOST data: re-fit the relation in mono-age or
mono-abundance bins and read off $\beta_R-\beta_z$ directly from spiral-arm kinematics.

## Reproducibility

Every number and figure on these pages is produced by the open-source engine, with a
full test suite — see **[Using the library](/library/usage)**. Nothing here is a fit to
the simulations; the analytic chain runs from Laplace's equation
([Section 2](/theory/form-factor)) to the measurable slope
([Section 5](/results/provenance-bias)) with the spiral strength as the only physical
input, and that input lands inside its independently known range.
