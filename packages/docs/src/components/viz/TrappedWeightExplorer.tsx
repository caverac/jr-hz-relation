import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Controls, Note, Readout, Slider } from '@site/src/components/viz/Controls'
import { columnWidth, columnsFor, useElementWidth } from '@site/src/components/viz/hooks'
import {
  type EnergyRow,
  MILKY_WAY_ALPHA,
  energyTable,
  powerWeight,
  reweight,
  trappedFraction,
  trappedWeight
} from '@site/src/physics/sheet'
import * as d3 from 'd3'
import React, { type ReactNode, useMemo, useState } from 'react'

const HEIGHT = 280
const ACTION_MAX = 8
const KAPPA_MAX = 6
const KAPPA_SAMPLES = 36
const REFERENCE_WIDTHS = [0.3, 4]

const format3 = d3.format('.3f')
const percent = d3.format('+.1f')

/** The trapped weight along the table, normalized to its midplane value. */
function weightCurve(
  table: readonly EnergyRow[],
  islandWidth: number
): Array<readonly [number, number]> {
  const midplane = trappedFraction(1, islandWidth)
  return [
    [0, 1] as const,
    ...table.map(
      (row) => [row.action, trappedFraction(row.formFactor, islandWidth) / midplane] as const
    )
  ]
}

/**
 * The exact trapped fraction of Equation (9) against the vertical action for the
 * current island width, between its narrow-island limit sqrt(F) and the flat
 * wide-island limit, and the provenance bias it produces against kappa.
 */
export default function TrappedWeightExplorer(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const [islandWidth, setIslandWidth] = useState(1.5)
  const [alpha, setAlpha] = useState(MILKY_WAY_ALPHA)
  const table = useMemo(() => energyTable(alpha), [alpha])
  const current = useMemo(() => weightCurve(table, islandWidth), [table, islandWidth])
  const references = useMemo(
    () => REFERENCE_WIDTHS.map((value) => weightCurve(table, value)),
    [table]
  )
  const dilute = useMemo(
    () => [
      [0, 1] as const,
      ...table.map((row) => [row.action, Math.sqrt(row.formFactor)] as const)
    ],
    [table]
  )
  const biasCurve = useMemo(
    () =>
      d3.range(KAPPA_SAMPLES).map((i) => {
        const kappa = 0.05 + ((KAPPA_MAX - 0.05) * i) / (KAPPA_SAMPLES - 1)
        return [kappa, reweight(table, trappedWeight(kappa)).bias] as const
      }),
    [table]
  )
  const bias = reweight(table, trappedWeight(islandWidth)).bias
  const floor = reweight(table, powerWeight(0.5)).bias

  const columns = columnsFor(width)
  const chartWidth = columnWidth(width, columns)
  const biasMin = Math.min(d3.min(biasCurve, (point) => point[1]) ?? -0.1, floor) * 1.15

  return (
    <div className="viz" ref={ref}>
      <div className="viz__row">
        <Chart width={chartWidth} height={HEIGHT} xLabel="$J_z$" yLabel="$W(J_z)/W(0)$">
          {(inner) => {
            const x = d3.scaleLinear().domain([0, ACTION_MAX]).range([0, inner.width])
            const y = d3.scaleLinear().domain([0, 1.05]).range([inner.height, 0])
            const pixels = (curve: ReadonlyArray<readonly [number, number]>): string =>
              linePath(
                curve.filter((p) => p[0] <= ACTION_MAX).map((p) => [x(p[0]), y(p[1])] as const)
              )
            return (
              <>
                {references.map((curve, i) => (
                  <path
                    key={i}
                    d={pixels(curve)}
                    className="viz-line viz-line--muted viz-line--thin"
                  />
                ))}
                <path d={pixels(dilute)} className="viz-line viz-line--muted viz-line--dashed" />
                <path d={pixels(current)} className="viz-line viz-line--cold viz-line--bold" />
                <text
                  x={x(ACTION_MAX) - 4}
                  y={y(dilute[dilute.length - 1][1]) - 6}
                  textAnchor="end"
                  className="viz-text viz-text--muted"
                >
                  {'√'}F
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
          xLabel="$\kappa$"
          yLabel="$\ln \sigma_z^{\rm mig}/\sigma_z^{\rm all}$"
        >
          {(inner) => {
            const x = d3.scaleLinear().domain([0, KAPPA_MAX]).range([0, inner.width])
            const y = d3.scaleLinear().domain([biasMin, 0]).range([inner.height, 0])
            return (
              <>
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(floor)}
                  y2={y(floor)}
                  className="viz-line viz-line--muted viz-line--dotted"
                />
                <path
                  d={linePath(biasCurve.map((p) => [x(p[0]), y(p[1])] as const))}
                  className="viz-line viz-line--cold"
                />
                <circle cx={x(islandWidth)} cy={y(bias)} r={5} className="viz-dot--accent" />
                <Axis scale={y} orientation="left" ticks={5} gridLength={inner.width} />
                <Axis
                  scale={x}
                  orientation="bottom"
                  transform={`translate(0,${inner.height})`}
                  ticks={6}
                  gridLength={inner.height}
                />
              </>
            )
          }}
        </Chart>
      </div>
      <Controls>
        <Slider
          label="$\kappa$"
          value={islandWidth}
          min={0.05}
          max={KAPPA_MAX}
          step={0.05}
          onChange={setIslandWidth}
        />
        <Slider label="$\alpha$" value={alpha} min={0.2} max={2} step={0.02} onChange={setAlpha} />
        <Readout
          items={[
            ['$W(J_z{=}0)$', format3(trappedFraction(1, islandWidth))],
            ['bias', `${percent(100 * bias)}%`],
            ['$\\sqrt{F}$ floor', `${percent(100 * floor)}%`]
          ]}
        />
      </Controls>
      <Note text="Left: the trapped weight for the current $\kappa$ (blue), for $\kappa = 0.3$ and 4 (thin gray) and the dilute limit $\sqrt{F}$ (dashed). Right: the bias against $\kappa$, with the dilute floor dotted." />
    </div>
  )
}
