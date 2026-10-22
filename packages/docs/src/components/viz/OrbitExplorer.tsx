import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Button, Controls, Readout, Slider } from '@site/src/components/viz/Controls'
import {
  columnWidth,
  columnsFor,
  useAnimationFrame,
  useElementWidth,
  useInView
} from '@site/src/components/viz/hooks'
import {
  acceleration,
  turningPoint,
  verticalAction,
  verticalFrequency,
  verticalOrbit
} from '@site/src/physics/sheet'
import * as d3 from 'd3'
import React, { type ReactNode, useMemo, useRef, useState } from 'react'

/** Flat rotation curve in units R_g = V_c = 1: Omega = 1 and kappa = sqrt 2. */
const KAPPA = Math.SQRT2

/** Disk scale height in units of the guiding radius (0.3 kpc at 8 kpc). */
const Z0 = 0.04

/**
 * The sheet's time unit z0/sigma_z in units of 1/Omega, chosen so that the
 * midplane vertical frequency sqrt(2)/tau is 2.5 Omega, the solar-neighborhood
 * ratio of the vertical to the orbital frequency.
 */
const TAU = Math.SQRT2 / 2.5

/** Orbital phase advanced per second of wall-clock time: one orbit in 8 s. */
const SPEED = (2 * Math.PI) / 8

const SUBSTEPS = 4
const TRAIL_LENGTH = 420
const LOOP_SAMPLES = 400

interface TrailPoint {
  readonly x: number
  readonly y: number
  readonly radius: number
  readonly z: number
}

interface Snapshot {
  readonly t: number
  readonly z: number
  readonly vz: number
  readonly trail: readonly TrailPoint[]
}

interface Motion {
  t: number
  z: number
  vz: number
  trail: TrailPoint[]
}

const format3 = d3.format('.3f')

function epicycle(t: number, amplitude: number): { radius: number; phi: number } {
  const radial = amplitude * Math.cos(KAPPA * t)
  const azimuthal = -((2 / KAPPA) * amplitude * Math.sin(KAPPA * t))
  return { radius: 1 + radial, phi: t + azimuthal }
}

/**
 * One star of a flat-rotation-curve disk, drawn in the four views that define
 * its actions: the face-on orbit about the guiding circle, the edge-on vertical
 * oscillation in the isothermal sheet, and the two phase-plane loops whose areas
 * are 2 pi J_R and 2 pi J_z.
 */
export default function OrbitExplorer(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const inView = useInView(ref)
  const [amplitude, setAmplitude] = useState(0.12)
  const [energy, setEnergy] = useState(1)
  const [playing, setPlaying] = useState(true)
  const motion = useRef<Motion>({ t: 0, z: 0, vz: Math.sqrt(2), trail: [] })
  const [snapshot, setSnapshot] = useState<Snapshot>({ t: 0, z: 0, vz: Math.sqrt(2), trail: [] })

  const loop = useMemo(() => {
    const period = (2 * Math.PI) / verticalFrequency(energy)
    return verticalOrbit(energy, period / LOOP_SAMPLES, LOOP_SAMPLES)
  }, [energy])
  const zMax = turningPoint(energy)
  const action = verticalAction(energy)
  const radialAction = (KAPPA * amplitude * amplitude) / 2

  const reset = (newEnergy: number): void => {
    motion.current = { t: 0, z: 0, vz: Math.sqrt(2 * newEnergy), trail: [] }
    setSnapshot({ t: 0, z: 0, vz: Math.sqrt(2 * newEnergy), trail: [] })
  }

  useAnimationFrame(playing && inView, (dt) => {
    const state = motion.current
    const advance = dt * SPEED
    const h = advance / SUBSTEPS / TAU
    for (let i = 0; i < SUBSTEPS; i += 1) {
      state.vz += 0.5 * h * acceleration(state.z)
      state.z += h * state.vz
      state.vz += 0.5 * h * acceleration(state.z)
    }
    state.t += advance
    const { radius, phi } = epicycle(state.t, amplitude)
    state.trail.push({ x: radius * Math.cos(phi), y: radius * Math.sin(phi), radius, z: state.z })
    if (state.trail.length > TRAIL_LENGTH) {
      state.trail.splice(0, state.trail.length - TRAIL_LENGTH)
    }
    setSnapshot({ t: state.t, z: state.z, vz: state.vz, trail: [...state.trail] })
  })

  const columns = columnsFor(width)
  const chartWidth = columnWidth(width, columns)
  const square = Math.min(chartWidth, 320)
  const current = epicycle(snapshot.t, amplitude)
  const trailPixels = (
    scaleX: d3.ScaleLinear<number, number>,
    scaleY: d3.ScaleLinear<number, number>,
    pick: (point: TrailPoint) => readonly [number, number]
  ): string =>
    linePath(
      snapshot.trail.map((point) => {
        const [u, v] = pick(point)
        return [scaleX(u), scaleY(v)] as const
      })
    )

  return (
    <div className="viz" ref={ref}>
      <div className="viz__row">
        <Chart width={chartWidth} height={square} xLabel="$x/R_g$" yLabel="$y/R_g$">
          {(inner) => {
            const x = d3.scaleLinear().domain([-1.45, 1.45]).range([0, inner.width])
            const y = d3.scaleLinear().domain([-1.45, 1.45]).range([inner.height, 0])
            const guidingRadius = Math.abs(x(1) - x(0))
            return (
              <>
                <circle
                  cx={x(0)}
                  cy={y(0)}
                  r={guidingRadius}
                  className="viz-line viz-line--muted viz-line--dotted viz-line--thin"
                />
                <circle cx={x(0)} cy={y(0)} r={3} className="viz-dot" />
                <path
                  d={trailPixels(x, y, (p) => [p.x, p.y])}
                  className="viz-line viz-line--cold viz-line--thin"
                />
                <circle
                  cx={x(Math.cos(snapshot.t))}
                  cy={y(Math.sin(snapshot.t))}
                  r={3}
                  className="viz-dot--open"
                />
                <circle
                  cx={x(current.radius * Math.cos(current.phi))}
                  cy={y(current.radius * Math.sin(current.phi))}
                  r={5}
                  className="viz-dot--accent"
                />
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
        <Chart width={chartWidth} height={square} xLabel="$R/R_g$" yLabel="$z/z_0$">
          {(inner) => {
            const x = d3.scaleLinear().domain([0.6, 1.4]).range([0, inner.width])
            const y = d3.scaleLinear().domain([-6, 6]).range([inner.height, 0])
            return (
              <>
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(0)}
                  y2={y(0)}
                  className="viz-line viz-line--muted viz-line--thin"
                />
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(zMax)}
                  y2={y(zMax)}
                  className="viz-line viz-line--muted viz-line--dotted viz-line--thin"
                />
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(-zMax)}
                  y2={y(-zMax)}
                  className="viz-line viz-line--muted viz-line--dotted viz-line--thin"
                />
                <path
                  d={trailPixels(x, y, (p) => [p.radius, p.z])}
                  className="viz-line viz-line--cold viz-line--thin"
                />
                <circle
                  cx={x(current.radius)}
                  cy={y(snapshot.z)}
                  r={5}
                  className="viz-dot--accent"
                />
                <Axis scale={y} orientation="left" ticks={5} />
                <Axis
                  scale={x}
                  orientation="bottom"
                  transform={`translate(0,${inner.height})`}
                  ticks={4}
                />
              </>
            )
          }}
        </Chart>
        <Chart width={chartWidth} height={square} xLabel="$X/R_g$" yLabel="$v_R/V_c$">
          {(inner) => {
            const x = d3.scaleLinear().domain([-0.35, 0.35]).range([0, inner.width])
            const y = d3.scaleLinear().domain([-0.5, 0.5]).range([inner.height, 0])
            const ellipse = d3
              .range(0, 2 * Math.PI + 0.05, 0.05)
              .map(
                (angle) =>
                  [x(amplitude * Math.cos(angle)), y(-amplitude * KAPPA * Math.sin(angle))] as const
              )
            const radial = amplitude * Math.cos(KAPPA * snapshot.t)
            const speed = -amplitude * KAPPA * Math.sin(KAPPA * snapshot.t)
            return (
              <>
                <path d={`${linePath(ellipse)} Z`} className="viz-fill--cold" />
                <path d={linePath(ellipse)} className="viz-line viz-line--cold" />
                <circle cx={x(radial)} cy={y(speed)} r={5} className="viz-dot--accent" />
                <text x={x(0)} y={y(0) + 4} textAnchor="middle" className="viz-text">
                  2{'π'}J_R
                </text>
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
        <Chart width={chartWidth} height={square} xLabel="$z/z_0$" yLabel="$v_z/\sigma_z$">
          {(inner) => {
            const x = d3.scaleLinear().domain([-6, 6]).range([0, inner.width])
            const y = d3.scaleLinear().domain([-4, 4]).range([inner.height, 0])
            const points = loop.z.map((z, i) => [x(z), y(loop.velocity[i])] as const)
            return (
              <>
                <path d={`${linePath(points)} Z`} className="viz-fill--cold" />
                <path d={linePath(points)} className="viz-line viz-line--cold" />
                <circle cx={x(snapshot.z)} cy={y(snapshot.vz)} r={5} className="viz-dot--accent" />
                <text x={x(0)} y={y(0) + 4} textAnchor="middle" className="viz-text">
                  2{'π'}J_z
                </text>
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
          label="$a_R/R_g$"
          value={amplitude}
          min={0}
          max={0.3}
          step={0.01}
          onChange={setAmplitude}
        />
        <Slider
          label="$E_z$"
          value={energy}
          min={0.02}
          max={6}
          step={0.02}
          onChange={(value) => {
            setEnergy(value)
            reset(value)
          }}
        />
        <Button label={playing ? 'Pause' : 'Play'} onClick={() => setPlaying(!playing)} primary />
        <Button label="Reset" onClick={() => reset(energy)} />
        <Readout
          items={[
            ['$J_R/(R_gV_c)$', format3(radialAction)],
            ['$J_z/(z_0\\sigma_z)$', format3(action)],
            ['$z_m/z_0$', format3(zMax)],
            [
              '$\\Omega:\\kappa:\\nu_z$',
              `1 : ${KAPPA.toFixed(2)} : ${(verticalFrequency(energy) / TAU).toFixed(2)}`
            ]
          ]}
        />
      </Controls>
      <p className="viz-note">
        Units R_g = V_c = 1 for the in-plane motion and z_0 = {Z0} R_g for the vertical one, whose
        scale is stretched in the edge-on view. The in-plane motion is the epicycle approximation;
        the vertical one is integrated in the isothermal sheet.
      </p>
    </div>
  )
}
