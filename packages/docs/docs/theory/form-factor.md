---
sidebar_position: 2
title: 2. The vertical form factor
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# 2. The vertical form factor

**Goal of this section.** Build the object $F(J_z,k)$ from scratch: first show *why*
a spiral's gravity falls off as $e^{-k|z|}$ above the plane, then turn the orbit
average into an integral we can actually compute, evaluate it on a realistic disk
model, and finally correct it for the fact that real arms are not infinitely thin.

## Step 1 — why a thin spiral decays as $e^{-k|z|}$

Above the disk there is (almost) no mass, so the spiral's gravitational potential
$\Phi_s$ obeys **Laplace's equation**,

$$
\nabla^2 \Phi_s = 0 \qquad (z \neq 0).
$$

A tightly wound spiral varies in the radial direction like a wave with wavenumber
$k$ — locally, $\Phi_s \propto e^{ikR}$ in the plane. Treat a small patch of the disk
as flat (Cartesian $x$ along the radial direction, $z$ vertical) so that
$\Phi_s(x,z) = f(z)\,e^{ikx}$. Plug into Laplace's equation:

$$
\frac{\partial^2 \Phi_s}{\partial x^2} + \frac{\partial^2 \Phi_s}{\partial z^2}
= \big(-k^2 + f''/f\big)\,\Phi_s = 0
\;\;\Longrightarrow\;\;
f'' = k^2 f .
$$

The solutions are $f(z)\propto e^{\pm k z}$. Requiring the potential to **stay finite
far from the disk** keeps only the decaying branch on each side, i.e.

$$
\boxed{\;\Phi_s(x,z) = \Phi_s(x,0)\,e^{-k|z|}\;}
$$

This is a standard result (Binney & Tremaine 2008): *the more tightly wound the arm
(larger $k$), the faster its influence dies away above the plane.* That single
exponential is the entire reason vertical motion matters for migration.

:::tip Why does a larger $k$ decay faster? (the intuition)
Two complementary pictures explain it.

**Neighboring opposite lanes cancel.** A spiral is a sequence of overdense (arm) and
underdense (inter-arm) lanes, alternating in sign and spaced by half a wavelength,
$\lambda/2=\pi/k$. Sit just above an arm and you feel that overdensity strongly,
because it is the nearest thing to you. Now rise to a height $z$: the *neighboring*
inter-arm lanes — of the **opposite** sign, a horizontal distance $\sim\lambda/2$ away
— start to lie at a comparable distance from you, and their pull partly cancels the
arm's. Once $z$ exceeds the lane spacing, the $+$ and $-$ contributions you see are
nearly equidistant and almost cancel, leaving an exponentially small net potential. A
more tightly wound arm (larger $k$, smaller $\lambda$) packs those cancelling opposite
lanes *closer together*, so the cancellation sets in at a smaller height — the field
dies off faster.

**Only one length scale.** A pure sinusoidal source of wavenumber $k$ has a single
horizontal length scale, its wavelength $\lambda=2\pi/k$. Above the plane Laplace's
equation introduces no new scale, so the field can only vary vertically on that same
scale — its decay length must be $\sim 1/k$. This is exactly what
$f''=k^2 f \Rightarrow f\propto e^{-k|z|}$ says: the horizontal wiggle rate $k$ *is*
the vertical decay rate. Finer horizontal structure forces faster vertical decay.
:::

## Step 2 — what a bobbing star actually feels

A star is not stationary; it oscillates vertically as $z(\theta_z; J_z)$, where the
vertical angle $\theta_z=\nu_z t$ advances at the vertical frequency $\nu_z$. Over
one oscillation it samples a *range* of heights, and therefore a range of spiral
amplitudes $e^{-k|z|}$. The effective coupling is the time-average of that amplitude
over an orbit. Because $\theta_z$ advances uniformly, a **time average equals an
angle average**:

$$
F(J_z,k) \equiv \big\langle e^{-k|z|}\big\rangle_{\theta_z}
= \frac{1}{2\pi}\oint \mathrm{d}\theta_z\; e^{-k|z(\theta_z)|}
= \frac{1}{T}\oint \mathrm{d}t\; e^{-k|z(t)|} ,
$$

with $T=2\pi/\nu_z$ the vertical period.

### Turning the time integral into a height integral

We do not know $z(t)$ in closed form, but we *do* know the vertical velocity at each
height from energy conservation. The vertical energy is

$$
E = \frac{1}{2} v_z^2 + \Phi(z) \;\;\Longrightarrow\;\; v_z = \frac{\mathrm{d}z}{\mathrm{d}t}
= \sqrt{2\big[E-\Phi(z)\big]} ,
$$

so we can trade the time element for a height element, $\mathrm{d}t = \mathrm{d}z/|v_z|$.
One full period consists of four identical quarter-swings ($0\to z_m$, $z_m\to 0$,
$0\to -z_m$, $-z_m\to 0$), where $z_m$ is the **turning point** defined by
$\Phi(z_m)=E$ (the height at which $v_z=0$). Since $e^{-k|z|}$ is even in $z$, all
four quarters contribute equally:

$$
\oint \mathrm{d}t\; e^{-k|z|} = 4\int_0^{z_m} \mathrm{d}z\; \frac{e^{-kz}}{|v_z|} .
$$

Putting it together with $1/T = \nu_z/2\pi$:

$$
F(J_z,k) = \frac{\nu_z}{2\pi}\cdot 4\int_0^{z_m} \mathrm{d}z\; \frac{e^{-kz}}{|v_z|}
= \frac{2}{\pi}\int_0^{z_m} \mathrm{d}z\; e^{-kz}\,\frac{\nu_z}{|v_z|} .
$$

That is the working formula — Equation (1) of the paper:

$$
\boxed{\;F(J_z, k) = \frac{2}{\pi}\int_0^{z_m} \mathrm{d}z\; e^{-kz}\,\frac{\nu_z}{|v_z|},
\qquad v_z=\sqrt{2[E-\Phi(z)]}\;}
$$

The integrand has a clean reading: $\nu_z/|v_z|$ is proportional to the **time per
unit height** the star spends at $z$ (slow near the turning point, fast through the
mid-plane), and $e^{-kz}$ weights each height by how strong the spiral is there. $F$
is literally "time spent near the plane, weighted by the spiral's reach."

## Step 3 — evaluate it on a realistic disk: the isothermal sheet

To get numbers we need a concrete vertical potential $\Phi(z)$. The standard
self-consistent model of an isothermal stellar layer (Spitzer 1942) gives

$$
\Phi(z) = 2\ln\cosh z \qquad \text{(in units } G=\sigma_z=z_0=1).
$$

Everything we need follows from this one function.

- **Restoring force / frequency near the plane.** Expand for small $z$ using
  $\ln\cosh z \approx z^2/2 - z^4/12+\dots$ so $\Phi\approx z^2$.
  The vertical frequency at low energy is set by the curvature
  $\Phi''(0)$: with $\Phi'=2\tanh z$, $\Phi''=2\,\mathrm{sech}^2 z$, we get
  $\Phi''(0)=2$, hence $\nu_z(J_z\to 0)=\sqrt{\Phi''(0)}=\sqrt2$. (At higher energy
  the orbit feels the softer, flatter top of the well and $\nu_z$ drops.)
- **Turning point.** Set $\Phi(z_m)=E$: $\;2\ln\cosh z_m = E \Rightarrow
  z_m=\mathrm{arccosh}\,(e^{E/2})$.
- **Vertical action.** By the general definition,
  $$
  J_z = \frac{1}{2\pi}\oint \mathrm{d}z\; v_z = \frac{2}{\pi}\int_0^{z_m} \mathrm{d}z\;\sqrt{2[E-\Phi(z)]} ,
  $$
  which maps each energy $E$ to an action $J_z$ (this is the $x$–axis of the figure
  below).

With $\Phi$ fixed, the *only* free parameter left in $F$ is the combination

$$
\alpha \equiv k z_0 ,
$$

the **dimensionless thickness** — the arm wavenumber measured in units of the disk
scale height. (In our $z_0=1$ units, $k$ and $\alpha$ are the same number.) This is
the crucial economy of the model: thickness and wavenumber only ever appear together,
as $\alpha$.

### Reading the result

<figure class="scientific">
  <img src={useBaseUrl('/figures/form-factor.png')} alt="Vertical form factor F versus vertical action for three values of alpha" />
</figure>

*__The vertical form factor__ $F(J_z,k)=\langle e^{-k|z|}\rangle$ versus vertical
action $J_z$, for three spiral wavenumbers $\alpha=kz_0$. By construction $F\to1$ as
$J_z\to0$ (a mid-plane orbit feels the full amplitude); $F$ falls monotonically as the
star gets vertically hotter, and the suppression steepens for more tightly wound arms
(larger $\alpha$). The dashed curve, $\alpha=0.84$, is the Milky-Way value.*

Two features are worth internalizing:

1. **$F$ decreases monotonically with $J_z$.** Hotter stars feel a weaker
   orbit-averaged arm. This is the quantitative content of "cold stars couple more
   readily."
2. **The effect is real, not negligible, for the Milky Way.** With a radial
   wavelength $\lambda_R\sim3\,\mathrm{kpc}$ (so $k=2\pi/\lambda_R\sim2\,\mathrm{kpc}^{-1}$;
   Reid et al. 2019) and a vertical scale $z_0\sim0.4\,\mathrm{kpc}$ (Bland-Hawthorn &
   Gerhard 2016), we get $\alpha\approx0.84$ — of order unity. The vertical coupling
   is appreciably selective, which is exactly why the provenance bias is an
   observable effect rather than a rounding error.

## Step 4 — real arms have thickness (the softened kernel)

The $e^{-k|z|}$ law is the **razor-thin** limit: it assumes all the arm's mass sits
exactly in the plane, which gives a sharp cusp at $z=0$. A real arm is overdense
*disk material* with its own vertical extent $h_s$, comparable to the disk scale
$z_0$. Smearing the thin-sheet source over that thickness rounds off the cusp (Toomre
1964).

Take the arm's vertical mass profile to be a normalized exponential,
$g(z)=(\beta/2)\,e^{-\beta|z|}$ with $\beta\equiv 1/h_s$ (so $\int \mathrm{d}z\,g=1$),
and keep the in-plane pattern $\Sigma(x)=\Sigma_0\,e^{ikx}$ from Step 1. The arm's 3-D
density is then $\rho(x,z)=\Sigma_0\,e^{ikx}\,g(z)$, and we solve Poisson's equation
$\nabla^2\Phi = 4\pi G\rho$ for it.

**Separate the horizontal wave.** Write $\Phi(x,z)=e^{ikx}\,\psi(z)$. Exactly as in
Step 1 the factor $e^{ikx}$ turns $\partial_x^2\to-k^2$, so Poisson collapses to a 1-D
equation for the vertical shape $\psi$:

$$
\psi''(z) - k^2\,\psi(z) = 4\pi G\,\Sigma_0\,g(z) .
$$

**Use the Green's function.** The operator $\partial_z^2-k^2$ has Green's function
$\mathcal{G}(z)=-e^{-k|z|}/(2k)$, i.e. $\mathcal{G}''-k^2\mathcal{G}=\delta(z)$ — the
$-1/(2k)$ prefactor is fixed by the unit jump that $\mathcal{G}'$ must make across
$z=0$. But this is nothing other than the razor-thin kernel of Step 1: a single sheet
at height $z'$ sources a potential $\propto e^{-k|z-z'|}$. The solution is therefore
the source convolved with that kernel,

$$
\psi(z) \;\propto\; \int \mathrm{d}z'\; e^{-k|z-z'|}\,g(z')
\;=\; \big(e^{-k|\cdot|}*g\big)(z) .
$$

For a true sheet ($g=\delta$) this returns $\psi\propto e^{-k|z|}$, so "thickening the
source" means *precisely* convolving the thin-sheet kernel with the arm's vertical
profile — that is all the softening is.

**Do the convolution.** With $g(z)=(\beta/2)\,e^{-\beta|z|}$, the convolution of two
two-sided exponentials is elementary: split the $z'$ integral at $z'=0$ and $z'=z$
(taking $z\ge0$; the result is even in $z$). The three pieces sum to

$$
\int \mathrm{d}z'\; e^{-k|z-z'|}\,\frac{\beta}{2}\,e^{-\beta|z'|}
= \frac{\beta\big(k\,e^{-\beta|z|} - \beta\,e^{-k|z|}\big)}{k^2-\beta^2} .
$$

**Normalize to the mid-plane.** Dividing by the value at $z=0$, which is
$\beta/(k+\beta)$, cancels the common $(k+\beta)$ and leaves the **softened kernel**
(normalized so $K(0)=1$):

$$
K(z) = \frac{k\,e^{-\beta|z|} - \beta\,e^{-k|z|}}{k-\beta}
     = \frac{\beta\,e^{-k|z|} - k\,e^{-\beta|z|}}{\beta - k} .
$$

Sanity checks, both of which you should verify by hand:

- **Normalization:** at $z=0$, $K(0)=(\beta-k)/(\beta-k)=1$. Good — the mid-plane
  amplitude is unchanged.
- **Thin limit:** as $h_s\to0$ (so $\beta\to\infty$), the second term vanishes and
  $K\to e^{-k|z|}$, the razor-thin kernel. Good.

Now orbit-average $K$. Because the average is **linear** in $z$-dependence, we can
average each exponential separately, and each one is *itself a form factor* at its
own wavenumber:

$$
\langle e^{-k|z|}\rangle = F(J_z,k)=F(\alpha), \qquad
\langle e^{-\beta|z|}\rangle = F(J_z,\beta)=F(1/h),
$$

where $h\equiv h_s/z_0$ (so in our units $\beta=1/h$, and $k=\alpha$). Therefore

$$
F_{\rm soft} = \langle K\rangle = \frac{\beta\,F(\alpha) - k\,F(1/h)}{\beta-k} .
$$

Multiply top and bottom by $h$ (using $\beta h = 1$ and $kh=\alpha h$) to get the
tidy form — Equation (2) of the paper:

$$
\boxed{\;F_{\rm soft}(J_z;\alpha,h) = \frac{F(J_z,\alpha) - \alpha h\,F(J_z,1/h)}{1-\alpha h},
\qquad h\equiv h_s/z_0 \;}
$$

It is just a fixed linear combination of the bare form factor evaluated at two
wavenumbers. Its limits are the physical ones: $F_{\rm soft}\to F$ as $h\to0$ (thin
arm) and $F_{\rm soft}\to 1$ as $h\to\infty$ (an arm so thick the star never escapes
it). We will use $F_{\rm soft}$ in place of the razor-thin $F$ when we put in
Milky-Way numbers, and it turns out to *weaken* the bias by an order-unity factor —
quantified in [Section 3](/theory/corotation-hamiltonian).

:::tip What to carry forward
$F(J_z,k)$ is the orbit-averaged spiral amplitude a star feels. It equals $1$ for a
mid-plane orbit, falls with vertical action, depends on thickness and wavenumber only
through $\alpha=kz_0$, and softens (toward $1$) when the arm has finite thickness $h$.
The next section shows this same $F$ is *exactly* the coupling that traps stars at
corotation — it was never a free choice.
:::
