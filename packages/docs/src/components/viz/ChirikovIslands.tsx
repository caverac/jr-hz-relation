import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Controls, Readout, Select, Slider } from '@site/src/components/viz/Controls'
import { columnWidth, columnsFor, useElementWidth } from '@site/src/components/viz/hooks'
import {
  BAR_PATTERN_SPEEDS,
  MW_BAR_PATTERN_SPEED,
  MW_SPIRAL_PATTERN_SPEED,
  SPIRAL_PATTERN_SPEEDS,
  corotationRadius,
  librationHalfWidth,
  overlapFromPatternSpeeds
} from '@site/src/physics/overlap'
import * as d3 from 'd3'
import React, { type ReactNode, useState } from 'react'

const HEIGHT = 220
const RADIUS_MAX = 16
const STRENGTH_MAX = 0.05
const PHYSICAL_BAND: readonly [number, number] = [0.01, 0.03]

const format2 = d3.format('.2f')
const format3 = d3.format('.3f')

interface Population {
  readonly label: string
  readonly formFactor: number
  readonly className: 'cold' | 'hot'
}

/**
 * The corotation islands of the bar and the spiral along the radius, for a cold
 * and a hot population, and the overlap parameter S of Equation (11) against the
 * spiral strength. The pattern speeds take the values of Table 1.
 */
export default function ChirikovIslands(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const [strength, setStrength] = useState(0.02)
  const [barSpeed, setBarSpeed] = useState(MW_BAR_PATTERN_SPEED)
  const [spiralSpeed, setSpiralSpeed] = useState(MW_SPIRAL_PATTERN_SPEED)
  const [hotFormFactor, setHotFormFactor] = useState(0.5)

  const populations: Population[] = [
    { label: 'F = 1', formFactor: 1, className: 'cold' },
    { label: `F = ${format2(hotFormFactor)}`, formFactor: hotFormFactor, className: 'hot' }
  ]
  const barRadius = corotationRadius(barSpeed)
  const spiralRadius = corotationRadius(spiralSpeed)
  // The faster pattern is the inner one whichever slider carries it.
  const innerSpeed = Math.max(barSpeed, spiralSpeed)
  const outerSpeed = Math.min(barSpeed, spiralSpeed)
  const overlapOf = (formFactor: number, epsilon: number): number =>
    overlapFromPatternSpeeds(innerSpeed, outerSpeed, epsilon, 1, formFactor)
  const thresholdStrength = (formFactor: number): number =>
    1 / (4 * formFactor * ((innerSpeed + outerSpeed) / (innerSpeed - outerSpeed)) ** 2)

  const columns = columnsFor(width)
  const chartWidth = columnWidth(width, columns)

  return (
    <div className="viz" ref={ref}>
      <div className="viz__row">
        <Chart width={chartWidth} height={HEIGHT} xLabel="$R$ (kpc)">
          {(inner) => {
            const x = d3.scaleLinear().domain([0, RADIUS_MAX]).range([0, inner.width])
            const rowHeight = inner.height / populations.length
            return (
              <>
                {populations.map((population, row) => {
                  const center = rowHeight * (row + 0.5)
                  const barWidth = librationHalfWidth(barRadius, strength, 1, population.formFactor)
                  const spiralWidth = librationHalfWidth(
                    spiralRadius,
                    strength,
                    1,
                    population.formFactor
                  )
                  const sharedLower = Math.max(barRadius - barWidth, spiralRadius - spiralWidth, 0)
                  const sharedUpper = Math.min(
                    barRadius + barWidth,
                    spiralRadius + spiralWidth,
                    RADIUS_MAX
                  )
                  const overlapping = sharedLower <= sharedUpper
                  return (
                    <g key={population.label}>
                      <text
                        x={4}
                        y={center - rowHeight * 0.32}
                        className={`viz-text viz-text--${population.className}`}
                      >
                        {population.label}
                      </text>
                      <rect
                        x={x(Math.max(barRadius - barWidth, 0))}
                        y={center - rowHeight * 0.2}
                        width={x(barRadius + barWidth) - x(Math.max(barRadius - barWidth, 0))}
                        height={rowHeight * 0.4}
                        className={`viz-fill--${population.className}`}
                      />
                      <rect
                        x={x(spiralRadius - spiralWidth)}
                        y={center - rowHeight * 0.2}
                        width={
                          x(Math.min(spiralRadius + spiralWidth, RADIUS_MAX)) -
                          x(spiralRadius - spiralWidth)
                        }
                        height={rowHeight * 0.4}
                        className={`viz-fill--${population.className}`}
                      />
                      {overlapping ? (
                        <rect
                          x={x(sharedLower)}
                          y={center - rowHeight * 0.2}
                          width={x(sharedUpper) - x(sharedLower)}
                          height={rowHeight * 0.4}
                          className="viz-fill--muted"
                        />
                      ) : null}
                      <line
                        x1={x(barRadius)}
                        x2={x(barRadius)}
                        y1={center - rowHeight * 0.3}
                        y2={center + rowHeight * 0.3}
                        className={`viz-line viz-line--${population.className}`}
                      />
                      <line
                        x1={x(spiralRadius)}
                        x2={x(spiralRadius)}
                        y1={center - rowHeight * 0.3}
                        y2={center + rowHeight * 0.3}
                        className={`viz-line viz-line--${population.className}`}
                      />
                      <text
                        x={x(barRadius)}
                        y={center + rowHeight * 0.45}
                        textAnchor="middle"
                        className="viz-text viz-text--muted"
                      >
                        bar
                      </text>
                      <text
                        x={x(spiralRadius)}
                        y={center + rowHeight * 0.45}
                        textAnchor="middle"
                        className="viz-text viz-text--muted"
                      >
                        spiral
                      </text>
                    </g>
                  )
                })}
                <Axis
                  scale={x}
                  orientation="bottom"
                  transform={`translate(0,${inner.height})`}
                  ticks={8}
                />
              </>
            )
          }}
        </Chart>
        <Chart width={chartWidth} height={HEIGHT} xLabel="$\epsilon = |\Phi_s|/V_c^2$" yLabel="$S$">
          {(inner) => {
            const x = d3.scaleLinear().domain([0, STRENGTH_MAX]).range([0, inner.width])
            const top = Math.max(2, 1.1 * overlapOf(1, STRENGTH_MAX))
            const y = d3.scaleLinear().domain([0, top]).range([inner.height, 0])
            const epsilons = d3.range(0, STRENGTH_MAX + 1e-6, STRENGTH_MAX / 80)
            return (
              <>
                <rect
                  x={x(PHYSICAL_BAND[0])}
                  y={0}
                  width={x(PHYSICAL_BAND[1]) - x(PHYSICAL_BAND[0])}
                  height={inner.height}
                  className="viz-fill--muted"
                />
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(1)}
                  y2={y(1)}
                  className="viz-line viz-line--muted viz-line--dashed"
                />
                {populations.map((population) => (
                  <path
                    key={population.label}
                    d={linePath(
                      epsilons.map(
                        (epsilon) =>
                          [x(epsilon), y(overlapOf(population.formFactor, epsilon))] as const
                      )
                    )}
                    className={`viz-line viz-line--${population.className}`}
                  />
                ))}
                {populations.map((population) => (
                  <circle
                    key={population.label}
                    cx={x(strength)}
                    cy={y(overlapOf(population.formFactor, strength))}
                    r={5}
                    className={`viz-dot--${population.className}`}
                  />
                ))}
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
        <Slider
          label="$\epsilon$"
          value={strength}
          min={0.002}
          max={STRENGTH_MAX}
          step={0.001}
          onChange={setStrength}
          format={(v) => v.toFixed(3)}
        />
        <Slider
          label="$\Omega_{\rm bar}$"
          value={barSpeed}
          min={20}
          max={45}
          step={0.1}
          onChange={setBarSpeed}
          format={(v) => v.toFixed(1)}
        />
        <Slider
          label="$\Omega_{\rm sp}$"
          value={spiralSpeed}
          min={14}
          max={32}
          step={0.1}
          onChange={setSpiralSpeed}
          format={(v) => v.toFixed(1)}
        />
        <Slider
          label="$F_{\rm hot}$"
          value={hotFormFactor}
          min={0.1}
          max={1}
          step={0.01}
          onChange={setHotFormFactor}
        />
        <Select
          label="bar"
          value={String(barSpeed)}
          options={BAR_PATTERN_SPEEDS.map(
            (entry) => [String(entry.value), `${entry.value} (${entry.label})`] as const
          )}
          onChange={(value) => setBarSpeed(Number(value))}
        />
        <Select
          label="spiral"
          value={String(spiralSpeed)}
          options={SPIRAL_PATTERN_SPEEDS.map(
            (entry) => [String(entry.value), `${entry.value} (${entry.label})`] as const
          )}
          onChange={(value) => setSpiralSpeed(Number(value))}
        />
      </Controls>
      <Controls>
        <Readout
          items={[
            ['$R_{\\rm CR}$ bar, spiral (kpc)', `${format2(barRadius)}, ${format2(spiralRadius)}`],
            ['$S$ (cold)', format2(overlapOf(1, strength))],
            ['$S$ (hot)', format2(overlapOf(hotFormFactor, strength))],
            ['$\\epsilon$ at $S = 1$, cold', format3(thresholdStrength(1))],
            ['$\\epsilon$ at $S = 1$, hot', format3(thresholdStrength(hotFormFactor))]
          ]}
        />
      </Controls>
      <p className="viz-note">
        Pattern speeds in km/s/kpc with V_c = 230 km/s. Left: the libration islands of the two
        corotation resonances, overlapping where the gray band appears. Right: S against the spiral
        strength, with the threshold S = 1 dashed and the physical band shaded.
      </p>
    </div>
  )
}
