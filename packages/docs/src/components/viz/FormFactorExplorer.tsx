import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Controls, Readout, Slider } from '@site/src/components/viz/Controls'
import { columnWidth, columnsFor, useElementWidth } from '@site/src/components/viz/hooks'
import {
  MILKY_WAY_ALPHA,
  softenedFormFactor,
  softenedKernel,
  turningPoint,
  verticalAction,
  verticalFrequency,
  verticalOrbit
} from '@site/src/physics/sheet'
import * as d3 from 'd3'
import React, { type ReactNode, useMemo, useState } from 'react'

const PERIODS_SHOWN = 2
const SAMPLES_PER_PERIOD = 200
const CURVE_POINTS = 48
const ACTION_MAX = 10
const PANEL_HEIGHT = 150
const CURVE_HEIGHT = 300

interface CurvePoint {
  readonly action: number
  readonly formFactor: number
}

/** The form factor against the vertical action, on log-spaced energies. */
function formFactorCurve(alpha: number, thickness: number): CurvePoint[] {
  const energies = d3.range(CURVE_POINTS).map((i) => 0.01 * 1500 ** (i / (CURVE_POINTS - 1)))
  const points = energies.map((energy) => ({
    action: verticalAction(energy),
    formFactor: softenedFormFactor(energy, alpha, thickness)
  }))
  return [{ action: 0, formFactor: 1 }, ...points]
}

const format3 = d3.format('.3f')

/**
 * The vertical form factor as the time average of the arm's kernel along the
 * orbit: the sampled orbit z(t), the kernel K(z(t)) under it with its mean, and
 * the resulting curve F(J_z) with the current orbit marked on it.
 */
export default function FormFactorExplorer(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const [energy, setEnergy] = useState(1)
  const [alpha, setAlpha] = useState(MILKY_WAY_ALPHA)
  const [thickness, setThickness] = useState(0)

  const orbit = useMemo(() => {
    const period = (2 * Math.PI) / verticalFrequency(energy)
    const sampled = verticalOrbit(
      energy,
      period / SAMPLES_PER_PERIOD,
      PERIODS_SHOWN * SAMPLES_PER_PERIOD
    )
    return { period, time: sampled.time, z: sampled.z }
  }, [energy])
  const kernel = useMemo(
    () => orbit.z.map((z) => softenedKernel(z, alpha, thickness)),
    [orbit, alpha, thickness]
  )
  const curve = useMemo(() => formFactorCurve(alpha, thickness), [alpha, thickness])
  const thinCurve = useMemo(
    () => (thickness > 0 ? formFactorCurve(alpha, 0) : null),
    [alpha, thickness]
  )

  const zMax = turningPoint(energy)
  const frequency = verticalFrequency(energy)
  const action = verticalAction(energy)
  const formFactor = softenedFormFactor(energy, alpha, thickness)
  const thinFormFactor = thickness > 0 ? softenedFormFactor(energy, alpha, 0) : formFactor

  const columns = columnsFor(width)
  const chartWidth = columnWidth(width, columns)

  const readout: Array<readonly [string, string]> = [
    ['$z_m/z_0$', format3(zMax)],
    ['$\\nu_z$', format3(frequency)],
    ['$J_z$', format3(action)],
    ['$F$', format3(formFactor)]
  ]
  if (thickness > 0) {
    readout.push(['$F_{\\rm thin}$', format3(thinFormFactor)])
  }

  return (
    <div className="viz" ref={ref}>
      <div className="viz__row">
        <div>
          <Chart width={chartWidth} height={PANEL_HEIGHT} yLabel="$z/z_0$">
            {(inner) => {
              const x = d3.scaleLinear().domain([0, PERIODS_SHOWN]).range([0, inner.width])
              const y = d3
                .scaleLinear()
                .domain([-1.15 * zMax, 1.15 * zMax])
                .range([inner.height, 0])
              const path = linePath(
                orbit.time.map((t, i) => [x(t / orbit.period), y(orbit.z[i])] as const)
              )
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
                  <path d={path} className="viz-line viz-line--cold" />
                  <Axis scale={y} orientation="left" ticks={4} />
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
          <Chart width={chartWidth} height={PANEL_HEIGHT} yLabel="$K(z)$" xLabel="$t/T_z$">
            {(inner) => {
              const x = d3.scaleLinear().domain([0, PERIODS_SHOWN]).range([0, inner.width])
              const y = d3.scaleLinear().domain([0, 1.05]).range([inner.height, 0])
              const points = orbit.time.map((t, i) => [x(t / orbit.period), y(kernel[i])] as const)
              const area = `${linePath(points)} L${x(PERIODS_SHOWN)},${y(0)} L${x(0)},${y(0)} Z`
              return (
                <>
                  <path d={area} className="viz-fill--cold" />
                  <path d={linePath(points)} className="viz-line viz-line--cold" />
                  <line
                    x1={0}
                    x2={inner.width}
                    y1={y(formFactor)}
                    y2={y(formFactor)}
                    className="viz-line viz-line--accent viz-line--dashed"
                  />
                  <text
                    x={inner.width - 4}
                    y={y(formFactor) - 4}
                    textAnchor="end"
                    className="viz-text"
                  >
                    F = {format3(formFactor)}
                  </text>
                  <Axis scale={y} orientation="left" ticks={3} />
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
        </div>
        <Chart width={chartWidth} height={CURVE_HEIGHT} xLabel="$J_z$" yLabel="$F$">
          {(inner) => {
            const x = d3.scaleLinear().domain([0, ACTION_MAX]).range([0, inner.width])
            const y = d3.scaleLinear().domain([0, 1.05]).range([inner.height, 0])
            const toPixels = (point: CurvePoint): readonly [number, number] => [
              x(point.action),
              y(point.formFactor)
            ]
            return (
              <>
                <g clipPath={inner.clip}>
                  {thinCurve === null ? null : (
                    <path
                      d={linePath(thinCurve.map(toPixels))}
                      className="viz-line viz-line--muted viz-line--dashed"
                    />
                  )}
                  <path d={linePath(curve.map(toPixels))} className="viz-line viz-line--cold" />
                </g>
                <line
                  x1={x(action)}
                  x2={x(action)}
                  y1={y(0)}
                  y2={y(formFactor)}
                  className="viz-line viz-line--muted viz-line--dotted viz-line--thin"
                />
                <line
                  x1={x(0)}
                  x2={x(action)}
                  y1={y(formFactor)}
                  y2={y(formFactor)}
                  className="viz-line viz-line--muted viz-line--dotted viz-line--thin"
                />
                <circle cx={x(action)} cy={y(formFactor)} r={5} className="viz-dot--accent" />
                <Axis scale={y} orientation="left" ticks={5} gridLength={inner.width} />
                <Axis
                  scale={x}
                  orientation="bottom"
                  transform={`translate(0,${inner.height})`}
                  ticks={5}
                  gridLength={inner.height}
                />
              </>
            )
          }}
        </Chart>
      </div>
      <Controls>
        <Slider label="$E_z$" value={energy} min={0.05} max={8} step={0.05} onChange={setEnergy} />
        <Slider label="$\alpha$" value={alpha} min={0.1} max={3} step={0.01} onChange={setAlpha} />
        <Slider label="$h$" value={thickness} min={0} max={2} step={0.05} onChange={setThickness} />
        <Readout items={readout} />
      </Controls>
    </div>
  )
}
