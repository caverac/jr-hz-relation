import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Controls, Note, Readout, Slider } from '@site/src/components/viz/Controls'
import { useElementWidth } from '@site/src/components/viz/hooks'
import { type PendulumState, separatrix, strobeMap } from '@site/src/physics/pendulum'
import * as d3 from 'd3'
import React, { type ReactNode, useMemo, useState } from 'react'

const ORBITS = 36
const PERIODS = 350
const STEPS_PER_PERIOD = 64
const HEIGHT = 380
const P_MIN = -0.8
const P_MAX = 1.8
const ANGLE_TICKS = [-Math.PI, -Math.PI / 2, 0, Math.PI / 2, Math.PI]

const format3 = d3.format('.3f')

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

/** A path of dots: one zero-length segment per point, drawn with round caps. */
function dotPath(
  points: readonly PendulumState[],
  x: (v: number) => number,
  y: (v: number) => number
): string {
  return points
    .map((point) => `M${x(point.theta).toFixed(1)},${y(point.p).toFixed(1)}h0.01`)
    .join('')
}

/**
 * The stroboscopic map of two corotation resonances of equal strength, at
 * p = 0 and p = 1 in units of their separation: a point per drive period for
 * each of 36 orbits. The slider sets the Chirikov parameter S, the sum of the
 * two island half-widths over their separation. Below S of about 2/3 invariant
 * curves still separate the islands; near S = 1 the chaotic layers of the two
 * separatrices merge into one sea that a star can cross.
 */
export default function OverlapMap(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const [overlap, setOverlap] = useState(0.7)
  const orbits = useMemo(
    () =>
      strobeMap({ overlap, orbits: ORBITS, periods: PERIODS, stepsPerPeriod: STEPS_PER_PERIOD }),
    [overlap]
  )
  const psi = (overlap / 4) ** 2
  const halfWidth = 2 * Math.sqrt(psi)
  const chartWidth = width - 24

  return (
    <div className="viz" ref={ref}>
      <Chart width={chartWidth} height={HEIGHT} xLabel="$\theta$" yLabel="$p$">
        {(inner) => {
          const x = d3.scaleLinear().domain([-Math.PI, Math.PI]).range([0, inner.width])
          const y = d3.scaleLinear().domain([P_MIN, P_MAX]).range([inner.height, 0])
          const thetas = d3.range(-Math.PI, Math.PI + 0.01, 0.02)
          const branch = (center: number, sign: 1 | -1): string =>
            linePath(
              thetas.map(
                (theta) =>
                  [x(theta), y(center + sign * separatrix(theta, { psi, gAbs: 1 }))] as const
              )
            )
          return (
            <>
              <g clipPath={inner.clip}>
                {orbits.map((orbit, i) => (
                  <path
                    key={i}
                    d={dotPath(orbit, x, y)}
                    fill="none"
                    stroke={d3.schemeTableau10[i % 10]}
                    strokeWidth={2.2}
                    strokeLinecap="round"
                  />
                ))}
                {[0, 1].map((center) => (
                  <React.Fragment key={center}>
                    <path d={branch(center, 1)} className="viz-line viz-line--thin" />
                    <path d={branch(center, -1)} className="viz-line viz-line--thin" />
                  </React.Fragment>
                ))}
              </g>
              <Axis scale={y} orientation="left" ticks={6} />
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
        <Slider label="$S$" value={overlap} min={0.2} max={1.6} step={0.05} onChange={setOverlap} />
        <Readout
          items={[
            ['$\\Psi$', format3(psi)],
            ['$2\\sqrt{\\Psi}$', format3(halfWidth)],
            ['$\\Delta p$', '1']
          ]}
        />
      </Controls>
      <Note text="$H = -p^2/2 + \Psi[\cos\theta + \cos(\theta + t)]$, sampled once per period of the second wave. The thin curves are the separatrices each resonance would have alone; the dots of one color belong to one orbit." />
    </div>
  )
}
