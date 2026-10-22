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
  hamiltonian,
  islandHalfWidth,
  isTrapped,
  levelCurve,
  separatrix,
  step,
  wrapAngle
} from '@site/src/physics/pendulum'
import * as d3 from 'd3'
import React, { type ReactNode, useMemo, useRef, useState } from 'react'

/** Coupling of a midplane orbit, so that Psi = PSI0 F. */
const PSI0 = 1
const G_ABS = 1
const P_LIMIT = 2.6
const PARTICLES = 18
const TRAIL = 40
const HEIGHT = 320
const SPEED = 1.2
const SUBSTEPS = 3
const ANGLE_TICKS = [-Math.PI, -Math.PI / 2, 0, Math.PI / 2, Math.PI]

interface Mover {
  state: PendulumState
  trail: PendulumState[]
}

const format2 = d3.format('.2f')

function seedMovers(): Mover[] {
  const random = makeRandom(7)
  return d3.range(PARTICLES).map((i) => {
    const p = -P_LIMIT + (2 * P_LIMIT * (i + 0.5)) / PARTICLES
    const state: PendulumState = { theta: wrapAngle(2 * Math.PI * random() - Math.PI), p }
    return { state, trail: [state] }
  })
}

function angleTick(value: number): string {
  if (value === 0) {
    return '0'
  }
  const multiple = value / Math.PI
  if (Math.abs(Math.abs(multiple) - 1) < 1e-9) {
    return multiple > 0 ? 'π' : '-π'
  }
  return `${multiple.toFixed(1)}π`
}

/**
 * The phase portrait of the corotation pendulum, H = -(1/2)|g| p^2 + Psi cos(theta)
 * with Psi = Psi_0 F: level curves, the separatrix, and a few stars moving on
 * it. The slider changes the form factor, and with it the island half-width
 * 2 sqrt(Psi/|g|), as the square root of F.
 */
export default function PendulumPortrait(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const inView = useInView(ref)
  const [formFactor, setFormFactor] = useState(1)
  const [playing, setPlaying] = useState(true)
  const pendulum = useMemo<Pendulum>(() => ({ psi: PSI0 * formFactor, gAbs: G_ABS }), [formFactor])
  const movers = useRef<Mover[]>(seedMovers())
  const [frame, setFrame] = useState<Mover[]>(() => movers.current.map((m) => ({ ...m })))
  const clock = useRef(0)

  const reset = (): void => {
    movers.current = seedMovers()
    clock.current = 0
    setFrame(movers.current.map((m) => ({ ...m })))
  }

  useAnimationFrame(playing && inView, (dt) => {
    const h = (dt * SPEED) / SUBSTEPS
    for (const mover of movers.current) {
      let state = mover.state
      for (let i = 0; i < SUBSTEPS; i += 1) {
        state = step(state, clock.current, h, pendulum)
        clock.current += h
      }
      mover.state = { theta: wrapAngle(state.theta), p: state.p }
      mover.trail.push(mover.state)
      if (mover.trail.length > TRAIL) {
        mover.trail.splice(0, mover.trail.length - TRAIL)
      }
    }
    setFrame(movers.current.map((m) => ({ state: m.state, trail: [...m.trail] })))
  })

  const levels = useMemo(() => {
    const trapped = [0.15, 0.45, 0.8].map((s) => pendulum.psi * (1 - 2 * s))
    const circulating = [0.6, 1.2, 1.8, 2.4].map(
      (momentum) => -pendulum.psi - 0.5 * G_ABS * momentum * momentum
    )
    return { trapped, circulating }
  }, [pendulum])

  const chartWidth = width - 24
  const halfWidth = islandHalfWidth(pendulum)

  return (
    <div className="viz" ref={ref}>
      <Chart width={chartWidth} height={HEIGHT} xLabel="$\theta_r$" yLabel="$p = L_z - L_{\rm CR}$">
        {(inner) => {
          const x = d3.scaleLinear().domain([-Math.PI, Math.PI]).range([0, inner.width])
          const y = d3.scaleLinear().domain([-P_LIMIT, P_LIMIT]).range([inner.height, 0])
          const toPath = (points: readonly PendulumState[], sign: 1 | -1): string =>
            linePath(points.map((point) => [x(point.theta), y(sign * point.p)] as const))
          const separatrixPoints = d3
            .range(-Math.PI, Math.PI + 0.01, 0.02)
            .map((theta) => ({ theta, p: separatrix(theta, pendulum) }))
          const island = `${toPath(separatrixPoints, 1)} ${toPath([...separatrixPoints].reverse(), -1).replace('M', 'L')} Z`
          const trailOf = (mover: Mover): string => {
            // Break the trail where the angle wraps around.
            const segments: PendulumState[][] = [[]]
            mover.trail.forEach((point, i) => {
              const previous = mover.trail[i - 1]
              if (previous !== undefined && Math.abs(point.theta - previous.theta) > Math.PI) {
                segments.push([])
              }
              segments[segments.length - 1].push(point)
            })
            return segments.map((segment) => toPath(segment, 1)).join(' ')
          }
          return (
            <>
              <g clipPath={inner.clip}>
                <path d={island} className="viz-fill--cold" />
                {levels.trapped.map((level) => {
                  const points = levelCurve(level, pendulum, 240)
                  return (
                    <React.Fragment key={level}>
                      <path
                        d={toPath(points, 1)}
                        className="viz-line viz-line--muted viz-line--thin"
                      />
                      <path
                        d={toPath(points, -1)}
                        className="viz-line viz-line--muted viz-line--thin"
                      />
                    </React.Fragment>
                  )
                })}
                {levels.circulating.map((level) => {
                  const points = levelCurve(level, pendulum, 240)
                  return (
                    <React.Fragment key={level}>
                      <path
                        d={toPath(points, 1)}
                        className="viz-line viz-line--muted viz-line--thin"
                      />
                      <path
                        d={toPath(points, -1)}
                        className="viz-line viz-line--muted viz-line--thin"
                      />
                    </React.Fragment>
                  )
                })}
                <path
                  d={toPath(separatrixPoints, 1)}
                  className="viz-line viz-line--cold viz-line--bold"
                />
                <path
                  d={toPath(separatrixPoints, -1)}
                  className="viz-line viz-line--cold viz-line--bold"
                />
                <line
                  x1={x(0)}
                  x2={x(0)}
                  y1={y(-halfWidth)}
                  y2={y(halfWidth)}
                  className="viz-line viz-line--accent viz-line--dashed"
                />
                <text x={x(0) + 6} y={y(halfWidth / 2)} className="viz-text viz-text--muted">
                  2{'√'}({'Ψ'}/|g|)
                </text>
                {frame.map((mover, i) => (
                  <React.Fragment key={i}>
                    <path
                      d={trailOf(mover)}
                      className={`viz-line viz-line--thin ${isTrapped(mover.state, pendulum) ? 'viz-line--cold' : 'viz-line--hot'}`}
                    />
                    <circle
                      cx={x(mover.state.theta)}
                      cy={y(mover.state.p)}
                      r={4}
                      className={
                        isTrapped(mover.state, pendulum) ? 'viz-dot--cold' : 'viz-dot--hot'
                      }
                    />
                  </React.Fragment>
                ))}
                <circle cx={x(0)} cy={y(0)} r={3} className="viz-dot" />
                <circle cx={x(Math.PI)} cy={y(0)} r={3} className="viz-dot--open" />
                <circle cx={x(-Math.PI)} cy={y(0)} r={3} className="viz-dot--open" />
              </g>
              <Axis scale={y} orientation="left" ticks={5} />
              <Axis
                scale={x}
                orientation="bottom"
                transform={`translate(0,${inner.height})`}
                tickValues={ANGLE_TICKS}
                tickFormat={angleTick}
              />
            </>
          )
        }}
      </Chart>
      <Controls>
        <Slider
          label="$F$"
          value={formFactor}
          min={0.05}
          max={1}
          step={0.01}
          onChange={setFormFactor}
        />
        <Button label={playing ? 'Pause' : 'Play'} onClick={() => setPlaying(!playing)} primary />
        <Button label="Reset" onClick={reset} />
        <Readout
          items={[
            ['$\\Psi/\\Psi_0$', format2(formFactor)],
            ['$\\Delta p$', format2(halfWidth)],
            [
              'trapped',
              `${frame.filter((m) => hamiltonian(m.state, pendulum) > -pendulum.psi).length} of ${PARTICLES}`
            ]
          ]}
        />
      </Controls>
    </div>
  )
}
