import Chart, { Axis, linePath } from '@site/src/components/viz/Chart'
import { Controls, Readout, Slider } from '@site/src/components/viz/Controls'
import { columnWidth, columnsFor, useElementWidth } from '@site/src/components/viz/hooks'
import {
  SOLAR_NEIGHBORHOOD,
  slopeAgeFactor,
  slopeInSolarUnits,
  structuralSlope
} from '@site/src/physics/slope'
import * as d3 from 'd3'
import React, { type ReactNode, useState } from 'react'

const HEIGHT = 260
const AGE_MAX = 12
const REFERENCE_AGE = 1
const MEASURED_SLOPE = 3.7e-2
const ANISOTROPY_RANGE: readonly [number, number] = [1, 3]

const format2 = d3.format('.2f')
const format1 = d3.format('.1f')

/**
 * The structural slope of Equation (15) against the heating anisotropy, and its
 * age running of Equation (16) for the two exponents of the age-velocity-dispersion
 * relations.
 */
export default function SlopeExplorer(): ReactNode {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const [sigmaR, setSigmaR] = useState(SOLAR_NEIGHBORHOOD.sigmaR)
  const [sigmaZ, setSigmaZ] = useState(SOLAR_NEIGHBORHOOD.sigmaZ)
  const [surfaceDensity, setSurfaceDensity] = useState(SOLAR_NEIGHBORHOOD.surfaceDensity)
  const [cMax, setCMax] = useState(1)
  const [betaR, setBetaR] = useState(0.35)
  const [betaZ, setBetaZ] = useState(0.5)

  const env = { ...SOLAR_NEIGHBORHOOD, sigmaR, sigmaZ, surfaceDensity }
  const slope = structuralSlope(env, cMax)
  const slopeSolar = slopeInSolarUnits(env, cMax)
  const anisotropy = sigmaR / sigmaZ
  const exponent = 2 * (betaR - betaZ)

  const columns = columnsFor(width)
  const chartWidth = columnWidth(width, columns)

  return (
    <div className="viz" ref={ref}>
      <div className="viz__row">
        <Chart
          width={chartWidth}
          height={HEIGHT}
          xLabel="$\sigma_R/\sigma_z$"
          yLabel="$a$ ($10^{-2}\,L_\odot/\mathrm{kpc}$)"
        >
          {(inner) => {
            const x = d3.scaleLinear().domain(ANISOTROPY_RANGE).range([0, inner.width])
            const atRatio = (ratio: number): number =>
              100 * slopeInSolarUnits({ ...env, sigmaR: ratio * sigmaZ }, cMax)
            const y = d3
              .scaleLinear()
              .domain([0, 1.1 * atRatio(ANISOTROPY_RANGE[1])])
              .range([inner.height, 0])
            const curve = d3
              .range(ANISOTROPY_RANGE[0], ANISOTROPY_RANGE[1] + 0.01, 0.02)
              .map((ratio) => [x(ratio), y(atRatio(ratio))] as const)
            return (
              <>
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(100 * MEASURED_SLOPE)}
                  y2={y(100 * MEASURED_SLOPE)}
                  className="viz-line viz-line--muted viz-line--dashed"
                />
                <text x={4} y={y(100 * MEASURED_SLOPE) - 5} className="viz-text viz-text--muted">
                  measured 3.7
                </text>
                <path d={linePath(curve)} className="viz-line viz-line--cold" />
                <circle
                  cx={x(Math.min(Math.max(anisotropy, ANISOTROPY_RANGE[0]), ANISOTROPY_RANGE[1]))}
                  cy={y(100 * slopeSolar)}
                  r={5}
                  className="viz-dot--accent"
                />
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
          xLabel="age (Gyr)"
          yLabel="$a(\mathrm{age})/a(1\,\mathrm{Gyr})$"
        >
          {(inner) => {
            const x = d3.scaleLinear().domain([0, AGE_MAX]).range([0, inner.width])
            const y = d3.scaleLinear().domain([0, 2]).range([inner.height, 0])
            const curve = d3
              .range(0.25, AGE_MAX + 0.01, 0.05)
              .map((age) => [x(age), y(slopeAgeFactor(age, REFERENCE_AGE, betaR, betaZ))] as const)
            return (
              <>
                <line
                  x1={0}
                  x2={inner.width}
                  y1={y(1)}
                  y2={y(1)}
                  className="viz-line viz-line--muted viz-line--dotted viz-line--thin"
                />
                <path d={linePath(curve)} className="viz-line viz-line--cold" />
                <circle
                  cx={x(8)}
                  cy={y(slopeAgeFactor(8, REFERENCE_AGE, betaR, betaZ))}
                  r={5}
                  className="viz-dot--accent"
                />
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
          label="$\sigma_R$"
          value={sigmaR}
          min={15}
          max={60}
          step={0.5}
          onChange={setSigmaR}
          format={format1}
        />
        <Slider
          label="$\sigma_z$"
          value={sigmaZ}
          min={8}
          max={40}
          step={0.5}
          onChange={setSigmaZ}
          format={format1}
        />
        <Slider
          label="$\Sigma$"
          value={surfaceDensity}
          min={30}
          max={90}
          step={1}
          onChange={setSurfaceDensity}
          format={(v) => v.toFixed(0)}
        />
        <Slider label="$c_{\max}$" value={cMax} min={0.5} max={2} step={0.05} onChange={setCMax} />
        <Slider label="$\beta_R$" value={betaR} min={0} max={0.8} step={0.01} onChange={setBetaR} />
        <Slider label="$\beta_z$" value={betaZ} min={0} max={0.8} step={0.01} onChange={setBetaZ} />
      </Controls>
      <Controls>
        <Readout
          items={[
            ['$a$ (km/s)', format1(slope)],
            ['$a$ ($10^{-2}\\,L_\\odot/\\mathrm{kpc}$)', format2(100 * slopeSolar)],
            ['$(\\sigma_R/\\sigma_z)^2$', format2(anisotropy * anisotropy)],
            ['$2(\\beta_R - \\beta_z)$', format2(exponent)],
            [
              '$a(8\\,\\mathrm{Gyr})/a(1\\,\\mathrm{Gyr})$',
              format2(slopeAgeFactor(8, REFERENCE_AGE, betaR, betaZ))
            ]
          ]}
        />
      </Controls>
      <p className="viz-note">
        Dispersions in km/s, the surface density in solar masses per square parsec, the epicyclic
        frequency fixed at 37 km/s/kpc and L_sun = R_0 V_0 with R_0 = 8.2 kpc and V_0 = 233 km/s.
      </p>
    </div>
  )
}
