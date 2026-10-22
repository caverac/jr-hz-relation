import useBaseUrl from '@docusaurus/useBaseUrl'
import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Controls, Readout, Select } from '@site/src/components/viz/Controls'
import { columnWidth, columnsFor, useElementWidth } from '@site/src/components/viz/hooks'
import * as d3 from 'd3'
import React, { type ReactNode, useEffect, useState } from 'react'

const HEIGHT = 300

/** The cached tables of the migration test, one per baseline. */
const BASELINES: ReadonlyArray<readonly [string, string]> = [
  ['migration-0.5-1.0.json', '0.49 Gyr'],
  ['migration-0.5-1.5.json', '0.98 Gyr'],
  ['migration-0.5-2.5.json', '1.96 Gyr']
]

interface RingBins {
  readonly ring: string
  readonly F: readonly number[]
  readonly variance: readonly number[]
}

interface RingCore {
  readonly ring: string
  readonly k: number
  readonly exponent_F: number
  readonly sigma_dLz: number
}

interface Tables {
  readonly meta: { readonly baseline_gyr: number; readonly form: string }
  readonly core: readonly RingCore[]
  readonly bins: readonly RingBins[]
  readonly collapse: { readonly F: number; readonly z: number }
}

type Loaded = Record<string, Tables>

const format2 = d3.format('.2f')

/** Center radius of a ring labeled "3 to 4", in kpc. */
function ringCenter(label: string): number {
  const [inner, outer] = label.split(' to ').map(Number)
  return (inner + outer) / 2
}

/** Ring colors from blue (inner) to red (outer), as the static figure. */
function ringColor(index: number, count: number): string {
  return d3.interpolateRdBu(1 - (index + 0.5) / count)
}

/**
 * The core test of Section 6 from the cached tables: the variance of the
 * angular-momentum change in eight bins of the layer form factor per origin
 * ring, both axes normalized to the bin of largest F, against the F^2 law, and
 * the fitted exponent per ring at the three baselines.
 */
export default function NbodyVarianceExplorer(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const dataRoot = useBaseUrl('/data/nbody/')
  const [loaded, setLoaded] = useState<Loaded>({})
  const [failed, setFailed] = useState<string | null>(null)
  const [selected, setSelected] = useState(BASELINES[2][0])

  useEffect(() => {
    let cancelled = false
    Promise.all(
      BASELINES.map(async ([file]) => {
        const response = await fetch(`${dataRoot}${file}`)
        if (!response.ok) {
          throw new Error(`${file}: ${response.status}`)
        }
        // The tables are written by Python's json module, which emits NaN for
        // the rule without a measured counterpart and for rings without
        // arrivals in one direction; the token is not JSON, so it is read as
        // null. Neither table is used here.
        const text = (await response.text()).replace(/\bNaN\b/g, 'null')
        return [file, JSON.parse(text) as Tables] as const
      })
    )
      .then((entries) => {
        if (!cancelled) {
          setLoaded(Object.fromEntries(entries))
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setFailed(error instanceof Error ? error.message : String(error))
        }
      })
    return () => {
      cancelled = true
    }
  }, [dataRoot])

  const tables = loaded[selected]
  const columns = columnsFor(width)
  const chartWidth = columnWidth(width, columns)

  if (failed !== null) {
    return (
      <div className="viz" ref={ref}>
        <p className="viz-note">The cached tables could not be loaded: {failed}</p>
      </div>
    )
  }

  return (
    <div className="viz" ref={ref}>
      <div className="viz__row">
        <Chart
          width={chartWidth}
          height={HEIGHT}
          xLabel="$\ln F/F_{\max}$"
          yLabel="$\ln \mathrm{Var}(\Delta L_z)/\mathrm{Var}_{\max}(\Delta L_z)$"
        >
          {(inner) => {
            const rings = tables?.bins ?? []
            const xMin = Math.min(
              -1,
              ...rings.map((ring) => Math.log(ring.F[0] / ring.F[ring.F.length - 1]))
            )
            const x = d3
              .scaleLinear()
              .domain([1.05 * xMin, 0.05])
              .range([0, inner.width])
            const y = d3
              .scaleLinear()
              .domain([2.1 * xMin, 0.1])
              .range([inner.height, 0])
            return (
              <>
                <path
                  d={linePath([
                    [x(xMin), y(2 * xMin)],
                    [x(0), y(0)]
                  ])}
                  className="viz-line"
                />
                {rings.map((ring, index) => {
                  const last = ring.F.length - 1
                  const points = ring.F.map(
                    (value, i) =>
                      [
                        x(Math.log(value / ring.F[last])),
                        y(Math.log(ring.variance[i] / ring.variance[last]))
                      ] as const
                  )
                  const color = ringColor(index, rings.length)
                  const core = tables?.core[index]
                  return (
                    <g key={ring.ring}>
                      <path d={linePath(points)} fill="none" stroke={color} strokeWidth={1.2} />
                      {points.map((point, i) => (
                        <circle key={i} cx={point[0]} cy={point[1]} r={3.5} fill={color}>
                          <title>
                            {`${ring.ring} kpc, exponent ${core === undefined ? '' : format2(core.exponent_F)}`}
                          </title>
                        </circle>
                      ))}
                    </g>
                  )
                })}
                <text x={inner.width - 4} y={14} textAnchor="end" className="viz-text">
                  F^2
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
        <Chart width={chartWidth} height={HEIGHT} xLabel="$R_g$ (kpc)" yLabel="$b$">
          {(inner) => {
            const x = d3.scaleLinear().domain([3, 12]).range([0, inner.width])
            const y = d3.scaleLinear().domain([0, 3.2]).range([inner.height, 0])
            return (
              <>
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(2)}
                  y2={y(2)}
                  className="viz-line viz-line--muted viz-line--dotted"
                />
                {BASELINES.map(([file, label]) => {
                  const entry = loaded[file]
                  if (entry === undefined) {
                    return null
                  }
                  const points = entry.core.map(
                    (ring) => [x(ringCenter(ring.ring)), y(ring.exponent_F)] as const
                  )
                  const current = file === selected
                  return (
                    <g key={file}>
                      <path
                        d={linePath(points)}
                        className={`viz-line ${current ? 'viz-line--cold viz-line--bold' : 'viz-line--muted viz-line--thin'}`}
                      />
                      {current
                        ? entry.core.map((ring, index) => (
                            <circle
                              key={ring.ring}
                              cx={x(ringCenter(ring.ring))}
                              cy={y(ring.exponent_F)}
                              r={4}
                              fill={ringColor(index, entry.core.length)}
                            >
                              <title>{`${ring.ring} kpc, ${label}: b = ${format2(ring.exponent_F)}`}</title>
                            </circle>
                          ))
                        : null}
                    </g>
                  )
                })}
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
        <Select label="baseline" value={selected} options={BASELINES} onChange={setSelected} />
        {tables === undefined ? (
          <span className="viz-note">loading the cached tables</span>
        ) : (
          <Readout
            items={[
              ['mean $b$', format2(d3.mean(tables.core, (ring) => ring.exponent_F) ?? 0)],
              ['rms on $F$ (dex)', format2(tables.collapse.F)],
              ['rms on $|z|$ (dex)', format2(tables.collapse.z)]
            ]}
          />
        )}
      </Controls>
      <div className="viz-legend">
        {(tables?.core ?? []).map((ring, index, all) => (
          <span key={ring.ring} className="viz-legend__item">
            <span
              className="viz-legend__swatch"
              style={{ background: ringColor(index, all.length) }}
            />
            {ring.ring}
          </span>
        ))}
      </div>
      <p className="viz-note">
        Left: the nine origin rings at the selected baseline, the black line is F^2; hover a point
        for the ring and its fitted exponent. Right: the exponent per ring at the three baselines,
        the selected one in blue, with the prediction b = 2 dotted.
      </p>
    </div>
  )
}
