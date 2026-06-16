# jr-hz-relation

**An analytic origin for the provenance bias in radial migration.**

> **[Read the full documentation](https://caverac.github.io/jr-hz-relation/)**

Radial migration preferentially churns vertically cold stars -- the _provenance bias_ seen in N-body simulations (Vera-Ciro, D'Onghia & Navarro 2016; Mikkola, McMillan & Hobbs 2020) but so far understood only qualitatively. This project derives it from first principles.

A star's coupling to a spiral of radial wavenumber $k$ is the orbit-average over its vertical motion of the potential's $e^{-k|z|}$ fall-off above the plane -- a **vertical form factor**

$$F(J_z, k) = \langle e^{-k|z(\theta_z, J_z)|} \rangle_{\theta_z},$$

which proves to be the exact vertical coupling of the spiral at corotation, so vertically cold stars are trapped and migrate preferentially. Because $F$ depends on wavenumber and disk thickness only through $\alpha = k\,h_Z$, the same object also fixes the empirical spiral-arm $J_R^{\max}$–$h_Z$ relation (Palicio et al. 2024) -- tying two observables to one piece of physics.

## Table of Contents

- [Packages](#packages)
- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [Command-line interface](#command-line-interface)
- [Quality](#quality)
- [License](#license)

## Packages

| Package                                                                                                | Description                                         |
| ------------------------------------------------------------------------------------------------------ | --------------------------------------------------- |
| [`experiments`](packages/experiments)                                                                  | Core Python engine and CLI                          |
| [`docs`](packages/docs) Project documentation ([live site](https://caverac.github.io/jr-hz-relation/)) |
| [`pre-print`](packages/pre-print)                                                                      | LaTeX source (AASTeX v7) for the accompanying paper |

## Getting Started

This project uses [mise](https://mise.jdx.dev/) to manage tool versions (Python 3.14, Node 25, uv; see `.mise.toml`).

```bash
# Install tool versions
mise install

# Install Python dependencies (uv workspace)
uv sync

# Install JS/TS dependencies (docs site)
yarn install
```

## Documentation

All the physics -- every equation derived from the one before it, with the new results in two appendices -- lives on the [documentation site](https://caverac.github.io/jr-hz-relation/). To run it locally:

```bash
yarn workspace @jr-hz-relation/docs start
```

## Command-line interface

The `experiments` package derives every number and figure in the paper:

```bash
uv run experiments --help          # list all commands
uv run experiments figures         # regenerate the full figure set into assets/figures/
uv run pytest                      # run the tests + 100% coverage gate
make -C packages/pre-print         # sync figures and build the pre-print PDF
```

## License

This project is licensed under the [MIT License](LICENSE).
