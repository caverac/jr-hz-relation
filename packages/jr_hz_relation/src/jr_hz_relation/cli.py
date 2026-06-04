"""Command-line interface for the provenance-bias analysis.

Subcommands expose the form factor, the provenance bias, the structural slope and
its age-running, and figure generation::

    jr-hz-relation form-factor --energy 1.0 --alpha 0.84
    jr-hz-relation bias --alpha 0.84 --strength 0.9
    jr-hz-relation slope --c-max 1.0
    jr-hz-relation age-running --age 8 --ref 1 --beta-r 0.35 --beta-z 0.5
    jr-hz-relation figures --outdir packages/pre-print
"""

from __future__ import annotations

import argparse
from pathlib import Path

from jr_hz_relation.figures import make_all_figures
from jr_hz_relation.form_factor import dispersion_ratio, strength_matching_anchor, vertical_form_factor
from jr_hz_relation.slope import AVRExponents, SolarNeighbourhood, slope_age_factor, slope_in_lsun_per_kpc


def _cmd_form_factor(args: argparse.Namespace) -> int:
    """Print the vertical form factor at a given energy and wavenumber."""
    value = vertical_form_factor(args.energy, args.alpha)
    print(f"F(E={args.energy:.3f}, alpha={args.alpha:.3f}) = {value:.4f}")
    return 0


def _cmd_bias(args: argparse.Namespace) -> int:
    """Print the predicted provenance bias at a given thickness and spiral strength."""
    ratio = dispersion_ratio(args.alpha, args.strength)
    print(f"sigma_z,mig/sigma_z,all(alpha={args.alpha:.3f}, s={args.strength:.3f}) = {ratio:.4f}")
    print(f"=> {100.0 * (1.0 - ratio):.1f}% colder migrators")
    return 0


def _cmd_slope(args: argparse.Namespace) -> int:
    """Print the structural slope in L_sun/kpc for the default solar neighbourhood."""
    env = SolarNeighbourhood()
    slope = slope_in_lsun_per_kpc(env, args.c_max)
    print(f"structural slope (c_max={args.c_max:.2f}) = {slope:.3e} L_sun/kpc")
    print("Palicio+2024 measured = 3.69e-2 L_sun/kpc")
    return 0


def _cmd_age_running(args: argparse.Namespace) -> int:
    """Print the slope age-running factor between two ages."""
    avr = AVRExponents(args.beta_r, args.beta_z)
    factor = slope_age_factor(args.age, args.ref, avr)
    print(f"2(beta_R - beta_z) = {avr.slope_exponent:+.3f}")
    print(f"a({args.age:g} Gyr)/a({args.ref:g} Gyr) = {factor:.3f}")
    return 0


def _cmd_anchor(args: argparse.Namespace) -> int:
    """Print the spiral strength that reproduces the measured Milky-Way bias."""
    strength = strength_matching_anchor(args.alpha, args.target)
    print(f"spiral strength matching ratio {args.target:.2f} at alpha={args.alpha:.2f}: s={strength:.3f}")
    return 0


def _cmd_figures(args: argparse.Namespace) -> int:
    """Generate the PDF figure set."""
    for name, path in make_all_figures(Path(args.outdir)).items():
        print(f"{name}: {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands.

    Returns
    -------
    argparse.ArgumentParser
        The configured parser.
    """
    parser = argparse.ArgumentParser(prog="jr-hz-relation", description=__doc__)
    sub = parser.add_subparsers(dest="command")

    form = sub.add_parser("form-factor", help="vertical form factor F(E; alpha)")
    form.add_argument("--energy", type=float, default=1.0)
    form.add_argument("--alpha", type=float, default=0.84)
    form.set_defaults(func=_cmd_form_factor)

    bias = sub.add_parser("bias", help="provenance bias sigma_z,mig/sigma_z,all")
    bias.add_argument("--alpha", type=float, default=0.84)
    bias.add_argument("--strength", type=float, default=0.9)
    bias.set_defaults(func=_cmd_bias)

    slope = sub.add_parser("slope", help="structural J_R-h_Z slope")
    slope.add_argument("--c-max", type=float, default=1.0, dest="c_max")
    slope.set_defaults(func=_cmd_slope)

    age = sub.add_parser("age-running", help="slope age-running factor")
    age.add_argument("--age", type=float, default=8.0)
    age.add_argument("--ref", type=float, default=1.0)
    age.add_argument("--beta-r", type=float, default=0.35, dest="beta_r")
    age.add_argument("--beta-z", type=float, default=0.50, dest="beta_z")
    age.set_defaults(func=_cmd_age_running)

    anchor = sub.add_parser("anchor", help="spiral strength matching a target bias")
    anchor.add_argument("--alpha", type=float, default=0.84)
    anchor.add_argument("--target", type=float, default=0.80)
    anchor.set_defaults(func=_cmd_anchor)

    figs = sub.add_parser("figures", help="generate the PDF figure set")
    figs.add_argument("--outdir", default="build/figures")
    figs.set_defaults(func=_cmd_figures)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the selected subcommand.

    Parameters
    ----------
    argv :
        Optional argument vector (defaults to ``sys.argv``).

    Returns
    -------
    int
        Process exit code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "func", None) is None:
        parser.print_help()
        return 1
    return int(args.func(args))
