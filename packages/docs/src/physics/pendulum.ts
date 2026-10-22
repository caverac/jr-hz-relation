/**
 * The corotation pendulum of Section 3 and the two-resonance system of
 * Section 4, integrated with a symplectic leapfrog.
 *
 * The slow Hamiltonian is H = (1/2) g p^2 + Psi cos(theta) in the slow action
 * p = L_z - L_CR and the phase theta of the star relative to the pattern. For a
 * flat or declining rotation curve g = dOmega/dL_z is negative, so the stable
 * fixed point sits at theta = 0, where the perturbation Psi cos(theta) is largest,
 * the analog of the Lagrange points L4 and L5 in the inter-arm region at
 * corotation, and the unstable one at theta = pi, on the arm. The libration island
 * has half-width 2 sqrt(Psi/|g|) in p whatever the sign of g; the paper's
 * Appendix B writes the separatrix with sin(theta/2) after the shift
 * theta -> theta + pi, which places the island at pi instead. Here |g| is written
 * out and the island is at theta = 0.
 */

export interface PendulumState {
  readonly theta: number
  readonly p: number
}

/** The pendulum parameters: coupling Psi and the magnitude |g| of the curvature. */
export interface Pendulum {
  readonly psi: number
  readonly gAbs: number
}

/** A second wave of the same amplitude, Psi cos(theta + omega t), for the overlap map. */
export interface Drive {
  readonly omega: number
}

/** The Hamiltonian -(1/2)|g| p^2 + Psi cos(theta). */
export function hamiltonian(state: PendulumState, pendulum: Pendulum): number {
  return -0.5 * pendulum.gAbs * state.p * state.p + pendulum.psi * Math.cos(state.theta)
}

/** Half-width 2 sqrt(Psi/|g|) of the libration island in p, Equation (7). */
export function islandHalfWidth(pendulum: Pendulum): number {
  return 2 * Math.sqrt(pendulum.psi / pendulum.gAbs)
}

/** The separatrix |p| = 2 sqrt(Psi/|g|) |cos(theta/2)| through the unstable point at pi. */
export function separatrix(theta: number, pendulum: Pendulum): number {
  return islandHalfWidth(pendulum) * Math.abs(Math.cos(theta / 2))
}

/** Small-amplitude libration frequency sqrt(|g| Psi) about theta = 0. */
export function librationFrequency(pendulum: Pendulum): number {
  return Math.sqrt(pendulum.gAbs * pendulum.psi)
}

/** Whether a state lies inside the separatrix, that is, on a librating orbit. */
export function isTrapped(state: PendulumState, pendulum: Pendulum): boolean {
  return hamiltonian(state, pendulum) > -pendulum.psi
}

/** Reduce an angle to (-pi, pi]. */
export function wrapAngle(theta: number): number {
  const twoPi = 2 * Math.PI
  let wrapped = theta % twoPi
  if (wrapped > Math.PI) {
    wrapped -= twoPi
  } else if (wrapped <= -Math.PI) {
    wrapped += twoPi
  }
  return wrapped
}

/** The force -dH/dtheta = Psi sin(theta), plus the drive when present. */
function force(theta: number, time: number, pendulum: Pendulum, drive?: Drive): number {
  const own = pendulum.psi * Math.sin(theta)
  if (drive === undefined) {
    return own
  }
  return own + pendulum.psi * Math.sin(theta + drive.omega * time)
}

/**
 * One kick-drift-kick leapfrog step. The equations are theta' = dH/dp = -|g| p
 * and p' = -dH/dtheta = Psi sin(theta) [+ Psi sin(theta + omega t)].
 */
export function step(
  state: PendulumState,
  time: number,
  dt: number,
  pendulum: Pendulum,
  drive?: Drive
): PendulumState {
  let p = state.p + 0.5 * dt * force(state.theta, time, pendulum, drive)
  const theta = state.theta - dt * pendulum.gAbs * p
  p += 0.5 * dt * force(theta, time + dt, pendulum, drive)
  return { theta, p }
}

/** A sampled trajectory of the autonomous pendulum. */
export function trajectory(
  start: PendulumState,
  pendulum: Pendulum,
  dt: number,
  steps: number
): PendulumState[] {
  const points: PendulumState[] = [start]
  let state = start
  for (let i = 0; i < steps; i += 1) {
    state = step(state, i * dt, dt, pendulum)
    points.push(state)
  }
  return points
}

/**
 * A level curve H = level of the pendulum as the two branches
 * p = +/- sqrt(2 (Psi cos(theta) - level) / |g|), sampled where they exist.
 * Returns the upper branch; the lower one is its mirror image in p.
 */
export function levelCurve(level: number, pendulum: Pendulum, samples: number): PendulumState[] {
  const points: PendulumState[] = []
  for (let i = 0; i <= samples; i += 1) {
    const theta = -Math.PI + (2 * Math.PI * i) / samples
    const square = (2 * (pendulum.psi * Math.cos(theta) - level)) / pendulum.gAbs
    if (square >= 0) {
      points.push({ theta, p: Math.sqrt(square) })
    }
  }
  return points
}

/** Options of the stroboscopic map of the two-resonance system. */
export interface StrobeOptions {
  /** Chirikov overlap S = (sum of the two half-widths) / (their separation). */
  readonly overlap: number
  /** Number of initial conditions. */
  readonly orbits: number
  /** Number of drive periods followed per orbit. */
  readonly periods: number
  /** Leapfrog steps per drive period. */
  readonly stepsPerPeriod: number
}

/**
 * The two-resonance system of the primer, H = -(1/2) p^2 + Psi [cos(theta) +
 * cos(theta + t)] in units |g| = omega = 1, whose resonances sit at p = 0 and
 * p = 1 with half-widths 2 sqrt(Psi) each, so that S = 4 sqrt(Psi). The state is
 * sampled once per drive period, at t = 2 pi n, and the points of each orbit are
 * returned together with their starting momentum.
 */
export function strobeMap(options: StrobeOptions): PendulumState[][] {
  const psi = (options.overlap / 4) ** 2
  const pendulum: Pendulum = { psi, gAbs: 1 }
  const drive: Drive = { omega: 1 }
  const dt = (2 * Math.PI) / options.stepsPerPeriod
  const result: PendulumState[][] = []
  for (let orbit = 0; orbit < options.orbits; orbit += 1) {
    // Starting momenta from below the lower resonance to above the upper one,
    // alternating the starting phase between the two fixed points.
    const fraction = (orbit + 0.5) / options.orbits
    let state: PendulumState = {
      theta: orbit % 2 === 0 ? 0 : Math.PI,
      p: -0.8 + 2.6 * fraction
    }
    const points: PendulumState[] = [state]
    let time = 0
    for (let period = 0; period < options.periods; period += 1) {
      for (let i = 0; i < options.stepsPerPeriod; i += 1) {
        state = step(state, time, dt, pendulum, drive)
        time += dt
      }
      points.push({ theta: wrapAngle(state.theta), p: state.p })
    }
    result.push(points)
  }
  return result
}
