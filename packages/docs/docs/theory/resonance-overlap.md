---
sidebar_position: 4
title: 4. Resonance overlap & diffusion
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# 4. Resonance overlap and the diffusive regime

**Goal of this section.** [Section 3](/theory/corotation-hamiltonian) showed that a
*single* corotation resonance floors the provenance bias near $-7\%$ — too weak to match
the simulations. Here we show that when several patterns (the bar **and** the spiral,
plus transient arms) are present, their trapping islands **overlap**, and the clean
pendulum trapping turns into **stochastic, diffusive** churning. Diffusion is steeper
in $F$, deepening the bias into a derived $\sim -20$ to $-27\%$ band. We test, with the
Chirikov criterion, that the Milky Way sits right at this transition — and that the
transition is itself biased toward cold stars.

## Step 1 — the island width as a fraction of radius

In [Section 3](/theory/corotation-hamiltonian) the trapping island had half-width
$\Delta p = 2\sqrt{\Psi/|g|}$ in the slow action $p=L_z-L_{\rm CR}$. To compare
islands from *different* patterns we need their widths in **radius**, $\Delta R$.

Take a flat rotation curve, $\Omega = V_c/R$ (the Milky Way is nearly flat). Two facts
follow for a circular orbit:

- Angular momentum is $L_z = R\,V_c$, so a shift in $L_z$ is a shift in radius:
  $\Delta L_z = V_c\,\Delta R$, i.e. $\Delta R = \Delta p/V_c$.
- The pendulum curvature is
  $$
  g = \frac{\mathrm{d}\Omega}{\mathrm{d}L_z}
  = \frac{\mathrm{d}}{\mathrm{d}L_z}\!\left(\frac{V_c^2}{L_z}\right)
  = -\frac{V_c^2}{L_z^2} = -\frac{1}{R^2},
  \qquad |g| = \frac{1}{R^2}.
  $$

Substitute $\Psi\simeq|\Phi_s|\,G\,F$ (Equation 4 of the paper, with $\Phi_0\to
|\Phi_s|$) and $|g|=1/R^2$ into $\Delta R = 2\sqrt{\Psi/|g|}/V_c$:

$$
\Delta R = \frac{2}{V_c}\sqrt{\Psi R^2} = \frac{2R}{V_c}\sqrt{|\Phi_s| G F}
\;\;\Longrightarrow\;\;
\boxed{\;\frac{\Delta R}{R} = 2\sqrt{\epsilon\,G\,F},\qquad
\epsilon\equiv\frac{|\Phi_s|}{V_c^2}\;}
$$

So the island is a **fixed fraction** of the corotation radius, set by the
dimensionless spiral strength $\epsilon$ (typically $1$–$3\%$) and — through $F$ — by
the star's vertical action. Hold on to that last point: $\Delta R\propto\sqrt{F}$.

## Step 2 — the Chirikov overlap criterion

Chirikov (1979) gave the universal rule of thumb for when isolated resonances merge
into chaos: **two resonances overlap when the sum of their half-widths exceeds their
separation.** For an inner pattern (corotation radius $R_{\rm in}$) and an outer one
($R_{\rm out}>R_{\rm in}$), define the **overlap parameter**

$$
S \equiv \frac{\Delta R_{\rm in} + \Delta R_{\rm out}}{R_{\rm out}-R_{\rm in}} ,
\qquad \text{overlap when } S\ge 1 .
$$

Rewrite it using radii expressed through the pattern speeds, $R=V_c/\Omega$ (so
$R_{\rm in}=V_c/\Omega_{\rm in}$, etc.). The numerator and denominator are

$$
\Delta R_{\rm in}+\Delta R_{\rm out} = 2\sqrt{\epsilon G F}\,(R_{\rm in}+R_{\rm out})
= 2\sqrt{\epsilon G F}\;V_c\,\frac{\Omega_{\rm in}+\Omega_{\rm out}}{\Omega_{\rm in}\Omega_{\rm out}},
$$

$$
R_{\rm out}-R_{\rm in} = V_c\!\left(\frac{1}{\Omega_{\rm out}}-\frac{1}{\Omega_{\rm in}}\right)
= V_c\,\frac{\Omega_{\rm in}-\Omega_{\rm out}}{\Omega_{\rm in}\Omega_{\rm out}} .
$$

The common factor $V_c/(\Omega_{\rm in}\Omega_{\rm out})$ cancels, leaving the clean
result (Equation 8 of the paper):

$$
\boxed{\;S = 2\sqrt{\epsilon\,G\,F}\;
\frac{\Omega_{\rm in}+\Omega_{\rm out}}{\Omega_{\rm in}-\Omega_{\rm out}} \;\ge\; 1\;}
$$

## Step 3 — is the Milky Way at the threshold? (plug in the numbers)

The two dominant patterns are the **bar** and the **spiral**:

| pattern | pattern speed $\Omega_p$ | corotation radius |
|---|---|---|
| bar (inner) | $\approx 38\;\mathrm{km\,s^{-1}\,kpc^{-1}}$ | $R_{\rm CR}\approx 6.0\;\mathrm{kpc}$ |
| spiral (outer) | $\approx 20\;\mathrm{km\,s^{-1}\,kpc^{-1}}$ | $R_{\rm CR}\approx 11.5\;\mathrm{kpc}$ |

The pattern-speed factor is

$$
\frac{\Omega_{\rm in}+\Omega_{\rm out}}{\Omega_{\rm in}-\Omega_{\rm out}}
= \frac{38+20}{38-20} = \frac{58}{18} \approx 3.22 .
$$

For a vertically cold mid-plane reference ($F=1$) and order-unity radial factor
($G\approx1$), $S = 2\sqrt{\epsilon}\times 3.22$. Evaluating across the physical
spiral-strength band:

$$
S(\epsilon{=}0.01)=0.64,\qquad S(\epsilon{=}0.02)=0.91,\qquad S(\epsilon{=}0.03)=1.12 .
$$

So at the physical spiral strength $|\Phi_s|\sim1$–$3\%\,V_c^2$, **the bar and spiral
corotation resonances sit right at the overlap threshold $S\sim1$** (the mechanism of
Minchev & Famaey 2010). The Milky Way is poised exactly at the boundary between clean
trapping and diffusive churning.

## Step 4 — the transition is itself biased toward cold stars

Here is the crucial twist. Because $\Delta R\propto\sqrt F$, the overlap parameter
inherits the vertical dependence:

$$
S \propto \sqrt{F(J_z,k)} .
$$

So **vertically cold stars (large $F$) have wider islands and cross the overlap
threshold first.** At the fiducial parameters, the cold population ($F=1$) overlaps at
$\epsilon\approx 0.024$ — inside the physical band — while a hotter population
($F=0.5$) stays in regular libration until $\epsilon\approx 0.05$:

$$
2\sqrt{0.024\times 1}\times 3.22 \approx 1.00, \qquad
2\sqrt{\epsilon\times 0.5}\times 3.22 = 1 \;\Rightarrow\; \epsilon\approx 0.048 .
$$

<figure class="scientific">
  <img src={useBaseUrl('/figures/resonance-overlap.png')} alt="Chirikov overlap parameter versus spiral strength for cold and hot stars" />
</figure>

*__Overlap is vertical-action selective.__ The Chirikov parameter $S$ of the
bar+spiral corotation resonances versus spiral strength $\epsilon$, for cold ($F=1$)
and hot ($F=0.5$) stars. Overlap (diffusive churning) sets in at $S=1$. Cold stars
cross first; within the physical strength band (shaded), only the cold population is in
the diffusive regime.*

The diffusive channel is therefore *itself* biased toward cold stars, steepening the
provenance bias beyond the single-resonance $F^{1/2}$ law toward the diffusive $F^2$
law (derived next). The Milky Way lives at a crossover that is vertical-action
selective — exactly the ingredient missing from the single-resonance estimate.

## Step 5 — one weight that spans both regimes

The two regimes are limits of a single migration weight.

- **Trapping limit** (no overlap): from
  [Section 3](/theory/corotation-hamiltonian), $W\propto F^{1/2}$.
- **Diffusive limit** (overlap): quasilinear churning gives an angular-momentum
  diffusion coefficient $D\propto|\Psi|^2\propto F^2$ (it depends on the *square* of
  the coupling), so $W\propto F^2$.

Model the exponent as running smoothly from $1/2$ to $2$ through a gate centered
on the overlap threshold $S=1$ (Equation 9 of the paper):

$$
\boxed{\;W(J_z)=F^{\,p},\qquad p=\frac{1}{2}+\frac{3}{2}\,\frac{S^2}{1+S^2},\qquad
S(J_z)=S_0\sqrt{F(J_z,k)}\;}
$$

with the one physical parameter $S_0$ the effective overlap. Read off the limits of
the gate $S^2/(1+S^2)$:

- $S\to0$: $p\to1/2$ — pure trapping.
- $S\to\infty$: $p\to 2$ — pure diffusion.
- $S=1$ (threshold): $p=1/2+3/4=5/4$ — halfway.

The crossover happens at the **critical form factor** $F_{\rm crit}=1/S_0^2$ (where
$S=1$): a critical vertical action separating diffusive (cold) migrators from confined
(hot) ones — a structural prediction.

<figure class="scientific">
  <img src={useBaseUrl('/figures/crossover-bias.png')} alt="Provenance bias from the crossover weight versus effective overlap" />
</figure>

*__The bias deepens with overlap.__ Provenance bias $\ln\sigma_z^{\rm mig}/\sigma_z^{\rm all}$
from the crossover weight at the Milky-Way thickness, versus effective overlap $S_0$. It
deepens from the $\sqrt F$ value ($\approx -7\%$) to the $F^2$ value ($\approx -27\%$).
The bar+spiral alone ($S_0\approx1$, shaded) gives $\approx -11\%$; the observed
$\sim-22\%$ is reached at $S_0\approx 2$–$3$, the extra overlap expected once the Milky
Way's recurrent transient spirals are added.*

## Step 6 — the diffusive endpoint is not assumed, it is derived

The $F^2$ ceiling is not a guess; it follows from kinetic theory. The inhomogeneous
**Balescu–Lenard** equation describes secular evolution of a self-gravitating disk by
resonant relaxation. Its angular-momentum diffusion coefficient is

$$
D_{L_z}(J) = \pi\sum_m |\Psi_m(J)|^2\,C_m(\Omega) ,
$$

(Heyvaerts 2010; Fouvry, Pichon & Magorrian 2015), which inherits the
$|\Psi_m|^2\propto F^2$ of the corotation coupling (Equation 4) — so the bare
diffusive weight is $W\propto F^2$.

One refinement: a trapped star librates with a finite frequency width
$\Delta\omega\propto\sqrt{\Psi}\propto\sqrt{F}$, which **broadens the resonance**
(Dupree 1966). For a Lorentzian spiral spectrum of width $W_s$ this broadening gives a
closed form (Equation 10 of the paper):

$$
\boxed{\;W(J_z)=\frac{F^2}{1+b\sqrt F},\qquad b=\frac{\Delta\omega}{W_s}\;}
$$

with limits you can read directly:

- $b\to0$ (sharp resonances): $W\to F^2$ — the decorrelated quasilinear limit.
- $b\to\infty$ (broad resonances): $W\to F^2/(b\sqrt F)\propto F^{3/2}$ — the
  coherent, resonance-broadened limit.

<figure class="scientific">
  <img src={useBaseUrl('/figures/balescu-lenard.png')} alt="Provenance bias from the Balescu-Lenard weight versus broadening" />
</figure>

*__A narrow, parameter-free band.__ Provenance bias from the Balescu–Lenard weight at
the Milky-Way thickness, versus the resonance-broadening parameter $b$. Because the
exponent only moves between $F^2$ and $F^{3/2}$, the diffusive bias is pinned to
$\approx -20$ to $-27\%$ — nearly independent of $b$, with __no tuned parameter.__ The
observed bias follows simply from the disk being in the diffusive regime.*

This is the strongest statement in the paper: *the size of the provenance bias is a
near-parameter-free consequence of the disk being in the overlap (diffusive) regime.*
The crossover weight of Step 5 bridges the derived $\sqrt F$ value ($\approx-7\%$) and
this derived diffusive band ($\approx-20$ to $-27\%$).

## Step 7 — a clean check: test particles, no analytic input

Finally, the whole mechanism is confirmed by brute-force orbit integration with **no
analytic input at all**. Integrate $\sim3000$ test particles in a realistic Galactic
potential (`MWPotential2014`; Bovy 2015) plus an imposed transient spiral that falls
off vertically over a scale height $H$, and weight each star by how much angular
momentum it churned, $|\Delta L_z|$.

<figure class="scientific wide">
  <img src={useBaseUrl('/figures/test-particle-bias.png')} alt="Test-particle validation of the provenance bias" />
</figure>

*__Test-particle validation__ (seed-averaged; error bars are the standard error).
__Left:__ a single transient spiral — the churning-weighted migrator coldness rises
with spiral thinness $\alpha\sim z_0/H$, tracking the analytic single-resonance
prediction (curve) and reaching $\approx6\%$ near the Galactic $\alpha\sim1$.
__Right:__ stacking $M$ overlapping patterns of different pattern speed raises the bias
monotonically — a direct confirmation of the resonance-overlap mechanism.*

Both predictions come out: migrators are vertically colder, the single-resonance bias
matches the $\sqrt F$ analytics and its magnitude, and *overlapping* patterns push the
bias up exactly as the diffusive argument requires.

:::tip What to carry forward
The Milky Way sits at the Chirikov overlap threshold ($S\sim1$), and the threshold is
crossed first by cold stars. Overlap turns trapping ($W\propto F^{1/2}$) into
diffusion ($W\propto F^2$), and the diffusive bias is a near-parameter-free
$\sim-20$ to $-27\%$. [Section 5](/results/provenance-bias) turns this into the observable
bias magnitude and the $J_R^{\max}$–$h_Z$ slope.
:::
