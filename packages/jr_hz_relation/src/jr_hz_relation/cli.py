"""Command-line interface for the provenance-bias analysis.

Subcommands expose the form factor, the provenance bias, the structural slope and
its age-running, and figure generation::

    jr-hz-relation form-factor --energy 1.0 --alpha 0.84
    jr-hz-relation bias --alpha 0.84 --strength 0.9
    jr-hz-relation slope --c-max 1.0
    jr-hz-relation age-running --age 8 --ref 1 --beta-r 0.35 --beta-z 0.5
    jr-hz-relation trapping --alpha 0.84 --island-width 1.0
    jr-hz-relation crossover --alpha 0.84 --overlap 2.0
    jr-hz-relation thickness --alpha 0.84 --thickness 0.5
    jr-hz-relation diffusion --alpha 0.84 --broadening 3.0
    jr-hz-relation overlap --strength 0.02 --form-factor 1.0
    jr-hz-relation figures --outdir packages/pre-print
"""

from __future__ import annotations

import argparse
from pathlib import Path

from jr_hz_relation.balescu_lenard import bl_dispersion_ratio
from jr_hz_relation.crossover import crossover_dispersion_ratio
from jr_hz_relation.figures import make_all_figures
from jr_hz_relation.form_factor import dispersion_ratio, strength_matching_anchor, vertical_form_factor
from jr_hz_relation.overlap import milky_way_overlap
from jr_hz_relation.slope import AVRExponents, SolarNeighbourhood, slope_age_factor, slope_in_lsun_per_kpc
from jr_hz_relation.thickness import softened_dispersion_ratio
from jr_hz_relation.trapping import trapping_dispersion_ratio


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


def _cmd_trapping(args: argparse.Namespace) -> int:
    """Print the provenance bias from the exact corotation trapped fraction."""
    ratio = trapping_dispersion_ratio(args.alpha, args.island_width)
    print(f"trapped-fraction bias(alpha={args.alpha:.3f}, kappa={args.island_width:.3f}): ratio={ratio:.4f}")
    print(f"=> {100.0 * (1.0 - ratio):.1f}% colder (single-resonance; capped near 7% at the MW thickness)")
    return 0


def _cmd_crossover(args: argparse.Namespace) -> int:
    """Print the provenance bias from the trapping-to-diffusion crossover weight."""
    ratio = crossover_dispersion_ratio(args.alpha, args.overlap)
    print(f"crossover bias(alpha={args.alpha:.3f}, S0={args.overlap:.3f}): ratio={ratio:.4f}")
    print(f"=> {100.0 * (1.0 - ratio):.1f}% colder (between the 7% trapping floor and 24% diffusion ceiling)")
    return 0


def _cmd_diffusion(args: argparse.Namespace) -> int:
    """Print the diffusive provenance bias from the Balescu-Lenard weight."""
    ratio = bl_dispersion_ratio(args.alpha, args.broadening)
    print(f"Balescu-Lenard bias(alpha={args.alpha:.3f}, b={args.broadening:.3f}): ratio={ratio:.4f}")
    print(f"=> {100.0 * (1.0 - ratio):.1f}% colder (diffusive band ~19-24%, derived; F^2 at b=0, F^1.5 at large b)")
    return 0


def _cmd_thickness(args: argparse.Namespace) -> int:
    """Print the single-resonance bias with the finite-thickness form factor."""
    ratio = softened_dispersion_ratio(args.alpha, args.thickness)
    print(f"finite-thickness bias(alpha={args.alpha:.3f}, h={args.thickness:.3f}): ratio={ratio:.4f}")
    print(f"=> {100.0 * (1.0 - ratio):.1f}% colder (razor-thin h=0 gives ~7%; softens as the spiral thickens)")
    return 0


def _cmd_overlap(args: argparse.Namespace) -> int:
    """Print the Milky Way bar-spiral Chirikov overlap parameter."""
    overlap = milky_way_overlap(args.strength, form_factor=args.form_factor)
    regime = "overlap (diffusive)" if overlap >= 1.0 else "regular (trapping)"
    print(f"S(eps={args.strength:.3f}, F={args.form_factor:.2f}) = {overlap:.3f} -> {regime}")
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

    trapping = sub.add_parser("trapping", help="provenance bias from the exact trapped fraction")
    trapping.add_argument("--alpha", type=float, default=0.84)
    trapping.add_argument("--island-width", type=float, default=1.0, dest="island_width")
    trapping.set_defaults(func=_cmd_trapping)

    crossover = sub.add_parser("crossover", help="provenance bias across the overlap transition")
    crossover.add_argument("--alpha", type=float, default=0.84)
    crossover.add_argument("--overlap", type=float, default=2.0)
    crossover.set_defaults(func=_cmd_crossover)

    thickness = sub.add_parser("thickness", help="single-resonance bias with finite spiral thickness")
    thickness.add_argument("--alpha", type=float, default=0.84)
    thickness.add_argument("--thickness", type=float, default=0.5)
    thickness.set_defaults(func=_cmd_thickness)

    diffusion = sub.add_parser("diffusion", help="diffusive bias from the Balescu-Lenard weight")
    diffusion.add_argument("--alpha", type=float, default=0.84)
    diffusion.add_argument("--broadening", type=float, default=3.0)
    diffusion.set_defaults(func=_cmd_diffusion)

    overlap = sub.add_parser("overlap", help="bar-spiral Chirikov resonance overlap")
    overlap.add_argument("--strength", type=float, default=0.02)
    overlap.add_argument("--form-factor", type=float, default=1.0, dest="form_factor")
    overlap.set_defaults(func=_cmd_overlap)

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
