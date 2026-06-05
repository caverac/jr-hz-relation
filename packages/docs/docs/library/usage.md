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
uv run experiments anchor --alpha 0.84 --target 0.80
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

From Python:

```python
from experiments import vertical_form_factor, dispersion_ratio, slope_in_lsun_per_kpc, SolarNeighbourhood

vertical_form_factor(1.0, 0.84)          # form factor at E=1, alpha=0.84
dispersion_ratio(0.84, 0.9)              # provenance bias sigma_z,mig/sigma_z,all
slope_in_lsun_per_kpc(SolarNeighbourhood(), 1.0)  # structural slope
```

Every public function is covered by the test suite (100% coverage, `uv run pytest`).
