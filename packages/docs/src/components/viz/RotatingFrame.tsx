import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import {
  Controls,
  IconButton,
  Note,
  Readout,
  Select,
  Slider
} from '@site/src/components/viz/Controls'
import {
  makeRandom,
  useAnimationFrame,
  useElementWidth,
  useInView
} from '@site/src/components/viz/hooks'
import { type Pendulum, type PendulumState, isTrapped, step } from '@site/src/physics/pendulum'
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

/** The frame the stars are drawn in. */
type View = 'pattern' | 'inertial'

const VIEWS: ReadonlyArray<readonly [View, string]> = [
  ['pattern', 'rotating with the pattern'],
  ['inertial', 'inertial']
]

interface TrailPoint {
  readonly state: PendulumState
  /** Time of the point in units of 1/Omega at corotation. */
  readonly time: number
}

interface Star {
  state: PendulumState
  trail: TrailPoint[]
}

interface Snapshot {
  readonly stars: readonly Star[]
  readonly time: number
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

/**
 * The slow angle is left unwrapped and seeded over m turns, so that the
 * azimuth theta_r / m covers the whole disk and never jumps between sectors.
 */
function seedStars(): Star[] {
  const random = makeRandom(11)
  return d3.range(STARS).map(() => {
    const state: PendulumState = {
      theta: ARMS * (2 * Math.PI * random() - Math.PI),
      p: -0.42 + 0.84 * random()
    }
    return { state, trail: [{ state, time: 0 }] }
  })
}

/**
 * Position at radius 1 + x and azimuth theta_r / m in the pattern frame, turned
 * by the angle the pattern has swept, Omega_p t with Omega_p = 1 in these units,
 * when the inertial frame is drawn.
 */
function place(state: PendulumState, rotation: number): readonly [number, number] {
  const phi = state.theta / ARMS + rotation
  const radius = 1 + state.p
  return [radius * Math.cos(phi), radius * Math.sin(phi)]
}

/**
 * Stars near corotation of a two-armed pattern, in the frame that rotates with
 * the pattern or in the inertial frame. The arms sit at theta_r = +/- pi, the
 * inter-arm points at theta_r = 0, and each star follows the pendulum of
 * Section 3 mapped to the disk: in the pattern frame the trapped stars librate
 * about the inter-arm corotation points on horseshoe paths and the others
 * circulate; in the inertial frame every star orbits and the arms turn with
 * them, so the horseshoes are seen to exist only relative to the pattern.
 */
export default function RotatingFrame(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const inView = useInView(ref)
  const [strength, setStrength] = useState(0.02)
  const [formFactor, setFormFactor] = useState(1)
  const [view, setView] = useState<View>('pattern')
  const [playing, setPlaying] = useState(true)
  const pendulum = useMemo(() => pendulumOf(strength, formFactor), [strength, formFactor])
  const stars = useRef<Star[]>(seedStars())
  const elapsed = useRef(0)
  const [snapshot, setSnapshot] = useState<Snapshot>(() => ({
    stars: stars.current.map((s) => ({ ...s })),
    time: 0
  }))

  const reset = (): void => {
    stars.current = seedStars()
    elapsed.current = 0
    setSnapshot({ stars: stars.current.map((s) => ({ ...s })), time: 0 })
  }

  useAnimationFrame(playing && inView, (dt) => {
    const advance = dt * SPEED
    const h = advance / SUBSTEPS
    elapsed.current += advance
    for (const star of stars.current) {
      let state = star.state
      for (let i = 0; i < SUBSTEPS; i += 1) {
        state = step(state, elapsed.current, h, pendulum)
      }
      star.state = state
      star.trail.push({ state, time: elapsed.current })
      if (star.trail.length > TRAIL) {
        star.trail.splice(0, star.trail.length - TRAIL)
      }
    }
    setSnapshot({
      stars: stars.current.map((s) => ({ state: s.state, trail: [...s.trail] })),
      time: elapsed.current
    })
  })

  const size = Math.min(width - 24, 460)
  const halfWidth = 2 * Math.sqrt(strength * formFactor)
  const librationPeriod = (2 * Math.PI) / (ARMS * Math.sqrt(strength * formFactor)) / (2 * Math.PI)
  const trapped = snapshot.stars.filter((star) => isTrapped(star.state, pendulum)).length
  const inertial = view === 'inertial'
  const rotationAt = (time: number): number => (inertial ? time : 0)

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
                  const phi = phase + rotationAt(snapshot.time) - logRadius / Math.tan(PITCH)
                  return pixel([radius * Math.cos(phi), radius * Math.sin(phi)])
                })
              )
            const trailOf = (star: Star): string =>
              linePath(star.trail.map((point) => pixel(place(point.state, rotationAt(point.time)))))
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
                  {snapshot.stars.map((star, i) => {
                    const trappedStar = isTrapped(star.state, pendulum)
                    const [cx, cy] = pixel(place(star.state, rotationAt(snapshot.time)))
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
        <Select
          label="frame"
          value={view}
          options={VIEWS}
          onChange={(value) => setView(value as View)}
        />
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
        <IconButton
          icon={playing ? 'pause' : 'play'}
          label={playing ? 'Pause' : 'Play'}
          onClick={() => setPlaying(!playing)}
          primary
        />
        <IconButton icon="reset" label="Reset" onClick={reset} />
        <Readout
          items={[
            ['$\\Delta R/R_{\\rm CR}$', format2(halfWidth)],
            ['$T_{\\rm lib}/T_{\\rm orb}$', format2(librationPeriod)],
            ['trapped', `${trapped} of ${STARS}`]
          ]}
        />
      </Controls>
      <Note text="In the frame of the pattern the arms stand still and the disk turns counterclockwise inside corotation and clockwise outside it; in the inertial frame the arms turn at $\Omega_p$ and every star orbits with them. The dashed circles sit at $R_{\rm CR}(1 \pm 2\sqrt{\epsilon F})$, the island half-width; the trapped stars are blue." />
    </div>
  )
}
