---
sidebar_position: 1
title: Usage
---

# Using the library

The `experiments` package implements every result here.

Scalar diagnostics print a single number:

```bash
uv run experiments form-factor --energy 1.0 --alpha 0.84
uv run experiments bias --alpha 0.84 --strength 0.9
uv run experiments anchor --alpha 0.84 --target 0.90
uv run experiments slope --c-max 1.0
uv run experiments age-running --age 8 --ref 1 --beta-r 0.35 --beta-z 0.5
```

Each figure has its own command (with per-figure options), or generate the whole
set at once. Every figure is written to `assets/figures/` as both a `.png` (for
this docs site) and a `.pdf` (for the paper), and is only rewritten when its
content actually changed:

```bash
uv run experiments form-factor-plot --n-energies 60
uv run experiments balescu-lenard-plot --n-b 24
uv run experiments figures   # the full set
```

Run `uv run experiments --help` for the full command list.

## The N-body test

The `nbody-*` commands run the test of [Section 6](/results/nbody-test) from the
GADGET snapshots of the LD model to the figures. The snapshots (2.8 GB each, 1,020 of
them) stay on their drive and the extracted products (15 GB) go to `staging/` at the
repository root, a folder that git ignores; only the tables of the migration test are
cached, under `assets/data/nbody/` (26 KB per baseline), so the figures can be redrawn
without the simulation.

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
uv run experiments nbody-plot
```

| Command | Input | Output | Time |
| --- | --- | --- | --- |
| `nbody-extract` | the `snap_NNN` files of a run | `tracks/` and `rings/` per snapshot, `meta/` | 55 to 68 s per snapshot |
| `nbody-spiral` | `rings/` | amplitudes, wavenumbers, strengths, pattern speeds; an `npz` of the modes | 10 s |
| `nbody-window` | `tracks/`, `rings/` | per-star averages, actions, periods and form factors over one window | 65 s |
| `nbody-migration` | two windows and the modes | the tables of the test, as markdown and JSON | 5 s |
| `nbody-floor` | a control and a run | the variance of $\Delta L_z$ in both, per ring | 5 s |
| `nbody-arms` | `tracks/`, `rings/` | the vertical profile of the arms per ring and harmonic | 20 s |
| `nbody-plot` | the cached JSON tables | `nbody-variance`, `nbody-exponents`, `nbody-rules`, `nbody-destination` | 10 s |

`nbody-migration --form thin` uses the razor-thin form factor $\langle e^{-k|z|}\rangle$
instead of the layer factor, `--harmonics m` one harmonic instead of the combined
$m = 5$ to $8$, and `--k-sweep` adds the exponent against $F_k$ for every wavenumber of
the stored grid.

From Python:

```python
from experiments import vertical_form_factor, dispersion_ratio, slope_in_lsun_per_kpc, SolarNeighbourhood

vertical_form_factor(1.0, 0.84)          # form factor at E=1, alpha=0.84
dispersion_ratio(0.84, 0.9)              # provenance bias sigma_z,mig/sigma_z,all
slope_in_lsun_per_kpc(SolarNeighbourhood(), 1.0)  # structural slope
```

Every public function is covered by the test suite (100% coverage, `uv run pytest`).
