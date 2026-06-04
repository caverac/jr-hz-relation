---
sidebar_position: 1
title: Usage
---

# Using the library

The `jr_hz_relation` package implements every result here.

```bash
uv run jr-hz-relation form-factor --energy 1.0 --alpha 0.84
uv run jr-hz-relation bias --alpha 0.84 --strength 0.9
uv run jr-hz-relation anchor --alpha 0.84 --target 0.80
uv run jr-hz-relation slope --c-max 1.0
uv run jr-hz-relation age-running --age 8 --ref 1 --beta-r 0.35 --beta-z 0.5
uv run jr-hz-relation figures --outdir packages/pre-print
```

From Python:

```python
from jr_hz_relation import vertical_form_factor, dispersion_ratio, slope_in_lsun_per_kpc, SolarNeighbourhood

vertical_form_factor(1.0, 0.84)          # form factor at E=1, alpha=0.84
dispersion_ratio(0.84, 0.9)              # provenance bias sigma_z,mig/sigma_z,all
slope_in_lsun_per_kpc(SolarNeighbourhood(), 1.0)  # structural slope
```

Every public function is covered by the test suite (100% coverage, `uv run pytest`).
