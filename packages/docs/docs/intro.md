---
sidebar_position: 1
title: 1. Introduction
slug: /
---

# 1. Introduction — what problem are we solving?

:::note What is in this guide?
These pages walk through the problem *one section at a time*. Although I tried to make it 
as self-contained as possible, there are things here that probably will require some
background in galactic dynamics to understand. I highly recomment reading the always
reliable Binney & Tremaine's *Galactic Dynamics* (2008) and the more recent *Dynamics
and Astrophycis of Galaxies* (2025) by Jo Bovy.
:::

## The picture: a disk galaxy is a sea of orbits

For all practical purposes in this document, a disk galaxy like the Milky Way is an enormous collection of
stars each orbiting in a shared gravitational potential $\Phi$. Most of the visible mass is
arranged in a flattened disk, so the potential is nearly **axisymmetric** (it looks
the same at every azimuth $\phi$) and symmetric about the mid-plane $z=0$.

A star in such a potential does three nearly-independent things at once:

1. it goes **around** the center (azimuthal motion, roughly at the circular speed
   $V_c$);
2. it **breathes in and out** in radius, oscillating about a guiding circle
   (the *epicyclic* or *radial* oscillation);
3. it **bobs up and down** through the mid-plane (the *vertical* oscillation).

Because these three motions are each (approximately) a clean oscillation, we can
describe the star not by its messy position and velocity but by three conserved
"sizes of oscillation" called **actions**, paired with three angles that just
advance steadily in time. This is the *action–angle* description, and it is the
single most useful change of variables in the field.

### Actions and angles in one paragraph

For each oscillation, define an **action** $J$ as the area its motion sweeps out in
the phase plane (position vs. its conjugate momentum), divided by $2\pi$:

$$
J = \frac{1}{2\pi}\oint \mathrm{d}q\; p .
$$

The action is an *adiabatic invariant*: if the potential changes slowly, $J$ stays
(very nearly) constant. Each action has a partner **angle** $\theta$ that increases
linearly in time, $\theta(t)=\theta_0+\Omega t$, where the rate $\Omega =
\partial H/\partial J$ is the oscillation frequency. The three actions of a disk star
are:

| action | what it measures | partner frequency |
|---|---|---|
| $L_z$ | angular momentum about the spin axis ($=$ how far out the guiding circle is) | $\Omega$ (circular/orbital) |
| $J_R$ | size of the in–out radial epicycle | $\kappa$ (epicyclic) |
| $J_z$ | size of the up–down vertical bob | $\nu_z$ (vertical) |

A **cold** star has small $J_R$ and small $J_z$ — it stays near a circle in the
plane. A **hot** star has large $J_R$ and/or $J_z$ — it wanders radially/rises
high above the plane. "Vertically cold" specifically means small $J_z$.

## Radial migration and the corotation resonance

Real disks are not perfectly axisymmetric: they grow **spiral arms**. The arms in a
galaxy like ours are thought to be *transient and recurrent* — they appear, wind up,
dissolve, and reappear (Sellwood & Carlberg 1984; D'Onghia, Vogelsberger & Hernquist
2013; Baba, Saitoh & Wada 2013). A spiral is a slowly rotating, non-axisymmetric
bump in the potential. It rotates rigidly at a **pattern speed** $\Omega_p$, which is
generally *different* from the orbital speed $\Omega$ of any given star.

There is one special radius where a star keeps pace with the pattern: the
**corotation radius** $R_{\rm CR}$, where

$$
\Omega(R_{\rm CR}) = \Omega_p .
$$

A star sitting near corotation sees the spiral arm *not* rushing past, but hovering
nearly still in its own rotating frame. That sustained, non-averaging push is what
lets the arm exchange angular momentum $L_z$ with the star — and since $L_z$ sets the
radius of the guiding circle, changing $L_z$ **moves the star to a new radius**. This
is **radial migration** (Sellwood & Binney 2002; Roškar et al. 2008).

The remarkable feature of corotation migration is that it changes $L_z$ while barely
changing $J_R$ — it slides a star to a new circle without heating its epicycle. So a
star can travel kiloparsecs across the disk and stay nearly circular. This is why
migration matters for galactic archaeology: it scrambles the link between a star's
*birth* radius and its *present* radius, blurring chemical gradients.

:::tip The one-line summary of migration
A spiral arm hands angular momentum to stars **at corotation**, sliding them to new
radii with almost no heating. Which stars get picked up is the whole question of this
paper.
:::

## The puzzle: migration prefers vertically cold stars

In $N$-body simulations of disks, the stars that actually migrate are not a random
sample. They are **preferentially the vertically cold ones** — stars on nearly
planar orbits with small $J_z$. Vera-Ciro, D'Onghia & Navarro (2016) named this the
**provenance bias** and showed it is what sets the vertical structure of migrator
populations: the strongest migrators are drawn from the kinematically cool stars,
those with vertical velocity dispersions below the local average. Mikkola, McMillan &
Hobbs (2020) confirmed that how much migration reaches large $J_z$ depends on the
spiral strength, and pointed out that an **analytic explanation was still missing**.

The standard qualitative explanation is intuitive:

> *Cold stars spend more of their time near the mid-plane, where the spiral's
> gravity is strongest, so they couple to the arm more effectively and migrate more
> readily.*

That sentence is almost certainly right — but it is a *story*, not a derivation. It
does not tell you **how big** the bias should be, how it should depend on the disk
thickness or the spiral strength, or whether it can be connected to anything
measurable. **Turning that sentence into a quantitative model is the goal of this paper.**

## A second clue: the spiral $J_R^{\max}$–$h_Z$ relation

Independently, Palicio et al. (2024) measured something suggestive across simulated
spiral galaxies (and found it holds for the Milky Way too): the **maximum radial
action** $J_R^{\max}$ reached by spiral-arm stars grows *linearly* with the disk's
vertical scale height $h_Z$,

$$
J_R^{\max} = a\,h_Z + b , \qquad a \approx 3.7\times10^{-2}\,L_\odot\,\mathrm{kpc}^{-1} .
$$

Here $h_Z$ is how thick the disk is vertically and $J_R^{\max}$ is how radially hot
the spiral-affected stars can get. The slope $a$ was measured but **never derived**.
It is a second loose thread that, as we will see, is tied to the very same piece of
physics as the provenance bias.

:::caution 
Read $L_\odot$ here as angular momentum, not luminosity
:::

## The key object: a vertical form factor

Both puzzles, we will argue, are controlled by a single quantity. A thin spiral arm
concentrated near the mid-plane has a potential that falls off above the plane like
$e^{-k|z|}$, where $k$ is the radial wavenumber of the arm (how tightly wound it is).
At any instant a star feels the *actual* local force of the arm — this is just
Newtonian dynamics. It feels the full mid-plane strength each time it crosses $z=0$,
and a fraction $e^{-k|z|}$ of it when it is at height $z$. What controls the *slow*
migration dynamics, however, is not the instantaneous force but the **orbit-average**
of the arm's amplitude over a full vertical oscillation. (This is not just a
convenient summary: as Section 3 shows, only the orbit-averaged component of the
perturbation survives to drive the corotation resonance — the rapidly varying part
oscillates away over many orbits.) That orbit-average is the **vertical form factor**:

$$
F(J_z, k) = \big\langle e^{-k|z(\theta_z, J_z)|}\big\rangle_{\theta_z} .
$$

The notation $\langle\,\cdot\,\rangle_{\theta_z}$ means "average over one full vertical
oscillation." Read it physically:

- A **mid-plane** star ($J_z=0$) never leaves $z=0$, so its orbit-average is the full
  amplitude: $F=1$.
- A **vertically hot** star ($J_z$ large) spends most of its time high above the
  plane where $e^{-k|z|}$ is small, so its average $F$ is small.

So $F$ is exactly the "spends more time near the mid-plane" half of the verbal
mechanism, made quantitative. The rest of the paper is the claim that **$F$ is not a
hand-inserted weight but the precise coupling strength that enters the resonance**,
and that it is the common thread organizing everything that follows — the size of the
provenance bias, its dependence on thickness and spiral strength, and the
$J_R^{\max}$–$h_Z$ slope. $F$ does not set those magnitudes single-handedly: each also
needs its own physics — the resonance regime that turns coupling strength into a
migration rate (the bias), and the disk's structural anisotropy (the slope). What $F$
supplies is the link that makes them one story.

## The thread of the argument

Here is the logic, section by section, with links to the detailed walkthroughs:

1. **[The vertical form factor](/theory/form-factor)** — define $F$ carefully and
   compute it on a realistic disk model. *(Section 2)*
2. **[The corotation-resonant Hamiltonian](/theory/corotation-hamiltonian)** — show
   that $F$ is the *exact* vertical Fourier coefficient of the spiral at corotation,
   reduce the resonance to a pendulum, and read off how strongly each star is trapped.
   This caps single-arm trapping at a modest $\sim 7\%$ bias. *(Section 3)*
3. **[Resonance overlap and the diffusive regime](/theory/resonance-overlap)** — when
   several patterns (the bar plus spirals) overlap, trapping gives way to *diffusive*
   churning, which is steeper in $F$ and pushes the bias up to a derived $\sim
   19$–$24\%$ band. The Milky Way sits right at the overlap threshold. *(Section 4)*
4. **[The provenance bias and the $J_R^{\max}$–$h_Z$ relation](/results/provenance-bias)**
   — recover the bias magnitude, the measured slope, and a prediction that the slope
   *flattens with stellar age*. *(Section 5)*
5. **[Discussion](/discussion)** — how the pieces fit together, and the caveats.
   *(Section 6)*

The companion **[library](/library/usage)** is the open-source engine that derives
every number and figure here, with a full test suite.

:::info A note on units
Throughout, the vertical equations are written in units where $G=\sigma_z=z_0=1$
($G$ the gravitational constant, $\sigma_z$ the vertical velocity dispersion, $z_0$
the disk scale height). This is just a choice of rulers that makes the algebra clean;
the dimensionless thickness $\alpha\equiv k z_0$ is the one number that survives, and
for the Milky Way $\alpha\approx0.84$.
:::
