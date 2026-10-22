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
- `gadget.py`, `tracks.py`, `spiral.py`, `windows.py`, `migration.py`, `floor.py`,
  `arms.py`: the test of the model in a self-consistent N-body disk, the LD model of
  Vera-Ciro, D'Onghia and Navarro (2016). `tracks.py` reads the GADGET snapshots once into tracked
  orbits and ring sums (15 GB, kept outside the repository); `spiral.py` measures the
  arms, `windows.py` the per-star orbit averages, actions and form factors, and
  `migration.py` the variance of the angular-momentum change against the form factor,
  the bias per selection rule and the destination state. The resulting tables are
  cached under `assets/data/nbody/` (26 KB each) and plotted from there.
- `figures.py`, `_plotting.py`, `cli.py` -- publication figures and the command
  line. The `@figure` decorator writes each plot to `assets/figures/` as both a
  `.png` (docs site) and a `.pdf` (paper), only when its pixel content changed.

```bash
uv run pytest
uv run experiments figures   # writes the full set to assets/figures/
```

The N-body chain, from the snapshots on an external drive to the cached tables
(the extraction takes about 10 hours for the 611 snapshots; every later step takes
seconds to a minute). The extraction products (15 GB) go to `staging/` at the
repository root, a folder that git ignores; only the tables under `assets/data/nbody/`
and the figures under `assets/figures/` are committed:

```bash
uv run experiments nbody-extract /path/to/simulations/LD staging/LD --snapshots 512:1020
uv run experiments nbody-spiral staging/LD --windows 0.25:0.5,0.5:0.8 \
    --output staging/LD/analysis/spiral_modes.npz
uv run experiments nbody-window staging/LD --start 0.5
uv run experiments nbody-window staging/LD --start 2.5
uv run experiments nbody-migration staging/LD/analysis/windows/t_0.500.npz \
    staging/LD/analysis/windows/t_2.500.npz \
    staging/LD/analysis/spiral_modes.npz --spiral-window 1 \
    --output assets/data/nbody/migration-0.5-2.5.json
uv run experiments nbody-plot          # the four nbody-* figures from the cached tables
uv run experiments nbody-floor staging/LD-control staging/LD --times 0.5,0.8
uv run experiments nbody-arms staging/LD --start 0.5 --length 0.3
```
