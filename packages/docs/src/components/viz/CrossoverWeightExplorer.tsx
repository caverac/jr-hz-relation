import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Controls, Note, Readout, Slider } from '@site/src/components/viz/Controls'
import { columnWidth, columnsFor, useElementWidth } from '@site/src/components/viz/hooks'
import {
  MILKY_WAY_ALPHA,
  criticalFormFactor,
  crossoverExponent,
  crossoverWeight,
  energyTable,
  powerWeight,
  reweight
} from '@site/src/physics/sheet'
import * as d3 from 'd3'
import React, { type ReactNode, useMemo, useState } from 'react'

const HEIGHT = 280
const ACTION_MAX = 8
const OVERLAP_MAX = 5
const OVERLAP_SAMPLES = 41

const format2 = d3.format('.2f')
const percent = d3.format('+.1f')

/**
 * The crossover weight W = F^p of Equation (12), whose exponent runs from the
 * trapping value 1/2 to the diffusive value 2 as the local overlap S0 sqrt(F)
 * crosses unity, and the bias it produces against the effective overlap S0.
 */
export default function CrossoverWeightExplorer(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const [overlap, setOverlap] = useState(2)
  const [alpha, setAlpha] = useState(MILKY_WAY_ALPHA)
  const table = useMemo(() => energyTable(alpha), [alpha])
  const biasCurve = useMemo(
    () =>
      d3.range(OVERLAP_SAMPLES).map((i) => {
        const value = (OVERLAP_MAX * i) / (OVERLAP_SAMPLES - 1)
        return [value, reweight(table, crossoverWeight(value)).bias] as const
      }),
    [table]
  )
  const bias = reweight(table, crossoverWeight(overlap)).bias
  const floor = reweight(table, powerWeight(0.5)).bias
  const ceiling = reweight(table, powerWeight(2)).bias
  const critical = criticalFormFactor(overlap)
  // The action at which F crosses F_crit, by interpolation on the table.
  const criticalRow = table.find((row) => row.formFactor <= critical)
  const criticalAction = criticalRow?.action

  const columns = columnsFor(width)
  const chartWidth = columnWidth(width, columns)

  return (
    <div className="viz" ref={ref}>
      <div className="viz__row">
        <Chart width={chartWidth} height={HEIGHT} xLabel="$J_z$" yLabel="$p(J_z)$, $W(J_z)$">
          {(inner) => {
            const x = d3.scaleLinear().domain([0, ACTION_MAX]).range([0, inner.width])
            const y = d3.scaleLinear().domain([0, 2.1]).range([inner.height, 0])
            const rows = table.filter((row) => row.action <= ACTION_MAX)
            const exponent = linePath(
              rows.map(
                (row) =>
                  [
                    x(row.action),
                    y(crossoverExponent(overlap * Math.sqrt(row.formFactor)))
                  ] as const
              )
            )
            const weight = linePath([
              [x(0), y(1)],
              ...rows.map(
                (row) => [x(row.action), y(crossoverWeight(overlap)(row.formFactor))] as const
              )
            ])
            const bare = linePath([
              [x(0), y(1)],
              ...rows.map((row) => [x(row.action), y(row.formFactor)] as const)
            ])
            return (
              <>
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(0.5)}
                  y2={y(0.5)}
                  className="viz-line viz-line--muted viz-line--dotted viz-line--thin"
                />
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(2)}
                  y2={y(2)}
                  className="viz-line viz-line--muted viz-line--dotted viz-line--thin"
                />
                {criticalAction === undefined || criticalAction > ACTION_MAX ? null : (
                  <line
                    x1={x(criticalAction)}
                    x2={x(criticalAction)}
                    y1={0}
                    y2={inner.height}
                    className="viz-line viz-line--accent viz-line--dashed"
                  />
                )}
                <path d={bare} className="viz-line viz-line--muted viz-line--thin" />
                <path d={weight} className="viz-line viz-line--cold viz-line--bold" />
                <path d={exponent} className="viz-line viz-line--hot" />
                <text
                  x={inner.width - 4}
                  y={y(2) + 12}
                  textAnchor="end"
                  className="viz-text viz-text--hot"
                >
                  p
                </text>
                <text
                  x={inner.width - 4}
                  y={y(0) - 6}
                  textAnchor="end"
                  className="viz-text viz-text--cold"
                >
                  W
                </text>
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
        <Chart
          width={chartWidth}
          height={HEIGHT}
          xLabel="$S_0$"
          yLabel="$\ln \sigma_z^{\rm mig}/\sigma_z^{\rm all}$"
        >
          {(inner) => {
            const x = d3.scaleLinear().domain([0, OVERLAP_MAX]).range([0, inner.width])
            const y = d3
              .scaleLinear()
              .domain([1.1 * ceiling, 0])
              .range([inner.height, 0])
            return (
              <>
                <rect
                  x={x(0.8)}
                  y={0}
                  width={x(1.2) - x(0.8)}
                  height={inner.height}
                  className="viz-fill--muted"
                />
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(floor)}
                  y2={y(floor)}
                  className="viz-line viz-line--muted viz-line--dotted"
                />
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(ceiling)}
                  y2={y(ceiling)}
                  className="viz-line viz-line--muted viz-line--dotted"
                />
                <path
                  d={linePath(biasCurve.map((p) => [x(p[0]), y(p[1])] as const))}
                  className="viz-line viz-line--cold"
                />
                <circle cx={x(overlap)} cy={y(bias)} r={5} className="viz-dot--accent" />
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
          label="$S_0$"
          value={overlap}
          min={0}
          max={OVERLAP_MAX}
          step={0.05}
          onChange={setOverlap}
        />
        <Slider label="$\alpha$" value={alpha} min={0.2} max={2} step={0.02} onChange={setAlpha} />
        <Readout
          items={[
            ['$F_{\\rm crit}$', overlap > 0 ? format2(critical) : '-'],
            ['$J_{z,\\rm crit}$', criticalAction === undefined ? '-' : format2(criticalAction)],
            ['bias', `${percent(100 * bias)}%`],
            ['$\\sqrt{F}$ to $F^2$', `${percent(100 * floor)}% to ${percent(100 * ceiling)}%`]
          ]}
        />
      </Controls>
      <Note text="Left: the exponent $p$ (red), the weight $F^p$ (blue) and the bare $F$ (gray) against the vertical action; the dashed line marks $F = F_{\rm crit}$. Right: the bias against $S_0$ between the trapping floor and the diffusive value (dotted), with the bar-plus-spiral range shaded." />
    </div>
  )
}
