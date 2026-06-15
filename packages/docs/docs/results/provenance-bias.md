---
sidebar_position: 1
title: 5. The bias & the J_R–h_Z relation
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# 5. The provenance bias and the $J_R^{\max}$–$h_Z$ relation

**Goal of this section.** We now cash in the machinery. First we write a compact
effective weight for the diffusive regime and use it to predict the **size** of the
provenance bias and how it depends on disk thickness and spiral strength. Then we
derive the **slope** of the empirical $J_R^{\max}$–$h_Z$ relation of Palicio et al.
(2024) from first principles — and find it predicts that the relation should
**flatten with stellar age**, a clean, testable consequence.

## Part A — the magnitude of the bias

### Step 1 — a Boltzmann capture weight

In the diffusive regime, whether a star is swept into migration is a competition
between its **radial random energy** $\sigma_R^2$ (which carries it off-resonance) and
the **resonant coupling energy** $|\Phi_s|\,F$ (the spiral well it can fall into,
reduced by the vertical form factor from
[Section 3](/theory/corotation-hamiltonian)). A Boltzmann-style capture probability
weighs these against each other:

$$
P_{\rm capture} \propto \exp\!\left(-\frac{\sigma_R^2}{|\Phi_s|\,F}\right).
$$

This is the natural 3-D generalization of the Daniel & Wyse (2015) random-energy
capture criterion: their in-plane criterion is the $F=1$ case, and the vertical form
factor simply reduces the felt well depth, $|\Phi_s|\to|\Phi_s|F$.

To compare stars at different $J_z$ we **normalize to a mid-plane orbit** ($F=1$) —
i.e. divide by $P_{\rm capture}(F{=}1)=\exp(-\sigma_R^2/|\Phi_s|)$:

$$
W(J_z) = \frac{\exp\!\big(-\sigma_R^2/|\Phi_s|F\big)}{\exp\!\big(-\sigma_R^2/|\Phi_s|\big)}
= \exp\!\left[-\frac{\sigma_R^2}{|\Phi_s|}\left(\frac1F-1\right)\right].
$$

Defining the single dimensionless **spiral strength parameter** $s$, this is
Equation 11 of the paper:

$$
\boxed{\;W(J_z)=\exp\!\left[-s\left(\frac{1}{F(J_z,k)}-1\right)\right],
\qquad s\equiv\frac{\sigma_R^2}{|\Phi_s|}\;}
$$

Check it: a mid-plane star ($F=1$) has $W=1$; a vertically hot star ($F<1$, so
$1/F>1$) is exponentially suppressed. The single knob $s$ controls how sharp the
selection is. Physically this is the smooth, phenomenological stand-in for the
diffusive crossover weight of
[Section 4](/theory/resonance-overlap) at $S_0\approx 2$–$3$.

### Step 2 — reweight and read off the bias

Apply exactly the reweighting procedure of
[Section 3, Step 7](/theory/corotation-hamiltonian): take the equilibrium vertical
distribution $\mathrm{d}N/\mathrm{d}E_z\propto e^{-E_z}/\nu_z$, multiply by $W(J_z)$, and
form the migrator-to-parent dispersion ratio
$\sigma_z^{\rm mig}/\sigma_z^{\rm all}=\sqrt{\langle E_z\rangle_{\rm mig}/\langle
E_z\rangle_{\rm all}}$. The provenance bias is the log dispersion ratio
$\ln\sigma_z^{\rm mig}/\sigma_z^{\rm all}$ (negative; the more negative, the stronger
the bias).

<figure class="scientific">
  <img src={useBaseUrl('/figures/provenance-bias.png')} alt="Predicted migrator bias versus disk thickness" />
</figure>

*__Predicted migrator bias__ $\ln\sigma_z^{\rm mig}/\sigma_z^{\rm all}$ versus disk
thickness $\alpha=k h_Z$, shown as a band over the physical spiral-strength range
$s=0.8$–$2$ ($|\Phi_s|\sim1$–$3\%\,V_c^2$). The bias __deepens (grows more negative)
with thickness__; at the Milky-Way value $\alpha=0.84$ (dotted) it is
$\approx -20$ to $-41\%$.*

Two numbers anchor the result:

- At the Milky-Way thickness $\alpha=0.84$, a bias of $\approx-22\%$
  ($\sigma_z^{\rm mig}/\sigma_z^{\rm all}\approx0.80$, i.e. $\ln 0.80\approx-0.22$ — the
  cool-star threshold of Vera-Ciro et al. 2016) corresponds to $s=0.90$, comfortably
  **inside** the physical range $s\sim0.8$–$2$. No tuning is needed.
- The model makes two falsifiable trends explicit:
  1. the bias **weakens as the spiral strengthens** (smaller $s$ means a deeper well
     that captures hot stars too) — matching the strength dependence found by Mikkola
     et al. (2020);
  2. the bias **strengthens with disk thickness** $\alpha$ — and is independent of
     spiral morphology, matching Vera-Ciro et al. (2016).

## Part B — the $J_R^{\max}$–$h_Z$ slope

The same form factor that controls the bias links it to a completely different
observable: the Palicio et al. (2024) linear relation
$J_R^{\max}=a\,h_Z+b$. We now derive the slope $a$.

### Step 3 — two structural ingredients

**Vertical: the scale height.** For a self-gravitating isothermal sheet, vertical
hydrostatic equilibrium between the pressure $\sim\sigma_z^2$ and the self-gravity of
a surface density $\Sigma$ gives the scale height

$$
h_Z = \frac{\sigma_z^2}{\pi G\Sigma}.
$$

(Thicker disks are hotter vertically and/or less self-gravitating.)

**Radial: the maximum radial action.** The epicyclic (radial) action of a star with
radial velocity dispersion $\sigma_R$ and epicyclic frequency $\kappa$ scales as
$J_R\sim\sigma_R^2/\kappa$. The hot tail that defines $J_R^{\max}$ is a fixed multiple
of this,

$$
J_R^{\max}=c_{\max}\,\frac{\sigma_R^2}{\kappa},
$$

with $c_{\max}$ an order-unity constant set by where the tail is cut.

### Step 4 — divide them: the slope is an anisotropy ratio

Form the ratio $a=J_R^{\max}/h_Z$ directly:

$$
a = \frac{J_R^{\max}}{h_Z}
= \frac{c_{\max}\,\sigma_R^2/\kappa}{\sigma_z^2/(\pi G\Sigma)}
= c_{\max}\,\frac{\pi G\Sigma}{\kappa}\left(\frac{\sigma_R}{\sigma_z}\right)^2 .
$$

That is Equation 12 of the paper:

$$
\boxed{\;a = \frac{J_R^{\max}}{h_Z}
= c_{\max}\,\frac{\pi G\Sigma}{\kappa}\left(\frac{\sigma_R}{\sigma_z}\right)^2\;}
$$

The slope is the **squared radial-to-vertical heating-anisotropy ratio**
$(\sigma_R/\sigma_z)^2$, scaled by structural quantities $\Sigma$ and $\kappa$. It has
a clean reading: a disk that is hotter radially than vertically (large
$\sigma_R/\sigma_z$) reaches large $J_R^{\max}$ for a given $h_Z$, i.e. a steep slope.

### Step 5 — put in solar-neighborhood numbers

Use $\Sigma=50\,M_\odot\,\mathrm{pc}^{-2}$,
$\kappa=0.037\,\mathrm{km\,s^{-1}\,pc^{-1}}$, $\sigma_R=35\,\mathrm{km\,s^{-1}}$,
$\sigma_z=18\,\mathrm{km\,s^{-1}}$, and $c_{\max}=1$. **Check the dimensions first.**
The structural factor $\pi G\Sigma/\kappa$ works out to a *velocity*
($\approx18\,\mathrm{km\,s^{-1}}$), and the anisotropy ratio $(35/18)^2\approx3.78$ is
dimensionless, so the slope $a$ is a **velocity** — a specific momentum — exactly as
an action-over-length ($J_R^{\max}/h_Z$) must be. Numerically,

$$
a \approx 69\,\mathrm{km\,s^{-1}} \;=\; 3.6\times10^{-2}\,L_\odot\,\mathrm{kpc}^{-1},
$$

within a few percent of the measured $3.7\times10^{-2}\,L_\odot\,\mathrm{kpc}^{-1}$.

:::caution $L_\odot$ here is the Sun's angular momentum, not its luminosity
The relation is quoted in $L_\odot/\mathrm{kpc}$, where
$L_\odot\equiv R_0V_0\approx1.9\times10^{3}\,\mathrm{kpc\,km\,s^{-1}}$ is the Sun's
*orbital angular momentum* (an action; more carefully $L_{z,\odot}$) — **not** the
solar luminosity. Since $L_\odot$ is an action (length$\times$velocity),
$L_\odot/\mathrm{kpc}$ is a velocity, which is why
$3.6\times10^{-2}\,L_\odot\,\mathrm{kpc}^{-1}=69\,\mathrm{km\,s^{-1}}$ — and the
dimensions of $a=J_R^{\max}/h_Z$ come out as a momentum, as they must. (The engine
computes $a$ in $\mathrm{km\,s^{-1}}$ and only divides by $R_0V_0$ at the end to
report it in these units.)
:::

(One bookkeeping caveat: our
$h_Z$ is the self-gravitating $\mathrm{sech}^2$ scale height, while Palicio et al. fit
an *exponential* vertical scale-length; the two differ by an order-unity factor that
we absorb into $c_{\max}$. The point is that the slope is structural, not the third
decimal.)

## Part C — a prediction: the slope runs with age

### Step 6 — only the anisotropy is population-dependent

In Equation 12 the surface density $\Sigma$ and epicyclic frequency $\kappa$ are
**structural** — properties of the disk at a given radius, the same for old and young
stars. The *only* factor that depends on which stellar population you select is the
anisotropy ratio $(\sigma_R/\sigma_z)^2$.

Each velocity dispersion grows with stellar age through an
**age–velocity-dispersion relation**, $\sigma\propto\mathrm{age}^{\beta}$, with a
different exponent for the radial and vertical channels. Therefore

$$
a(\mathrm{age}) \propto \left(\frac{\sigma_R}{\sigma_z}\right)^2
\propto \mathrm{age}^{\,2(\beta_R-\beta_z)} .
$$

That is Equation 13 of the paper:

$$
\boxed{\;a(\mathrm{age}) \propto \mathrm{age}^{\,2(\beta_R-\beta_z)}\;}
$$

### Step 7 — the sign and size of the effect

Measured exponents are $\beta_z\approx0.5$ (vertical heating is efficient) and
$\beta_R\approx0.35$ (radial heating less so) (Aumer, Binney & Schönrich 2016; Sun et
al. 2024). So the exponent is

$$
2(\beta_R-\beta_z) = 2(0.35-0.50) = -0.3 ,
$$

which is **negative**: older populations have a *shallower* slope. Quantitatively, an
$8\,\mathrm{Gyr}$ population has a slope

$$
\frac{a(8\,\mathrm{Gyr})}{a(1\,\mathrm{Gyr})} = 8^{-0.3} \approx 0.54 ,
$$

about half that of a $1\,\mathrm{Gyr}$ population. **The $J_R^{\max}$–$h_Z$ relation
should flatten with age.**

This is a sharp, falsifiable test. Re-fitting the relation in mono-age or
mono-abundance bins of current Gaia–APOGEE–LAMOST data measures
$\beta_R-\beta_z$ *directly from spiral-arm kinematics*. An age-*independent* slope
would instead require $\beta_R=\beta_z$ — a different statement about how disks heat.

:::tip What to carry forward
One object, the vertical form factor $F$, is the common thread linking the *size* of
the provenance bias to the *slope* of the $J_R^{\max}$–$h_Z$ relation — both governed
by the same disk thickness $\alpha=k\,h_Z$. Neither magnitude is set by $F$ alone,
though: the bias size ($\sim-22\%$ at $s\approx0.9$) also needs the migration weight
from the resonance regime ([Sections 3](/theory/corotation-hamiltonian)–[4](/theory/resonance-overlap)),
and the slope ($\approx3.6\times10^{-2}\,L_\odot\,\mathrm{kpc}^{-1}\approx69\,
\mathrm{km\,s^{-1}}$) comes from the structural factor
$\pi G\Sigma/\kappa\,(\sigma_R/\sigma_z)^2$, with $F$ selecting the cold migrators that
populate $J_R^{\max}$. The model also predicts the slope flattens with age. The
[Discussion](/discussion) puts the whole story together.
:::
