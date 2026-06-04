---
sidebar_position: 1
title: Introduction
slug: /
---

# An analytic provenance bias

Radial migration churns stellar angular momentum at the corotation resonance with
little heating. In $N$-body discs it acts **preferentially on vertically-cold
stars** -- the *provenance bias* (Vera-Ciro, D'Onghia & Navarro 2016; Mikkola,
McMillan & Hobbs 2020). That selectivity was established only qualitatively:
*cold stars spend more time near the mid-plane and couple more readily to the
plane-concentrated spiral.* This project turns that sentence into equations.

The coupling of a star to a spiral of radial wavenumber $k$ is the angle-average
over its vertical orbit of the spiral potential's $e^{-k|z|}$ fall-off above the
plane -- a **vertical form factor**

$$
F(J_z, k) = \big\langle e^{-k|z(\theta_z, J_z)|}\big\rangle_{\theta_z}.
$$

Inserting $F$ into the Daniel & Wyse (2015, 2018) corotation-capture criterion
yields the provenance bias from first principles, and -- because $F$ depends on
$k$ and $h_Z$ only through $\alpha = k\,h_Z$ -- ties it to the empirical
spiral-arm $J_R^{\max}$--$h_Z$ relation (Palicio et al. 2024).

- [The vertical form factor](theory/form-factor)
- [The provenance bias](theory/provenance-bias)
- [The $J_R$--$h_Z$ slope](results/slope) and [its predictions](results/predictions)
- [Using the library](library/usage)
