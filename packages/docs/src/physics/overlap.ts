/**
 * Chirikov overlap of two corotation resonances for a flat rotation curve,
 * mirroring `experiments.overlap` of the Python package (Section 4 and Table 1
 * of the paper).
 */

/** Milky Way circular speed (km/s). */
export const MW_VCIRC = 230

/** Fiducial bar pattern speed (km/s/kpc). */
export const MW_BAR_PATTERN_SPEED = 38

/** Fiducial spiral pattern speed (km/s/kpc). */
export const MW_SPIRAL_PATTERN_SPEED = 20

/** Corotation radius R_CR = V_c / Omega_p of a flat rotation curve, in kpc. */
export function corotationRadius(patternSpeed: number, circularSpeed = MW_VCIRC): number {
  return circularSpeed / patternSpeed
}

/** Libration half-width dR = 2 R sqrt(epsilon G F) in kpc, Equation (10). */
export function librationHalfWidth(
  radius: number,
  strength: number,
  radialFactor = 1,
  formFactor = 1
): number {
  return 2 * radius * Math.sqrt(strength * radialFactor * formFactor)
}

/** The overlap parameter S = (dR_in + dR_out) / (R_out - R_in) of Equation (11). */
export function overlapParameter(
  innerRadius: number,
  outerRadius: number,
  strength: number,
  radialFactor = 1,
  formFactor = 1
): number {
  const inner = librationHalfWidth(innerRadius, strength, radialFactor, formFactor)
  const outer = librationHalfWidth(outerRadius, strength, radialFactor, formFactor)
  return (inner + outer) / (outerRadius - innerRadius)
}

/** The same overlap parameter from the two pattern speeds, in km/s/kpc. */
export function overlapFromPatternSpeeds(
  innerSpeed: number,
  outerSpeed: number,
  strength: number,
  radialFactor = 1,
  formFactor = 1
): number {
  return (
    2 *
    Math.sqrt(strength * radialFactor * formFactor) *
    ((innerSpeed + outerSpeed) / (innerSpeed - outerSpeed))
  )
}

/** A measured pattern speed of Table 1 of the paper. */
export interface PatternSpeed {
  readonly label: string
  readonly value: number
  readonly uncertainty: number
}

/** The bar pattern speeds of Table 1 (km/s/kpc). */
export const BAR_PATTERN_SPEEDS: readonly PatternSpeed[] = [
  { label: 'Horta et al. 2025', value: 24, uncertainty: 3 },
  { label: 'Clarke and Gerhard 2022', value: 33.3, uncertainty: 1.8 },
  { label: 'fiducial', value: 38, uncertainty: 0 },
  { label: 'Portail et al. 2017', value: 39.0, uncertainty: 3.5 },
  { label: 'Sanders et al. 2019; Bovy et al. 2019', value: 41, uncertainty: 3 }
]

/** The spiral pattern speeds of Table 1 (km/s/kpc). */
export const SPIRAL_PATTERN_SPEEDS: readonly PatternSpeed[] = [
  { label: 'Castro-Ginard et al. 2021', value: 17.8, uncertainty: 3.0 },
  { label: 'fiducial', value: 20, uncertainty: 0 },
  { label: 'Dias et al. 2019', value: 28.2, uncertainty: 2.1 }
]
