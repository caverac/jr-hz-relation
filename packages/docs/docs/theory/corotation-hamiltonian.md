---
sidebar_position: 3
title: 3. The corotation-resonant Hamiltonian
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# 3. The corotation-resonant Hamiltonian and the trapped weight

**Goal of this section.** This is the conceptual core. We show that the form factor
$F$ from [Section 2](/theory/form-factor) is *not* an inserted weight but the **exact
vertical coupling** of the spiral at corotation. We then reduce the resonance to a
**pendulum**, read off which stars get trapped (and migrate), and compute the
resulting provenance bias. The punchline: a single arm can only produce a modest
$\sim -7\%$ bias — which forces us into the overlap regime of
[Section 4](/theory/resonance-overlap).

## Step 1 — write the spiral in action–angle variables

Use the background actions $(J_R,L_z,J_z)$ and their angles
$(\theta_R,\theta_\phi,\theta_z)$, with frequencies $(\kappa,\Omega,\nu_z)$. A steady,
$m$-armed, tightly wound spiral of pattern speed $\Omega_p$ is

$$
\Phi_s = \mathrm{Re}\!\left[\Phi_0(R)\,e^{-k|z|}\,
e^{\,i\left(m\phi + \int\! \mathrm{d}R\, k - m\Omega_p t\right)}\right] .
$$

The three pieces are exactly the physics we have already met: $\Phi_0(R)$ is the
in-plane amplitude, $e^{-k|z|}$ is the vertical fall-off from
[Section 2, Step 1](/theory/form-factor), and the phase
$m\phi+\int \mathrm{d}R\, k-m\Omega_p t$ describes an $m$-armed pattern winding through
the disk and rotating at $\Omega_p$.

A star's position $(R,\phi,z)$ is itself an oscillating function of its angles. So we
expand $\Phi_s$ as a **Fourier series in the background angles** — the natural basis,
because the angles just advance linearly in time:

$$
\Phi_s = \sum_{n_R,\,n_z} \Phi_{n_R n_z}(J_R,L_z,J_z)\,
e^{\,i\left(n_R\theta_R + m\theta_\phi + n_z\theta_z - m\Omega_p t\right)} .
$$

Here $n_R$ and $n_z$ are integers labelling the radial and vertical harmonics; the
azimuthal harmonic is fixed at the arm number $m$. Each coefficient
$\Phi_{n_R n_z}$ is a **fast-angle average**: the *fast angles* are $\theta_R$ and
$\theta_z$, which wind through $2\pi$ at the orbital frequencies $\kappa$ and $\nu_z$
(tens of Myr), so $\Phi_{n_R n_z}$ is just the spiral projected onto the $(n_R,n_z)$
harmonic of those rapidly cycling angles, at fixed actions. (There is a complementary
*slow angle* — the star's phase relative to the rotating pattern, with rate
$\Omega-\Omega_p$ that nearly vanishes at corotation. It is *not* averaged away; it
survives to become the pendulum coordinate $\theta_r$ of Step 4.) Crucially, the
radial and vertical averages **separate**, because the radial epicycle and the
vertical bob are independent motions. We will use that separation in Step 3.

## Step 2 — which term resonates?

A term in the sum has phase
$\psi_{n_R n_z}= n_R\theta_R + m\theta_\phi + n_z\theta_z - m\Omega_p t$. Its time
derivative is

$$
\dot\psi_{n_R n_z} = n_R\kappa + m\Omega + n_z\nu_z - m\Omega_p .
$$

If $\dot\psi\neq0$ the term oscillates and averages to nothing over time — no
sustained effect. A term acts **resonantly** only when its phase is *stationary*,
$\dot\psi=0$:

$$
n_R\kappa + n_z\nu_z + m(\Omega-\Omega_p) = 0 .
$$

**Corotation** is the special case where the star orbits at the pattern speed,
$\Omega=\Omega_p$. Then the equation reduces to $n_R\kappa + n_z\nu_z=0$, whose only
solution for generic frequencies is $n_R=n_z=0$. So the corotation-resonant piece of
the spiral is the **$(n_R,n_z)=(0,0)$ harmonic** — the part of the potential averaged
over *both* the radial epicycle and the vertical orbit. This is the deep reason the
orbit average from Section 2 is the right object: corotation literally selects the
doubly orbit-averaged spiral.

## Step 3 — the coupling factorizes into $G(J_R)\,F(J_z)$

The resonant coupling $\Psi$ is the **amplitude of that $(0,0)$ term** — and pulling a
Fourier coefficient out of $\Phi_s$ *is* an integral. Here is why we integrate, and
what the integral is.

**Why integrate.** Over the long time a star spends drifting through corotation, the
fast angles $\theta_R,\theta_z$ wind through many full cycles. Any part of $\Phi_s$
that depends on them therefore delivers rapidly alternating pushes that cancel — it
averages to zero and drives no secular effect. The *only* part that survives is the
piece independent of the fast angles, which is by definition the $(0,0)$ Fourier
coefficient — i.e. the average of $\Phi_s$ over $\theta_R$ and $\theta_z$ at fixed
actions:

$$
\Psi = \big\langle \Phi_s\big\rangle_{\theta_R,\theta_z}
= \frac{1}{(2\pi)^2}\int_0^{2\pi}\!\mathrm{d}\theta_R\int_0^{2\pi}\!\mathrm{d}\theta_z\;
\Phi_s .
$$

**What is inside the integral.** Write the star's position through its angles. Radially
it sits at $R = R_{\rm CR}+x$ with the epicyclic excursion $x=a_R\cos\theta_R$
($a_R=\sqrt{2J_R/\kappa}$), so the spiral's radial phase is
$\int \mathrm{d}R\,k \approx kR_{\rm CR}+k a_R\cos\theta_R$; vertically it is at
$z=z(\theta_z;J_z)$, where the amplitude carries the fall-off $e^{-k|z|}$. Pulling out
the slowly varying guiding-centre amplitude $\Phi_0(R_{\rm CR})$ and the slow phase
(held fixed during the fast-angle average — it re-emerges as the $\cos\theta_r$ of the
pendulum in Step 4), the integrand becomes a radial factor times a vertical factor:

$$
\Psi = \Phi_0(R_{\rm CR})\;
\big\langle e^{ik a_R\cos\theta_R}\big\rangle_{\theta_R}\;
\big\langle e^{-k|z(\theta_z)|}\big\rangle_{\theta_z} .
$$

Because $\theta_R$ and $\theta_z$ are independent motions, the double integral
**separates** into the two single-angle averages we now evaluate.

**Radial part — the Kalnajs/Bessel factor.** During its epicycle a star's radial
excursion is $x = a_R\cos\theta_R$ with amplitude $a_R=\sqrt{2J_R/\kappa}$. The spiral
phase carries a factor $e^{ikx}=e^{ik a_R\cos\theta_R}$, and averaging it over the
radial angle uses the standard integral representation of the Bessel function,

$$
\langle e^{ik a_R\cos\theta_R}\rangle_{\theta_R}
= \frac{1}{2\pi}\int_0^{2\pi} \mathrm{d}\theta_R\; e^{ik a_R\cos\theta_R}
= J_0(k a_R) \equiv G(J_R) .
$$

This is the classical **radial reduction factor** (Binney & Tremaine 2008): a star
with a big epicycle ($a_R$ large) smears over many wavelengths of the arm and couples
weakly, so $G$ decreases — the *in-plane* selectivity.

**Vertical part — the form factor.** The vertical average of the fall-off is exactly
the object we already built in [Section 2](/theory/form-factor):

$$
\langle e^{-k|z|}\rangle_{\theta_z} = F(J_z,k) .
$$

Putting them together, the **amplitude** of the resonant coupling at corotation is

$$
\boxed{\;\Psi(J_R,J_z) = \Phi_0(R_{\rm CR})\;\underbrace{J_0(k a_R)}_{G(J_R)}\;
\underbrace{F(J_z,k)}_{\text{vertical}},\qquad a_R=\sqrt{2J_R/\kappa}\;}
$$

The two averages above only
acted on the *amplitude* of $\Phi_s$; its complex phase
$e^{i(m\phi+\int \mathrm{d}R\,k-m\Omega_p t)}$ does not depend on the fast angles
$\theta_R,\theta_z$ and so passes through the average untouched, collapsing to
$e^{i\theta_r}$ in the surviving **slow angle** $\theta_r$ (the star's phase relative to
the arm). Restoring it and taking the real part, the full fast-angle-averaged potential
is a single cosine in $\theta_r$ whose height is $\Psi$:

$$
\big\langle\Phi_s\big\rangle_{\theta_R,\theta_z}
= \mathrm{Re}\big[\,\Phi_0(R_{\rm CR})\,J_0(k a_R)\,F(J_z,k)\;e^{i\theta_r}\,\big]
= \Psi(J_R,J_z)\,\cos\theta_r .
$$

So $\Psi$ in the box is the **amplitude**, and $\Psi\cos\theta_r$ is the actual term the
resonance contributes.

This is the **central identification of the paper**: $F$ is the *exact vertical
Fourier coefficient of the spiral at corotation*. In one sentence —

> **The provenance bias is the $F$-factor of the corotation coupling; the classical
> Daniel & Wyse (2015) in-plane selectivity is the $G$-factor.**

$F$ was never a free choice; it falls out of the resonance.

## Step 4 — the resonance is a pendulum

Now we find out what $\Psi$ *does*. Move to the frame rotating with the pattern, where
the conserved energy is the **Jacobi integral** $H_J=H_0-\Omega_p L_z + \Phi_s$
($H_0$ is the unperturbed Hamiltonian). Average over the fast angles $\theta_R$ and
$\theta_z$ — legitimate because $J_R$ and $J_z$ are adiabatic invariants on the
timescale the slow corotation dynamics cares about — leaving a **slow Hamiltonian**
that depends only on $L_z$ and the slow angle $\theta_r$ (the angle of the star
relative to the arm).

Expand about corotation in the small quantity

$$
p \equiv L_z - L_{\rm CR},
$$

the angular-momentum offset from the corotation circle. By definition of corotation,
the first derivative vanishes there:

$$
\frac{\mathrm{d}H_0}{\mathrm{d}L_z}\bigg|_{\rm CR} = \Omega-\Omega_p = 0 .
$$

So the leading term is **quadratic**. Assemble the slow Hamiltonian explicitly: start
from the fast-angle-averaged Jacobi integral (the spiral has collapsed to its resonant
coupling, $\langle\Phi_s\rangle=\Psi\cos\theta_r$), call the axisymmetric part
$\bar H_0(L_z)\equiv H_0(L_z)-\Omega_p L_z$, and Taylor-expand it in $p=L_z-L_{\rm CR}$,
using $\mathrm{d}H_0/\mathrm{d}L_z=\Omega$:

$$
\begin{aligned}
\bar H(p,\theta_r)
  &= \big[\,H_0(L_z)-\Omega_p L_z\,\big] + \Psi\cos\theta_r
     && \text{averaged Jacobi integral} \\[4pt]
  &= \bar H_0(L_{\rm CR})
     + \frac{\mathrm{d}\bar H_0}{\mathrm{d}L_z}\bigg|_{\rm CR} p
     + \frac{1}{2}\frac{\mathrm{d}^2\bar H_0}{\mathrm{d}L_z^2}\bigg|_{\rm CR} p^2
     + \cdots + \Psi\cos\theta_r
     && \text{Taylor in } p \\[4pt]
  &= \text{const}
     + \underbrace{(\Omega-\Omega_p)\big|_{\rm CR}}_{=\,0}\, p
     + \frac{1}{2}\underbrace{\frac{\mathrm{d}\Omega}{\mathrm{d}L_z}\bigg|_{\rm CR}}_{\equiv\, g}\, p^2
     + \Psi\cos\theta_r
     && \Omega=\Omega_p \text{ at corotation} \\[4pt]
  &= \frac{1}{2}\,g\,p^2 + \Psi\cos\theta_r
     && \text{drop the constant.}
\end{aligned}
$$

The linear term dies because $\mathrm{d}\bar H_0/\mathrm{d}L_z=\Omega-\Omega_p$
vanishes at corotation, and the curvature
$\mathrm{d}^2\bar H_0/\mathrm{d}L_z^2=\mathrm{d}\Omega/\mathrm{d}L_z\equiv g$ supplies the
$\frac{1}{2}g\,p^2$. The result is the **pendulum Hamiltonian** (the resonant-trapping
construction of Monari et al. 2017, here carrying $J_z$ through $\Psi$),

$$
\bar H(p,\theta_r) = \frac{1}{2}\,g\,p^2 + \Psi\cos\theta_r,
\qquad g\equiv \frac{\mathrm{d}\Omega}{\mathrm{d}L_z}\bigg|_{\rm CR}.
$$

This is **exactly the Hamiltonian of a pendulum**, with $p$ playing the
role of momentum, $\theta_r$ the bob angle, $g$ an inverse "mass," and $\Psi$ the
strength of gravity on the bob. The depth of the pendulum well is the spiral coupling
$\Psi$ — and through $\Psi$, the depth is set by $F$.

## Step 5 — the trapping island width $\propto\sqrt{F}$

A pendulum has two kinds of motion: **circulation** (the bob swings all the way
around — here, a star that drifts past corotation) and **libration** (the bob rocks
back and forth in the well — here, a star *trapped* at corotation, carried along with
the arm and migrating). The two are separated by the **separatrix**.

Find the trapped region. The unstable equilibrium sits at the top of the cosine,
$\theta_r=0$, with energy $\bar H = \Psi$. The separatrix is the contour passing
through it:

$$
\frac{1}{2} g\,p^2 + \Psi\cos\theta_r = \Psi
\;\;\Longrightarrow\;\;
p^2 = \frac{2\Psi}{g}\,(1-\cos\theta_r) = \frac{4\Psi}{g}\sin^2\!\frac{\theta_r}{2}.
$$

So along the separatrix

$$
p_{\rm sep}(\theta_r) = 2\sqrt{\Psi/g}\;\left|\sin\frac{\theta_r}{2}\right| ,
$$

which is widest at $\theta_r=\pi$ (the bottom of the well). The **half-width** of the
trapping island in $p$ is therefore

$$
\boxed{\;\Delta p = 2\sqrt{\Psi/|g|} \;\propto\; \sqrt{F(J_z,k)}\;}
$$

because $\Psi\propto F$. This is the key inequality of the whole mechanism:
**vertically cold stars (large $F$) sit in wider trapping islands, so they are
captured — and migrate — preferentially.** The provenance bias, in one line.

### The narrow-island weight: $W\propto F^{1/2}$

Why is the trapped count proportional to $\Delta p$? The parent stars have some smooth
distribution $N(p)$ in the slow action $p=L_z-L_{\rm CR}$, centred on the corotation
circle. The island captures those that fall inside it — a range of $p$ of order its
width, around $p=0$. If the island is **narrow** compared with the spread $\sigma_p$ of
the parent distribution ($\Delta p\ll\sigma_p$), then $N(p)$ barely varies across that
small range, so $N(p)\approx N(0)$ and the count is simply density times width:

$$
N_{\rm trap}\approx N(0)\times(\text{width in }p)\;\propto\;\Delta p .
$$

(Equivalently, the trapped number is the — now uniform — phase-space density times the
libration *area*, and the pendulum's libration area is itself $\propto\Delta p$.) The
density factors out, leaving the migration weight proportional to the island width:

$$
W(J_z) \propto \Delta p \propto F(J_z,k)^{1/2} .
$$

This is the **"island-area counting" law**. It already biases migration toward cold
stars, but only as $\sqrt{F}$ — a fairly gentle slope. The one assumption it rests on —
that the island is narrow enough for $N(p)$ to be uniform across it — is exactly what
Step 6 drops, integrating the real distribution over the separatrix instead.

## Step 6 — the exact trapped fraction

The $\sqrt{F}$ law assumes infinitely narrow islands. To do better, ask: given a
realistic spread of stars in the slow action $p$, what *fraction* actually lands
inside the separatrix?

Model the parent population as a Gaussian in $p$ with dispersion $\sigma_p$,
$\;N(p)\propto e^{-p^2/2\sigma_p^2}$. At a fixed angle $\theta_r$, a star is trapped if
$|p| < p_{\rm sep}(\theta_r)$. The fraction of the Gaussian inside that band is an
error function:

$$
\frac{1}{\sqrt{2\pi}\,\sigma_p}\int_{-p_{\rm sep}}^{p_{\rm sep}} \mathrm{d}p\; e^{-p^2/2\sigma_p^2}
= \mathrm{erf}\!\left(\frac{p_{\rm sep}}{\sqrt2\,\sigma_p}\right).
$$

Now average over the angle $\theta_r$. Substitute $p_{\rm sep} = p_{\max}\sqrt{F}\,
\sin(\theta_r/2)$, where $p_{\max}=2\sqrt{\Psi_0/g}$ is the $F=1$ half-width
($\Psi_0$ the coupling of a mid-plane orbit), and define the single dimensionless
**island-width parameter**

$$
\kappa \equiv \frac{p_{\max}(F{=}1)}{\sigma_p} \;\propto\; \sqrt{|\Phi_s|} .
$$

Then $p_{\rm sep}/(\sqrt2\,\sigma_p) = (\kappa/\sqrt2)\sqrt{F}\,\sin(\theta_r/2)$, and
averaging over $\theta_r\in(0,2\pi)$ — with the substitution $u=\theta_r/2$ folding
the range to $(0,\pi)$ by the symmetry of $\sin$ — gives the **exact trapped weight**
(Equation 6 of the paper):

$$
\boxed{\;W(J_z) = \frac{1}{\pi}\int_0^\pi \mathrm{d}u\;
\mathrm{erf}\!\left(\frac{\kappa\sqrt{F(J_z,k)}}{\sqrt2}\,\sin u\right)\;}
$$

Check its two limits, both of which you can read straight off the error function:

- **Narrow islands, $\kappa\to0$:** use $\mathrm{erf}(x)\approx \frac{2}{\sqrt\pi}x$
  for small $x$, so the integrand is linear in $\sqrt F$ and
  $W\propto\sqrt{F}$ — we recover the island-counting law of Step 5.
- **Wide islands, $\kappa\to\infty$:** the error function saturates,
  $\mathrm{erf}\to1$, so $W\to1$ for *every* star — the weighting flattens out and
  the bias is *washed away*.

<figure class="scientific">
  <img src={useBaseUrl('/figures/trapped-weight.png')} alt="Exact trapped weight versus vertical action for three island widths" />
</figure>

*__The exact trapped weight__ (normalized to its mid-plane value) versus vertical
action, for three island-width parameters $\kappa$. It interpolates between the dilute
$\sqrt{F}$ law (dashed; narrow islands, strongest vertical selectivity) and a flat,
saturated profile (wide islands; selectivity lost).*

## Step 7 — from weight to bias, and the $-7\%$ floor

To get an observable, convert the weight into a **dispersion ratio**. The equilibrium
vertical distribution of an isothermal population is

$$
\frac{\mathrm{d}N}{\mathrm{d}E}\propto \frac{e^{-E}}{\nu_z(E)},
$$

i.e. a Boltzmann factor $e^{-E}$ (in units $\sigma_z=1$) times the density of states
$\propto$ orbital period $\propto 1/\nu_z$. The **migrator** population is this same
distribution *reweighted by the trapped weight* $W(J_z)$. Since the vertical energy
$E$ measures the squared vertical excursion, the squared dispersions are just the
mean energies, and the migrator-to-parent dispersion ratio is

$$
\frac{\sigma_z^{\rm mig}}{\sigma_z^{\rm all}}
= \sqrt{\frac{\langle E\rangle_{\rm mig}}{\langle E\rangle_{\rm all}}}
= \sqrt{\frac{\int \mathrm{d}E\; E\,W\,(e^{-E}/\nu_z)}{\int \mathrm{d}E\; W\,(e^{-E}/\nu_z)}\Big/
\frac{\int \mathrm{d}E\; E\,(e^{-E}/\nu_z)}{\int \mathrm{d}E\; (e^{-E}/\nu_z)}} .
$$

The **provenance bias** is the **log dispersion ratio**
$\ln\sigma_z^{\rm mig}/\sigma_z^{\rm all}$ — exactly the quantity the figures plot. It
is *negative* (because $W$ favours small $E$, the migrators are vertically colder than
the parent population, $\sigma_z^{\rm mig}<\sigma_z^{\rm all}$); the more negative, the
stronger the bias. Read as a percentage,
$\ln\sigma_z^{\rm mig}/\sigma_z^{\rm all}\approx-0.07$ means migrators are about $7\%$
colder. This is a *population-integrated* number — the whole distribution reweighted —
not the value of $W$ or $F$ for any single star.

<figure class="scientific">
  <img src={useBaseUrl('/figures/trapping-cap.png')} alt="Provenance bias from the exact trapped fraction versus island width" />
</figure>

*__The single-resonance floor.__ Provenance bias $\ln\sigma_z^{\rm mig}/\sigma_z^{\rm all}$
from the exact trapped weight at the Milky-Way thickness, versus island width $\kappa$.
The bias is most negative (strongest) in the dilute limit (where $W\propto\sqrt F$
gives the steepest vertical weighting) and weakens toward $0$ as $\kappa$ grows and the
islands saturate. So a single corotation resonance is bounded at __$\approx -7\%$__ (it
cannot be more negative), for any spiral strength.*

This is a strong and slightly counter-intuitive conclusion: making the spiral
*stronger* (larger $\kappa$) does **not** strengthen the single-resonance bias — it
*weakens* it (drives $\ln\sigma_z^{\rm mig}/\sigma_z^{\rm all}$ toward $0$), because wide
islands trap hot and cold stars alike. The most negative the single-resonance bias can
be — its **floor** — is the dilute-limit value with $W\propto\sqrt{F}$; at the
Milky-Way thickness that floor is $\approx -7\%$.

:::caution The "$-7\%$" is the log dispersion ratio, not a value of the form factor
$\sqrt{F}$ is **not** $0.07$. Across the population $\sqrt{F}$ runs over roughly
$0.3$–$1.0$ (see the [Section 2 figure](/theory/form-factor)). The $-7\%$ is the
*outcome of the reweighting integral above*: using $W=\sqrt{F}$ pulls the migrators'
mean vertical energy down from $\langle E\rangle_{\rm all}\approx1.11$ to
$\langle E\rangle_{\rm mig}\approx0.97$, so the dispersion ratio is
$\sigma_z^{\rm mig}/\sigma_z^{\rm all}=\sqrt{0.97/1.11}\approx0.93$ and the bias is
$\ln 0.93\approx-0.07$, i.e. $-7\%$. So "the $\sqrt{F}$ value" means *the bias produced
by the $W\propto\sqrt{F}$ weight law*, not the number $\sqrt{F}$ itself.
:::

### Finite thickness softens the floor further

If we replace the razor-thin $F$ by the finite-thickness $F_{\rm soft}$ from
[Section 2, Step 4](/theory/form-factor), the floor weakens further. The arm's own
vertical extent makes its gravity reach higher above the plane, so even hot stars
feel a non-negligible amplitude and the contrast between hot and cold shrinks.

<figure class="scientific">
  <img src={useBaseUrl('/figures/finite-thickness.png')} alt="Finite-thickness softening of the single-resonance cap" />
</figure>

*__Finite-thickness softening.__ Using $F_{\rm soft}(\alpha,h)$ in place of $F$, the
$\approx -7\%$ razor-thin floor weakens to $\approx -4$ to $-5.5\%$ across the plausible
Milky-Way arm thickness $h=h_s/z_0\sim0.5$–$1$ (shaded) — a $20$–$45\%$ reduction in
magnitude.*

## Why a single resonance is not enough

Even the steeper Daniel & Wyse (2018) capture-fraction accounting ($W\propto F$
rather than $F^{1/2}$) reaches only $\approx -14\%$. **None of these single-resonance
estimates produces the strong cold-migrator preference** seen in the simulations,
where migrators are drawn overwhelmingly from the kinematically cool population
(Vera-Ciro et al. 2016).

The arithmetic is telling us something physical: the Milky Way is *not* in the clean,
single-resonance trapping regime. It points instead to the regime where many
resonances **overlap** and trapping gives way to *diffusive* churning — which is
steeper in $F$. That is the subject of
[Section 4](/theory/resonance-overlap).

:::tip What to carry forward
The pendulum width $\Delta p\propto\sqrt{F}$ is the engine of the provenance bias.
A single resonance floors the bias near $-7\%$ (weaker with finite thickness). To reach
the observed $\sim-22\%$ we need resonance overlap, which steepens the weight from
$F^{1/2}$ toward $F^2$.
:::
