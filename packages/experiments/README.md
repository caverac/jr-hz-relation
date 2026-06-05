# experiments

The analysis code and command-line interface behind the analytic provenance-bias /
spiral J_R-h_Z paper. This is a **workspace-internal** package -- it is not a
published PyPI distribution; it exists only to derive every number and figure in
`packages/pre-print/`.

- `sheet.py` -- isothermal-sheet vertical orbit structure (J_z, nu_z, turning point).
- `form_factor.py` -- the vertical form factor F(J_z,k), the Daniel-Wyse capture
  weight, and the provenance bias sigma_z,mig/sigma_z,all.
- `trapping.py`, `crossover.py`, `overlap.py`, `thickness.py`, `balescu_lenard.py`
  -- the single-resonance trapped-fraction cap, the trapping->diffusion crossover,
  the Chirikov bar-spiral overlap, the finite-thickness kernel softening, and the
  Balescu-Lenard diffusive weight.
- `slope.py` -- the structural J_R-h_Z slope and its age-running.
- `validate.py` -- the independent galpy cross-check of F.
- `figures.py`, `_plotting.py`, `cli.py` -- publication figures and the command
  line. The `@figure` decorator writes each plot to `assets/figures/` as both a
  `.png` (docs site) and a `.pdf` (paper), only when its pixel content changed.

```bash
uv run pytest
uv run experiments figures   # writes the full set to assets/figures/
```
