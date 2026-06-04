# jr-hz-relation

An analytic theory of the **provenance bias** in radial migration, and its link to
the spiral-arm radial-action / disc vertical-scale-height relation.

Radial migration preferentially churns vertically-cold stars -- the *provenance
bias* established in N-body by Vera-Ciro, D'Onghia & Navarro (2016) and Mikkola,
McMillan & Hobbs (2020), and explained there only qualitatively. This project
writes the mechanism down: a **vertical form factor**

```
F(J_z, k) = < e^{-k|z(theta_z, J_z)|} >_{theta_z}
```

the angle-average over a star's vertical orbit of the spiral potential's
`e^{-k|z|}` fall-off above the plane. Inserting `F` into the Daniel & Wyse (2015,
2018) corotation-capture criterion yields the provenance bias from first
principles, and ties the same `F(k h_Z)` to the empirical spiral-arm
`J_R^max`-`h_Z` relation (Palicio et al. 2024).

## Layout

- `packages/jr_hz_relation/` -- the Python engine (form factor, capture weight,
  bias, structural slope, figures, CLI) with a full test suite (100% coverage,
  no lint exceptions).
- `packages/pre-print/` -- the MNRAS LaTeX pre-print and its figures.
- `notebooks/` -- the local-only research record (logs, notes, memory); git-ignored.

## Toolchain

`mise` pins Python 3.14 (target 3.15; see `.mise.toml`), Node 25, and `uv`. Python deps are a `uv` workspace.

```bash
mise install
uv sync
uv run pytest                       # tests + 100% coverage gate
uv run jr-hz-relation figures --outdir packages/pre-print
make -C packages/pre-print          # build the pre-print PDF
```

## Rules

Strict typing (`mypy --strict`), numpy-style docstrings, `black`/`isort`,
`flake8`, and `pylint` all run clean with **no rule disabled anywhere**. The
single-letter physics symbols (`F`, `k`, `z`, `E`, ...) are whitelisted in the
pylint configuration, which tunes the naming rule rather than disabling it.
