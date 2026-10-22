/**
 * The self-consistent isothermal sheet and the vertical form factor, in the
 * dimensionless units G = sigma_z = z0 = 1 of the paper (Spitzer 1942). The
 * potential is Phi(z) = 2 ln cosh z, the density rho0 sech^2 z with
 * rho0 = 1/(2 pi), and the small-amplitude vertical frequency is sqrt(2).
 *
 * This module mirrors `experiments.sheet`, `experiments.form_factor`,
 * `experiments.trapping`, `experiments.crossover`, `experiments.balescu_lenard`
 * and `experiments.thickness` of the Python package, so that the interactive
 * figures draw the same curves as the static ones. It imports nothing, so the
 * same file runs under Node for the cross-check against the Python values.
 */

/** Small-amplitude (midplane) vertical frequency nu_max = sqrt(4 pi G rho0). */
export const NU_MAX = Math.SQRT2

/** Thickness alpha = k z0 of the Milky Way adopted in the paper. */
export const MILKY_WAY_ALPHA = 0.84

/** Lowest energy of the quadrature grid of the dispersion ratios. */
const ENERGY_FLOOR = 1e-3

const GAUSS_ORDER = 24
const GAUSS_PANELS = 8

interface Quadrature {
  readonly nodes: readonly number[]
  readonly weights: readonly number[]
}

/** Gauss-Legendre nodes and weights on [-1, 1], by Newton iteration on P_n. */
function gaussLegendre(order: number): Quadrature {
  const nodes = new Array<number>(order).fill(0)
  const weights = new Array<number>(order).fill(0)
  const half = Math.floor((order + 1) / 2)
  for (let i = 0; i < half; i += 1) {
    let z = Math.cos((Math.PI * (i + 0.75)) / (order + 0.5))
    let derivative = 0
    for (let iteration = 0; iteration < 100; iteration += 1) {
      let p1 = 1
      let p2 = 0
      for (let j = 1; j <= order; j += 1) {
        const p3 = p2
        p2 = p1
        p1 = ((2 * j - 1) * z * p2 - (j - 1) * p3) / j
      }
      derivative = (order * (z * p1 - p2)) / (z * z - 1)
      const previous = z
      z = previous - p1 / derivative
      if (Math.abs(z - previous) < 1e-15) {
        break
      }
    }
    nodes[i] = -z
    nodes[order - 1 - i] = z
    const weight = 2 / ((1 - z * z) * derivative * derivative)
    weights[i] = weight
    weights[order - 1 - i] = weight
  }
  return { nodes, weights }
}

const GAUSS = gaussLegendre(GAUSS_ORDER)

/** Composite Gauss-Legendre integral of `f` over [a, b]. */
export function integrate(f: (x: number) => number, a: number, b: number): number {
  const width = (b - a) / GAUSS_PANELS
  let total = 0
  for (let panel = 0; panel < GAUSS_PANELS; panel += 1) {
    const left = a + panel * width
    const center = left + width / 2
    const scale = width / 2
    for (let i = 0; i < GAUSS_ORDER; i += 1) {
      total += GAUSS.weights[i] * f(center + scale * GAUSS.nodes[i])
    }
  }
  return total * (width / 2)
}

/** Vertical potential of the isothermal sheet, Phi(z) = 2 ln cosh z. */
export function potential(z: number): number {
  return 2 * Math.log(Math.cosh(z))
}

/** Vertical acceleration -dPhi/dz = -2 tanh z. */
export function acceleration(z: number): number {
  return -2 * Math.tanh(z)
}

/** Equilibrium density rho(z) = rho0 sech^2 z with rho0 = 1/(2 pi). */
export function density(z: number): number {
  const sech = 1 / Math.cosh(z)
  return (sech * sech) / (2 * Math.PI)
}

/** Turning point z_m with Phi(z_m) = E_z, for a strictly positive energy. */
export function turningPoint(energy: number): number {
  if (energy <= 0) {
    throw new RangeError('energy must be positive')
  }
  return Math.acosh(Math.exp(energy / 2))
}

/**
 * Integral over the upward quarter of the orbit, with the substitution
 * z = z_m sin(phi) that removes the inverse-square-root singularity of 1/|v_z|
 * at the turning point. `weight(z)` multiplies the time element dz/|v_z|.
 */
function quarterTimeIntegral(energy: number, weight: (z: number) => number): number {
  const zMax = turningPoint(energy)
  return integrate(
    (phi) => {
      const z = zMax * Math.sin(phi)
      const kinetic = Math.max(2 * (energy - potential(z)), 0)
      const speed = Math.sqrt(kinetic)
      if (speed === 0) {
        // The limit of cos(phi)/|v_z| at the turning point is finite; the nodes
        // never sit on it, so this guards only against underflow.
        return 0
      }
      return (weight(z) * zMax * Math.cos(phi)) / speed
    },
    0,
    Math.PI / 2
  )
}

/** Vertical frequency nu_z(E_z) = 2 pi / T from the quarter-period quadrature. */
export function verticalFrequency(energy: number): number {
  const quarter = quarterTimeIntegral(energy, () => 1)
  return (2 * Math.PI) / (4 * quarter)
}

/** Vertical action J_z(E_z) = (1/pi) INT |v_z| dz = (2/pi) INT_0^{z_m} v_z dz. */
export function verticalAction(energy: number): number {
  const zMax = turningPoint(energy)
  const integral = integrate(
    (phi) => {
      const z = zMax * Math.sin(phi)
      const kinetic = Math.max(2 * (energy - potential(z)), 0)
      return Math.sqrt(kinetic) * zMax * Math.cos(phi)
    },
    0,
    Math.PI / 2
  )
  return (2 / Math.PI) * integral
}

/**
 * Vertical form factor F(E_z; alpha) = <exp(-alpha |z|)> over the orbit,
 * Equation (1) of the paper: (2/pi) nu_z INT_0^{z_m} exp(-alpha z) dz / |v_z|.
 */
export function verticalFormFactor(energy: number, alpha: number): number {
  if (alpha < 0) {
    throw new RangeError('alpha must be non-negative')
  }
  const quarter = quarterTimeIntegral(energy, (z) => Math.exp(-alpha * z))
  return (2 / Math.PI) * verticalFrequency(energy) * quarter
}

/**
 * Finite-thickness form factor of Equation (2),
 * F_soft = [F(alpha) - alpha h F(1/h)] / (1 - alpha h), for an arm whose vertical
 * profile is exponential with scale h in disk scale heights; h = 0 is razor-thin.
 */
export function softenedFormFactor(energy: number, alpha: number, thickness: number): number {
  if (thickness < 0) {
    throw new RangeError('thickness must be non-negative')
  }
  if (thickness === 0) {
    return verticalFormFactor(energy, alpha)
  }
  let h = thickness
  let product = alpha * h
  if (Math.abs(1 - product) < 1e-6) {
    // The beta = k degeneracy is removable; a negligible nudge avoids the 0/0.
    h *= 1 + 1e-4
    product = alpha * h
  }
  const bare = verticalFormFactor(energy, alpha)
  const deep = verticalFormFactor(energy, 1 / h)
  return (bare - product * deep) / (1 - product)
}

/** Softened kernel K(z) of Section 2, normalized to K(0) = 1. */
export function softenedKernel(z: number, alpha: number, thickness: number): number {
  if (thickness === 0) {
    return Math.exp(-alpha * Math.abs(z))
  }
  const beta = 1 / thickness
  const height = Math.abs(z)
  return (beta * Math.exp(-alpha * height) - alpha * Math.exp(-beta * height)) / (beta - alpha)
}

/**
 * Error function. The Maclaurin series up to |x| = 3, where its terms stay
 * below 4e3 and the cancellation costs four digits, and the continued fraction
 * of the complement beyond, which converges in a few dozen terms there.
 */
export function erf(x: number): number {
  const magnitude = Math.abs(x)
  if (magnitude > 3) {
    return x > 0 ? 1 - erfc(magnitude) : erfc(magnitude) - 1
  }
  const square = x * x
  let term = x
  let sum = x
  for (let n = 1; n < 200; n += 1) {
    term *= -square / n
    const contribution = term / (2 * n + 1)
    sum += contribution
    if (Math.abs(contribution) < 1e-17 * Math.abs(sum)) {
      break
    }
  }
  return (2 / Math.sqrt(Math.PI)) * sum
}

/** Complementary error function erfc(x) = 1 - erf(x). */
export function erfc(x: number): number {
  if (x <= 3) {
    return 1 - erf(x)
  }
  // sqrt(pi) exp(x^2) erfc(x) = 1 / (x + (1/2)/(x + 1/(x + (3/2)/(x + ...)))),
  // evaluated backward from a fixed depth.
  let tail = x
  for (let k = 60; k >= 1; k -= 1) {
    tail = x + k / 2 / tail
  }
  return Math.exp(-x * x) / (Math.sqrt(Math.PI) * tail)
}

/** A migration weight as a function of the form factor F in (0, 1]. */
export type Weight = (formFactor: number) => number

/** Boltzmann capture weight W = exp[-s (1/F - 1)] of Equation (14). */
export function captureWeight(spiralStrength: number): Weight {
  return (formFactor) => Math.exp(-spiralStrength * (1 / formFactor - 1))
}

/** Power-law weight W = F^p; p = 1/2 is trapping, 1 the |dL_z| rule, 2 the (dL_z)^2 rule. */
export function powerWeight(exponent: number): Weight {
  return (formFactor) => Math.max(formFactor, 1e-12) ** exponent
}

/** Threshold rule W = erfc(lambda / F) for migrators with |dL_z| above a cut. */
export function thresholdWeight(lambda: number): Weight {
  return (formFactor) => erfc(lambda / formFactor)
}

/**
 * Exact trapped fraction of Equation (9),
 * W = (1/pi) INT_0^pi erf(kappa sqrt(F) sin(u) / sqrt 2) du,
 * with kappa the island-width parameter p_max(F = 1) / sigma_p.
 */
export function trappedFraction(formFactor: number, islandWidth: number): number {
  const lambda = islandWidth * Math.sqrt(formFactor)
  const integral = integrate((u) => erf((lambda * Math.sin(u)) / Math.SQRT2), 0, Math.PI)
  return integral / Math.PI
}

/** The trapped fraction as a weight at fixed island width. */
export function trappedWeight(islandWidth: number): Weight {
  return (formFactor) => trappedFraction(formFactor, islandWidth)
}

/** Crossover gate Theta(S) = S^2 / (1 + S^2). */
export function overlapGate(overlap: number): number {
  return (overlap * overlap) / (1 + overlap * overlap)
}

/** Exponent p(S) = 1/2 + (3/2) Theta(S) of the crossover weight. */
export function crossoverExponent(overlap: number): number {
  return 0.5 + 1.5 * overlapGate(overlap)
}

/** Crossover weight W = F^{p(S)} with S = S0 sqrt(F), Equation (12). */
export function crossoverWeight(overlapStrength: number): Weight {
  return (formFactor) => formFactor ** crossoverExponent(overlapStrength * Math.sqrt(formFactor))
}

/** Critical form factor F_crit = 1/S0^2 at the threshold S = 1. */
export function criticalFormFactor(overlapStrength: number): number {
  return 1 / (overlapStrength * overlapStrength)
}

/** Resonance-broadened Balescu-Lenard weight W = F^2 / (1 + b sqrt F), Equation (13). */
export function diffusionWeight(broadening: number): Weight {
  return (formFactor) => (formFactor * formFactor) / (1 + broadening * Math.sqrt(formFactor))
}

/** Uniform grid of n points from a to b, both included. */
export function linspace(a: number, b: number, n: number): number[] {
  const step = (b - a) / (n - 1)
  return Array.from({ length: n }, (_, i) => a + i * step)
}

/** Trapezoidal rule on a grid, as numpy.trapezoid. */
export function trapezoid(values: readonly number[], grid: readonly number[]): number {
  let total = 0
  for (let i = 1; i < grid.length; i += 1) {
    total += ((values[i] + values[i - 1]) / 2) * (grid[i] - grid[i - 1])
  }
  return total
}

/** One row of the vertical distribution used by the dispersion ratios. */
export interface EnergyRow {
  readonly energy: number
  readonly frequency: number
  readonly action: number
  readonly formFactor: number
  /** Equilibrium distribution dN/dE_z ~ exp(-E_z) T(E_z), unnormalized. */
  readonly base: number
}

/**
 * The equilibrium vertical distribution of the sheet on the quadrature grid of
 * the Python package: 120 energies from 1e-3 to 12, dN/dE_z ~ exp(-E_z) 2 pi / nu_z,
 * with the (softened) form factor at thickness alpha evaluated on each row.
 */
export function energyTable(alpha: number, thickness = 0, eMax = 12, n = 120): EnergyRow[] {
  return linspace(ENERGY_FLOOR, eMax, n).map((energy) => {
    const frequency = verticalFrequency(energy)
    return {
      energy,
      frequency,
      action: verticalAction(energy),
      formFactor: softenedFormFactor(energy, alpha, thickness),
      base: Math.exp(-energy) * ((2 * Math.PI) / frequency)
    }
  })
}

/** The reweighting of the vertical distribution by a migration weight. */
export interface Reweighting {
  /** Mean vertical energy of the whole population. */
  readonly meanAll: number
  /** Mean vertical energy of the migrators, the population reweighted by W. */
  readonly meanMigrators: number
  /** Dispersion ratio sigma_z,mig / sigma_z,all = sqrt(meanMigrators / meanAll). */
  readonly ratio: number
  /** The provenance bias ln(sigma_z,mig / sigma_z,all). */
  readonly bias: number
}

/** Reweight a table by a migration weight and form the dispersion ratio. */
export function reweight(table: readonly EnergyRow[], weight: Weight): Reweighting {
  const grid = table.map((row) => row.energy)
  const base = table.map((row) => row.base)
  const weighted = table.map((row) => row.base * weight(row.formFactor))
  const meanAll =
    trapezoid(
      base.map((b, i) => b * grid[i]),
      grid
    ) / trapezoid(base, grid)
  const meanMigrators =
    trapezoid(
      weighted.map((w, i) => w * grid[i]),
      grid
    ) / trapezoid(weighted, grid)
  const ratio = Math.sqrt(meanMigrators / meanAll)
  return { meanAll, meanMigrators, ratio, bias: Math.log(ratio) }
}

/** Provenance bias sigma_z,mig / sigma_z,all at thickness alpha for a weight. */
export function dispersionRatio(alpha: number, weight: Weight, thickness = 0): number {
  return reweight(energyTable(alpha, thickness), weight).ratio
}

/** A sampled vertical orbit of the sheet. */
export interface VerticalOrbit {
  readonly time: number[]
  readonly z: number[]
  readonly velocity: number[]
}

/**
 * Leapfrog integration of the vertical orbit of energy E_z, started at the
 * midplane moving upward, in the sheet's time unit z0 / sigma_z.
 */
export function verticalOrbit(energy: number, dt: number, steps: number): VerticalOrbit {
  const time = new Array<number>(steps + 1)
  const z = new Array<number>(steps + 1)
  const velocity = new Array<number>(steps + 1)
  let height = 0
  let speed = Math.sqrt(2 * energy)
  time[0] = 0
  z[0] = height
  velocity[0] = speed
  for (let i = 1; i <= steps; i += 1) {
    speed += 0.5 * dt * acceleration(height)
    height += dt * speed
    speed += 0.5 * dt * acceleration(height)
    time[i] = i * dt
    z[i] = height
    velocity[i] = speed
  }
  return { time, z, velocity }
}
