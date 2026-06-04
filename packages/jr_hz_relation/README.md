# jr_hz_relation

The Python engine for the analytic provenance bias and the spiral J_R-h_Z
relation. See the repository README and `packages/pre-print/` for the science.

- `sheet.py` -- isothermal-sheet vertical orbit structure (J_z, nu_z, turning point).
- `form_factor.py` -- the vertical form factor F(J_z,k), the Daniel-Wyse capture
  weight, and the provenance bias sigma_z,mig/sigma_z,all.
- `slope.py` -- the structural J_R-h_Z slope and its age-running.
- `figures.py`, `cli.py` -- publication figures and the command line.

```bash
uv run pytest
uv run jr-hz-relation figures --outdir packages/pre-print
```
