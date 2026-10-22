import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Button, Controls, Readout, Slider } from '@site/src/components/viz/Controls'
import {
  makeRandom,
  useAnimationFrame,
  useElementWidth,
  useInView
} from '@site/src/components/viz/hooks'
import {
  type Pendulum,
  type PendulumState,
  isTrapped,
  step,
  wrapAngle
} from '@site/src/physics/pendulum'
import * as d3 from 'd3'
import React, { type ReactNode, useMemo, useRef, useState } from 'react'

/** Number of arms. */
const ARMS = 2

/** Pitch angle of the drawn arms, in radians (15 degrees). */
const PITCH = (15 * Math.PI) / 180

const STARS = 48
const TRAIL = 90
const SUBSTEPS = 3

/** Orbital phase per second: one orbit of the corotation circle in 6 s. */
const SPEED = (2 * Math.PI) / 6

/** Radial window of the drawing, in units of the corotation radius. */
const RADIUS_MIN = 0.45
const RADIUS_MAX = 1.55

interface Star {
  state: PendulumState
  trail: PendulumState[]
  /** Which of the m identical sectors of the pattern the star is drawn in. */
  readonly branch: number
}

const format2 = d3.format('.2f')

/**
 * The pendulum in the units of the drawing. With x = dR/R_CR and time in
 * 1/Omega, the slow Hamiltonian divided by V_c^2 is -(1/2) x^2 + epsilon F cos(theta_r),
 * and the arm number multiplies both rates, so the pendulum of the physics
 * module has psi = m epsilon F and |g| = m.
 */
function pendulumOf(strength: number, formFactor: number): Pendulum {
  return { psi: ARMS * strength * formFactor, gAbs: ARMS }
}

function seedStars(): Star[] {
  const random = makeRandom(11)
  return d3.range(STARS).map((i) => {
    const state: PendulumState = {
      theta: wrapAngle(2 * Math.PI * random() - Math.PI),
      p: -0.42 + 0.84 * random()
    }
    return { state, trail: [state], branch: i % ARMS }
  })
}

/** Position in the pattern frame: azimuth theta_r / m in the star's sector, radius 1 + x. */
function place(state: PendulumState, branch: number): readonly [number, number] {
  const phi = state.theta / ARMS + (2 * Math.PI * branch) / ARMS
  const radius = 1 + state.p
  return [radius * Math.cos(phi), radius * Math.sin(phi)]
}

/**
 * Stars near corotation in the frame that rotates with a two-armed pattern. The
 * arms sit at theta_r = +/- pi, the inter-arm points at theta_r = 0, and each star
 * follows the pendulum of Section 3 mapped to the disk: trapped stars librate
 * about the inter-arm corotation points on horseshoe paths, the others circulate.
 */
export default function RotatingFrame(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const inView = useInView(ref)
  const [strength, setStrength] = useState(0.02)
  const [formFactor, setFormFactor] = useState(1)
  const [playing, setPlaying] = useState(true)
  const pendulum = useMemo(() => pendulumOf(strength, formFactor), [strength, formFactor])
  const stars = useRef<Star[]>(seedStars())
  const [frame, setFrame] = useState<Star[]>(() => stars.current.map((s) => ({ ...s })))
  const clock = useRef(0)

  const reset = (): void => {
    stars.current = seedStars()
    clock.current = 0
    setFrame(stars.current.map((s) => ({ ...s })))
  }

  useAnimationFrame(playing && inView, (dt) => {
    const h = (dt * SPEED) / SUBSTEPS
    for (const star of stars.current) {
      let state = star.state
      for (let i = 0; i < SUBSTEPS; i += 1) {
        state = step(state, clock.current, h, pendulum)
        clock.current += h
      }
      star.state = { theta: wrapAngle(state.theta), p: state.p }
      star.trail.push(star.state)
      if (star.trail.length > TRAIL) {
        star.trail.splice(0, star.trail.length - TRAIL)
      }
    }
    setFrame(stars.current.map((s) => ({ state: s.state, trail: [...s.trail], branch: s.branch })))
  })

  const size = Math.min(width - 24, 460)
  const halfWidth = 2 * Math.sqrt(strength * formFactor)
  const librationPeriod = (2 * Math.PI) / (ARMS * Math.sqrt(strength * formFactor)) / (2 * Math.PI)
  const trapped = frame.filter((star) => isTrapped(star.state, pendulum)).length

  return (
    <div className="viz" ref={ref}>
      <div className="viz__row">
        <Chart width={size} height={size} xLabel="$x/R_{\rm CR}$" yLabel="$y/R_{\rm CR}$">
          {(inner) => {
            const x = d3.scaleLinear().domain([-RADIUS_MAX, RADIUS_MAX]).range([0, inner.width])
            const y = d3.scaleLinear().domain([-RADIUS_MAX, RADIUS_MAX]).range([inner.height, 0])
            const pixel = (point: readonly [number, number]): readonly [number, number] => [
              x(point[0]),
              y(point[1])
            ]
            const unit = Math.abs(x(1) - x(0))
            // Trailing logarithmic arms through the corotation circle at
            // theta_r = +/- pi: the azimuth decreases outward for a disk that
            // turns counterclockwise.
            const armPath = (phase: number): string =>
              linePath(
                d3.range(Math.log(RADIUS_MIN), Math.log(RADIUS_MAX), 0.01).map((logRadius) => {
                  const radius = Math.exp(logRadius)
                  const phi = phase - logRadius / Math.tan(PITCH)
                  return pixel([radius * Math.cos(phi), radius * Math.sin(phi)])
                })
              )
            const trailOf = (star: Star): string => {
              const segments: PendulumState[][] = [[]]
              star.trail.forEach((point, i) => {
                const previous = star.trail[i - 1]
                if (previous !== undefined && Math.abs(point.theta - previous.theta) > Math.PI) {
                  segments.push([])
                }
                segments[segments.length - 1].push(point)
              })
              return segments
                .map((segment) => linePath(segment.map((s) => pixel(place(s, star.branch)))))
                .join(' ')
            }
            return (
              <>
                <g clipPath={inner.clip}>
                  <circle
                    cx={x(0)}
                    cy={y(0)}
                    r={unit}
                    className="viz-line viz-line--muted viz-line--dotted"
                  />
                  <circle
                    cx={x(0)}
                    cy={y(0)}
                    r={unit * (1 + halfWidth)}
                    className="viz-line viz-line--muted viz-line--thin viz-line--dashed"
                  />
                  <circle
                    cx={x(0)}
                    cy={y(0)}
                    r={unit * (1 - halfWidth)}
                    className="viz-line viz-line--muted viz-line--thin viz-line--dashed"
                  />
                  {[Math.PI / ARMS, -Math.PI / ARMS].map((phase) => (
                    <path
                      key={phase}
                      d={armPath(phase)}
                      className="viz-line viz-line--accent"
                      style={{ strokeWidth: unit * 0.09, strokeOpacity: 0.35 }}
                      strokeLinecap="round"
                    />
                  ))}
                  {frame.map((star, i) => {
                    const trappedStar = isTrapped(star.state, pendulum)
                    const [cx, cy] = pixel(place(star.state, star.branch))
                    return (
                      <React.Fragment key={i}>
                        <path
                          d={trailOf(star)}
                          className={`viz-line viz-line--thin ${trappedStar ? 'viz-line--cold' : 'viz-line--muted'}`}
                        />
                        <circle
                          cx={cx}
                          cy={cy}
                          r={3.5}
                          className={trappedStar ? 'viz-dot--cold' : 'viz-dot'}
                        />
                      </React.Fragment>
                    )
                  })}
                  <circle cx={x(0)} cy={y(0)} r={4} className="viz-dot" />
                </g>
                <Axis scale={y} orientation="left" ticks={5} />
                <Axis
                  scale={x}
                  orientation="bottom"
                  transform={`translate(0,${inner.height})`}
                  ticks={5}
                />
              </>
            )
          }}
        </Chart>
      </div>
      <Controls>
        <Slider
          label="$\epsilon$"
          value={strength}
          min={0.004}
          max={0.05}
          step={0.001}
          onChange={setStrength}
          format={(v) => v.toFixed(3)}
        />
        <Slider
          label="$F$"
          value={formFactor}
          min={0.1}
          max={1}
          step={0.01}
          onChange={setFormFactor}
        />
        <Button label={playing ? 'Pause' : 'Play'} onClick={() => setPlaying(!playing)} primary />
        <Button label="Reset" onClick={reset} />
        <Readout
          items={[
            ['$\\Delta R/R_{\\rm CR}$', format2(halfWidth)],
            ['$T_{\\rm lib}/T_{\\rm orb}$', format2(librationPeriod)],
            ['trapped', `${trapped} of ${STARS}`]
          ]}
        />
      </Controls>
      <p className="viz-note">
        The frame rotates with the pattern, so the arms stand still and the disk turns
        counterclockwise inside corotation and clockwise outside it. Dashed circles mark the island
        half-width 2 sqrt(epsilon F) R_CR, the trapped stars are blue.
      </p>
    </div>
  )
}
