import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Button, Controls, Readout, Slider } from '@site/src/components/viz/Controls'
import {
  columnWidth,
  columnsFor,
  makeRandom,
  useAnimationFrame,
  useElementWidth,
  useInView
} from '@site/src/components/viz/hooks'
import { MILKY_WAY_ALPHA, verticalFormFactor } from '@site/src/physics/sheet'
import * as d3 from 'd3'
import React, { type ReactNode, useRef, useState } from 'react'

/** Stars per population. */
const STARS = 800

/** Kick of a midplane star, in the units of the drawing. */
const KICK = 1

/** Transients per second while running. */
const RATE = 3

const MAX_KICKS = 300
const BINS = 41
const HEIGHT = 240

interface Spread {
  readonly kicks: number
  readonly cold: number
  readonly hot: number
}

interface Walk {
  cold: Float64Array
  hot: Float64Array
  history: Spread[]
  random: () => number
  pending: number
}

const format3 = d3.format('.3f')

function variance(values: Float64Array): number {
  let sum = 0
  let square = 0
  for (const value of values) {
    sum += value
    square += value * value
  }
  const mean = sum / values.length
  return square / values.length - mean * mean
}

function freshWalk(): Walk {
  return {
    cold: new Float64Array(STARS),
    hot: new Float64Array(STARS),
    history: [{ kicks: 0, cold: 0, hot: 0 }],
    random: makeRandom(2024),
    pending: 0
  }
}

/** The predicted variance after n transients: n (KICK F)^2 / 2. */
function predicted(kicks: number, formFactor: number): number {
  return (kicks * (KICK * formFactor) ** 2) / 2
}

/**
 * Angular-momentum diffusion as a random walk. Two populations of 800 stars
 * start at the same L_z; every transient spiral kicks each star by
 * Psi sin(theta) with its own random phase, and Psi is proportional to the form
 * factor, 1 for the cold population and F(E_z) for the hot one. The spread grows
 * as a random walk, Var ~ n (Psi)^2 / 2, and the two variances differ by F^2.
 */
export default function RandomWalk(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const inView = useInView(ref)
  const [energy, setEnergy] = useState(2.5)
  const [running, setRunning] = useState(false)
  const walk = useRef<Walk>(freshWalk())
  const [version, setVersion] = useState(0)
  const formFactor = verticalFormFactor(energy, MILKY_WAY_ALPHA)

  const kick = (): void => {
    const state = walk.current
    const kicks = state.history[state.history.length - 1].kicks
    if (kicks >= MAX_KICKS) {
      setRunning(false)
      return
    }
    for (let i = 0; i < STARS; i += 1) {
      state.cold[i] += KICK * Math.sin(2 * Math.PI * state.random())
      state.hot[i] += KICK * formFactor * Math.sin(2 * Math.PI * state.random())
    }
    state.history.push({ kicks: kicks + 1, cold: variance(state.cold), hot: variance(state.hot) })
    setVersion((v) => v + 1)
  }

  const reset = (): void => {
    walk.current = freshWalk()
    setRunning(false)
    setVersion((v) => v + 1)
  }

  useAnimationFrame(running && inView, (dt) => {
    const state = walk.current
    state.pending += dt * RATE
    while (state.pending >= 1) {
      state.pending -= 1
      kick()
    }
  })

  const state = walk.current
  const last = state.history[state.history.length - 1]
  const columns = columnsFor(width)
  const chartWidth = columnWidth(width, columns)
  const spread = Math.max(3 * Math.sqrt(predicted(Math.max(last.kicks, 1), 1)), 3)

  return (
    <div className="viz" ref={ref} data-version={version}>
      <div className="viz__row">
        <Chart width={chartWidth} height={HEIGHT} xLabel="$\Delta L_z$" yLabel="$N$">
          {(inner) => {
            const x = d3.scaleLinear().domain([-spread, spread]).range([0, inner.width])
            const binner = d3.bin().domain([-spread, spread]).thresholds(BINS)
            const coldBins = binner(Array.from(state.cold))
            const hotBins = binner(Array.from(state.hot))
            const binWidth = (2 * spread) / BINS
            const top = Math.max(
              d3.max(coldBins, (b) => b.length) ?? 1,
              d3.max(hotBins, (b) => b.length) ?? 1,
              1
            )
            const y = d3
              .scaleLinear()
              .domain([0, 1.1 * top])
              .range([inner.height, 0])
            const gaussian = (sigmaSquare: number): string => {
              if (sigmaSquare <= 0) {
                return ''
              }
              const points = d3.range(-spread, spread + 0.01, spread / 60).map((value) => {
                const density =
                  Math.exp(-(value * value) / (2 * sigmaSquare)) /
                  Math.sqrt(2 * Math.PI * sigmaSquare)
                return [x(value), y(STARS * binWidth * density)] as const
              })
              return linePath(points)
            }
            const bars = (bins: d3.Bin<number, number>[], className: string): ReactNode =>
              bins.map((bin, i) => (
                <rect
                  key={i}
                  x={x(bin.x0 ?? 0)}
                  y={y(bin.length)}
                  width={Math.max(x(bin.x1 ?? 0) - x(bin.x0 ?? 0) - 1, 1)}
                  height={inner.height - y(bin.length)}
                  className={className}
                />
              ))
            return (
              <>
                {bars(coldBins, 'viz-fill--cold')}
                {bars(hotBins, 'viz-fill--hot')}
                <path d={gaussian(predicted(last.kicks, 1))} className="viz-line viz-line--cold" />
                <path
                  d={gaussian(predicted(last.kicks, formFactor))}
                  className="viz-line viz-line--hot"
                />
                <Axis scale={y} orientation="left" ticks={4} />
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
        <Chart width={chartWidth} height={HEIGHT} xLabel="$n$" yLabel="$\mathrm{Var}(\Delta L_z)$">
          {(inner) => {
            const kicksShown = Math.max(last.kicks, 20)
            const x = d3.scaleLinear().domain([0, kicksShown]).range([0, inner.width])
            const y = d3
              .scaleLinear()
              .domain([0, 1.15 * predicted(kicksShown, 1)])
              .range([inner.height, 0])
            const series = (pick: (record: Spread) => number): string =>
              linePath(state.history.map((record) => [x(record.kicks), y(pick(record))] as const))
            const line = (factor: number): string =>
              linePath([
                [x(0), y(0)],
                [x(kicksShown), y(predicted(kicksShown, factor))]
              ])
            return (
              <>
                <path
                  d={line(1)}
                  className="viz-line viz-line--cold viz-line--dashed viz-line--thin"
                />
                <path
                  d={line(formFactor)}
                  className="viz-line viz-line--hot viz-line--dashed viz-line--thin"
                />
                <path d={series((r) => r.cold)} className="viz-line viz-line--cold" />
                <path d={series((r) => r.hot)} className="viz-line viz-line--hot" />
                <Axis scale={y} orientation="left" ticks={4} />
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
          label="$E_z$"
          value={energy}
          min={0.05}
          max={8}
          step={0.05}
          onChange={(value) => {
            setEnergy(value)
            reset()
          }}
        />
        <Button label="One transient" onClick={kick} />
        <Button label={running ? 'Pause' : 'Run'} onClick={() => setRunning(!running)} primary />
        <Button label="Reset" onClick={reset} />
        <Readout
          items={[
            ['$F$', format3(formFactor)],
            ['$F^2$', format3(formFactor * formFactor)],
            ['$n$', `${last.kicks}`],
            [
              '$\\mathrm{Var}_{\\rm hot}/\\mathrm{Var}_{\\rm cold}$',
              last.kicks > 0 ? format3(last.hot / last.cold) : '-'
            ]
          ]}
        />
      </Controls>
      <p className="viz-note">
        Blue: the cold population (F = 1). Red: the hot one, with F from the isothermal sheet at the
        Milky Way thickness. Dashed lines and curves are the prediction n (Psi)^2 / 2 for each.
      </p>
    </div>
  )
}
