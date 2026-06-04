---
sidebar_position: 1
title: The vertical form factor
---

# The vertical form factor

A razor-thin spiral of radial wavenumber $k$ has a potential that satisfies
Laplace's equation above the disc and so decays as $e^{-k|z|}$ (Binney & Tremaine
2008). A star on a vertical orbit $z(\theta_z; J_z)$ samples the spiral through the
angle-average of that decay,

$$
F(J_z, k) = \big\langle e^{-k|z(\theta_z, J_z)|}\big\rangle_{\theta_z}
          = \frac{2}{\pi}\int_0^{z_m} e^{-kz}\,\frac{\nu_z}{|v_z|}\,dz,
$$

evaluated on the self-consistent isothermal sheet $\Phi(z) = 2\ln\cosh z$ (units
$G=\sigma_z=z_0=1$), where the only parameter is the dimensionless thickness
$\alpha \equiv k z_0$.

By construction $F(0,k)=1$ -- a mid-plane orbit feels the full in-plane amplitude
-- and $F$ decreases monotonically with vertical action: vertically hot stars
couple weakly to the spiral. This is the quantitative content of "cold stars
couple more readily."

For the Milky Way $\lambda_R\sim3$ kpc and $z_0\sim0.4$ kpc give
$\alpha\sim0.84$ -- of order unity, which is why the provenance bias is an
order-20% effect rather than negligible.
