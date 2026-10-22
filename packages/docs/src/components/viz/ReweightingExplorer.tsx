import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Controls, Note, Readout, Select, Slider } from '@site/src/components/viz/Controls'
import { columnWidth, columnsFor, useElementWidth } from '@site/src/components/viz/hooks'
import {
  type Weight,
  MILKY_WAY_ALPHA,
  captureWeight,
  crossoverWeight,
  diffusionWeight,
  energyTable,
  powerWeight,
  reweight,
  thresholdWeight,
  trappedWeight
} from '@site/src/physics/sheet'
import * as d3 from 'd3'
import React, { type ReactNode, useMemo, useState } from 'react'

const HEIGHT = 280
const ENERGY_MAX = 8
const ALPHA_SAMPLES = 19
const ALPHA_RANGE: readonly [number, number] = [0.2, 2]

type Kind = 'capture' | 'power' | 'threshold' | 'trapped' | 'crossover' | 'diffusion'

interface Family {
  readonly text: string
  readonly parameter: string
  readonly min: number
  readonly max: number
  readonly step: number
  readonly initial: number
  readonly weight: (value: number) => Weight
}

const FAMILIES: Record<Kind, Family> = {
  capture: {
    text: 'capture weight',
    parameter: '$s$',
    min: 0,
    max: 4,
    step: 0.05,
    initial: 0.9,
    weight: captureWeight
  },
  power: {
    text: 'power law',
    parameter: '$p$',
    min: 0,
    max: 3,
    step: 0.05,
    initial: 1,
    weight: powerWeight
  },
  threshold: {
    text: 'threshold rule',
    parameter: '$\\lambda$',
    min: 0,
    max: 3,
    step: 0.05,
    initial: 1,
    weight: thresholdWeight
  },
  trapped: {
    text: 'trapped fraction',
    parameter: '$\\kappa$',
    min: 0.05,
    max: 6,
    step: 0.05,
    initial: 1.5,
    weight: trappedWeight
  },
  crossover: {
    text: 'crossover weight',
    parameter: '$S_0$',
    min: 0,
    max: 5,
    step: 0.05,
    initial: 2,
    weight: crossoverWeight
  },
  diffusion: {
    text: 'Balescu-Lenard weight',
    parameter: '$b$',
    min: 0,
    max: 10,
    step: 0.1,
    initial: 1,
    weight: diffusionWeight
  }
}

const KINDS = Object.keys(FAMILIES) as Kind[]

const format3 = d3.format('.3f')
const percent = d3.format('+.1f')

/**
 * The reweighting that turns a migration weight into a provenance bias: the
 * equilibrium vertical distribution of the sheet, the same distribution
 * reweighted by W(F(E_z)), and the mean vertical energies of the two, whose
 * ratio gives the dispersion ratio. Every weight of the paper is available.
 */
export default function ReweightingExplorer(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const [kind, setKind] = useState<Kind>('power')
  const [alpha, setAlpha] = useState(MILKY_WAY_ALPHA)
  const [parameters, setParameters] = useState<Record<Kind, number>>(
    () =>
      Object.fromEntries(KINDS.map((key) => [key, FAMILIES[key].initial])) as Record<Kind, number>
  )
  const family = FAMILIES[kind]
  const parameter = parameters[kind]
  const weight = useMemo(() => family.weight(parameter), [family, parameter])
  const table = useMemo(() => energyTable(alpha), [alpha])
  const result = reweight(table, weight)
  const alphaTables = useMemo(
    () =>
      d3.range(ALPHA_SAMPLES).map((i) => {
        const value = ALPHA_RANGE[0] + ((ALPHA_RANGE[1] - ALPHA_RANGE[0]) * i) / (ALPHA_SAMPLES - 1)
        return { alpha: value, table: energyTable(value) }
      }),
    []
  )
  const alphaCurve = useMemo(
    () => alphaTables.map((entry) => [entry.alpha, reweight(entry.table, weight).bias] as const),
    [alphaTables, weight]
  )

  const columns = columnsFor(width)
  const chartWidth = columnWidth(width, columns)
  const base0 = table[0].base
  const migrator0 = table[0].base * weight(table[0].formFactor)

  return (
    <div className="viz" ref={ref}>
      <div className="viz__row">
        <Chart
          width={chartWidth}
          height={HEIGHT}
          xLabel="$E_z$"
          yLabel="$\mathrm{d}N/\mathrm{d}E_z$, $W$"
        >
          {(inner) => {
            const x = d3.scaleLinear().domain([0, ENERGY_MAX]).range([0, inner.width])
            const y = d3.scaleLinear().domain([0, 1.05]).range([inner.height, 0])
            const rows = table.filter((row) => row.energy <= ENERGY_MAX)
            const parent = rows.map((row) => [x(row.energy), y(row.base / base0)] as const)
            const migrators = rows.map(
              (row) => [x(row.energy), y((row.base * weight(row.formFactor)) / migrator0)] as const
            )
            const weights = rows.map((row) => [x(row.energy), y(weight(row.formFactor))] as const)
            const close = (points: ReadonlyArray<readonly [number, number]>): string =>
              `${linePath(points)} L${points[points.length - 1][0]},${y(0)} L${points[0][0]},${y(0)} Z`
            return (
              <>
                <path d={close(parent)} className="viz-fill--muted" />
                <path d={close(migrators)} className="viz-fill--cold" />
                <path d={linePath(parent)} className="viz-line viz-line--muted" />
                <path d={linePath(migrators)} className="viz-line viz-line--cold" />
                <path d={linePath(weights)} className="viz-line viz-line--hot viz-line--dashed" />
                <line
                  x1={x(result.meanAll)}
                  x2={x(result.meanAll)}
                  y1={y(0)}
                  y2={y(0.12)}
                  className="viz-line viz-line--muted viz-line--bold"
                />
                <line
                  x1={x(result.meanMigrators)}
                  x2={x(result.meanMigrators)}
                  y1={y(0)}
                  y2={y(0.12)}
                  className="viz-line viz-line--cold viz-line--bold"
                />
                <text
                  x={inner.width - 4}
                  y={12}
                  textAnchor="end"
                  className="viz-text viz-text--hot"
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
          xLabel="$\alpha = k z_0$"
          yLabel="$\ln \sigma_z^{\rm mig}/\sigma_z^{\rm all}$"
        >
          {(inner) => {
            const x = d3.scaleLinear().domain(ALPHA_RANGE).range([0, inner.width])
            const low = Math.min(d3.min(alphaCurve, (p) => p[1]) ?? -0.1, result.bias, -0.05)
            const y = d3
              .scaleLinear()
              .domain([1.1 * low, 0])
              .range([inner.height, 0])
            return (
              <>
                <line
                  x1={x(MILKY_WAY_ALPHA)}
                  x2={x(MILKY_WAY_ALPHA)}
                  y1={0}
                  y2={inner.height}
                  className="viz-line viz-line--muted viz-line--dotted"
                />
                <path
                  d={linePath(alphaCurve.map((p) => [x(p[0]), y(p[1])] as const))}
                  className="viz-line viz-line--cold"
                />
                <circle cx={x(alpha)} cy={y(result.bias)} r={5} className="viz-dot--accent" />
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
        <Select
          label="$W$"
          value={kind}
          options={KINDS.map((key) => [key, FAMILIES[key].text] as const)}
          onChange={(value) => setKind(value as Kind)}
        />
        <Slider
          label={family.parameter}
          value={parameter}
          min={family.min}
          max={family.max}
          step={family.step}
          onChange={(value) => setParameters({ ...parameters, [kind]: value })}
        />
        <Slider
          label="$\alpha$"
          value={alpha}
          min={ALPHA_RANGE[0]}
          max={ALPHA_RANGE[1]}
          step={0.02}
          onChange={setAlpha}
        />
      </Controls>
      <Controls>
        <Readout
          items={[
            ['$\\langle E_z\\rangle_{\\rm all}$', format3(result.meanAll)],
            ['$\\langle E_z\\rangle_{\\rm mig}$', format3(result.meanMigrators)],
            ['$\\sigma_z^{\\rm mig}/\\sigma_z^{\\rm all}$', format3(result.ratio)],
            ['bias', `${percent(100 * result.bias)}%`]
          ]}
        />
      </Controls>
      <Note text="Left: the parent distribution (gray) and the migrators (blue), each normalized to its value at the lowest energy, with the weight $W$ dashed in red and the two mean energies as ticks. Right: the bias against the thickness, the Milky Way value dotted." />
    </div>
  )
}
