/**
 * The structural J_R-h_Z slope and its age running, mirroring
 * `experiments.slope` of the Python package (Section 5 of the paper).
 *
 * Units: G in pc (km/s)^2 / Msun, surface density in Msun/pc^2, the epicyclic
 * frequency in (km/s)/pc and the dispersions in km/s; the slope is then in km/s,
 * an action per unit length, and is converted to L_sun/kpc with L_sun = R0 V0.
 */

/** Gravitational constant in pc (km/s)^2 / Msun. */
export const G_PC = 4.30091e-3

/** Solar-neighborhood inputs of the structural slope. */
export interface SolarNeighborhood {
  /** Total dynamical surface density within about one scale height, Msun/pc^2. */
  readonly surfaceDensity: number
  /** Epicyclic frequency at R0, (km/s)/pc. */
  readonly kappa: number
  /** Radial velocity dispersion of the spiral population, km/s. */
  readonly sigmaR: number
  /** Vertical velocity dispersion of the same population, km/s. */
  readonly sigmaZ: number
  /** Solar galactocentric radius, kpc. */
  readonly r0: number
  /** Circular speed at R0, km/s. */
  readonly v0: number
}

/** The default inputs of the paper. */
export const SOLAR_NEIGHBORHOOD: SolarNeighborhood = {
  surfaceDensity: 50,
  kappa: 0.037,
  sigmaR: 35,
  sigmaZ: 18,
  r0: 8.2,
  v0: 233
}

/** Isothermal self-gravitating-sheet scale height h_Z = sigma_z^2 / (pi G Sigma), in pc. */
export function scaleHeight(sigmaZ: number, surfaceDensity: number): number {
  return (sigmaZ * sigmaZ) / (Math.PI * G_PC * surfaceDensity)
}

/** Characteristic spiral-arm radial action c_max sigma_R^2 / kappa, in pc km/s. */
export function radialActionScale(sigmaR: number, kappa: number, cMax: number): number {
  return (cMax * sigmaR * sigmaR) / kappa
}

/** Structural slope a = J_R^max / h_Z in km/s, Equation (15). */
export function structuralSlope(env: SolarNeighborhood, cMax: number): number {
  return (
    radialActionScale(env.sigmaR, env.kappa, cMax) / scaleHeight(env.sigmaZ, env.surfaceDensity)
  )
}

/** The slope in L_sun/kpc, with L_sun = R0 V0 the solar angular momentum. */
export function slopeInSolarUnits(env: SolarNeighborhood, cMax: number): number {
  return structuralSlope(env, cMax) / (env.r0 * env.v0)
}

/** Slope ratio a(age) / a(ref) = (age/ref)^{2 (beta_R - beta_z)}, Equation (16). */
export function slopeAgeFactor(
  ageGyr: number,
  referenceGyr: number,
  betaR: number,
  betaZ: number
): number {
  return (ageGyr / referenceGyr) ** (2 * (betaR - betaZ))
}
