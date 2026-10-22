import MathLabel from '@site/src/components/MathLabel'
import * as d3 from 'd3'
import React, { type ReactNode, useEffect, useId, useRef } from 'react'

export interface Margin {
  readonly top: number
  readonly right: number
  readonly bottom: number
  readonly left: number
}

export const DEFAULT_MARGIN: Margin = { top: 12, right: 16, bottom: 32, left: 48 }

/** Width of the gutter that holds a rotated axis label. */
const LABEL_GUTTER = 26

export interface InnerSize {
  readonly width: number
  readonly height: number
  /** The clip-path URL of the plot area, for layers that may spill beyond it. */
  readonly clip: string
}

interface ChartProps {
  /** Outer width, usually the measured width of the container. */
  readonly width: number
  readonly height: number
  readonly margin?: Margin
  /** Axis labels, with inline math between dollar signs. */
  readonly xLabel?: string
  readonly yLabel?: string
  readonly children: (inner: InnerSize) => ReactNode
}

/**
 * An SVG chart with its axis labels set in HTML around it, so that they can
 * carry KaTeX. The children are drawn inside the margins and receive the inner
 * size.
 */
export default function Chart({
  width,
  height,
  margin = DEFAULT_MARGIN,
  xLabel,
  yLabel,
  children
}: ChartProps): ReactNode {
  const clipId = `clip-${useId().replace(/[^a-zA-Z0-9]/g, '')}`
  const svgWidth = width - (yLabel === undefined ? 0 : LABEL_GUTTER)
  const inner: InnerSize = {
    width: Math.max(svgWidth - margin.left - margin.right, 10),
    height: Math.max(height - margin.top - margin.bottom, 10),
    clip: `url(#${clipId})`
  }
  return (
    <div className="viz-chart">
      {yLabel === undefined ? null : (
        <div className="viz-chart__ylabel" style={{ height }}>
          <span className="viz-chart__ylabel-text">
            <MathLabel label={yLabel} />
          </span>
        </div>
      )}
      <svg
        className="viz-chart__svg"
        width={svgWidth}
        height={height}
        viewBox={`0 0 ${svgWidth} ${height}`}
      >
        <defs>
          <clipPath id={clipId}>
            <rect x={0} y={0} width={inner.width} height={inner.height} />
          </clipPath>
        </defs>
        <g transform={`translate(${margin.left},${margin.top})`}>{children(inner)}</g>
      </svg>
      {xLabel === undefined ? null : (
        <div className="viz-chart__xlabel" style={{ paddingLeft: margin.left }}>
          <MathLabel label={xLabel} />
        </div>
      )}
    </div>
  )
}

interface AxisProps {
  readonly scale: d3.ScaleLinear<number, number> | d3.ScaleLogarithmic<number, number>
  readonly orientation: 'bottom' | 'left'
  readonly transform?: string
  readonly ticks?: number
  /** Explicit tick positions, which take precedence over the tick count. */
  readonly tickValues?: readonly number[]
  readonly tickFormat?: (value: number) => string
  /** Length of grid lines drawn across the plot, if any. */
  readonly gridLength?: number
}

/** A D3 axis rendered into a group, redrawn whenever its scale changes. */
export function Axis({
  scale,
  orientation,
  transform,
  ticks = 5,
  tickValues,
  tickFormat,
  gridLength
}: AxisProps): ReactNode {
  const ref = useRef<SVGGElement>(null)
  useEffect(() => {
    const group = ref.current
    if (group === null) {
      return
    }
    const axis = orientation === 'bottom' ? d3.axisBottom(scale) : d3.axisLeft(scale)
    axis.ticks(ticks)
    if (tickValues !== undefined) {
      axis.tickValues([...tickValues])
    }
    if (tickFormat !== undefined) {
      axis.tickFormat((value) => tickFormat(value.valueOf()))
    }
    if (gridLength !== undefined) {
      axis.tickSizeInner(-gridLength)
      axis.tickPadding(8)
    }
    const selection = d3.select(group)
    selection.call(axis)
    selection.selectAll('.tick line').attr('class', gridLength === undefined ? null : 'viz-grid')
  }, [scale, orientation, ticks, tickValues, tickFormat, gridLength])
  return <g ref={ref} className="viz-axis" transform={transform} />
}

interface ScriptPart {
  readonly kind: 'text' | 'sub' | 'sup'
  readonly value: string
}

/**
 * Splits a label such as `2πJ_R` or `F^2` into runs of text, subscripts and
 * superscripts. A script is the character after `_` or `^`, or the group in
 * braces after it.
 */
function parseScripts(text: string): ScriptPart[] {
  const parts: ScriptPart[] = []
  let run = ''
  let i = 0
  while (i < text.length) {
    const char = text[i]
    if ((char === '_' || char === '^') && i + 1 < text.length) {
      if (run !== '') {
        parts.push({ kind: 'text', value: run })
        run = ''
      }
      const kind = char === '_' ? 'sub' : 'sup'
      if (text[i + 1] === '{') {
        const close = text.indexOf('}', i + 2)
        const end = close === -1 ? text.length : close
        parts.push({ kind, value: text.slice(i + 2, end) })
        i = end + 1
      } else {
        parts.push({ kind, value: text[i + 1] })
        i += 2
      }
    } else {
      run += char
      i += 1
    }
  }
  if (run !== '') {
    parts.push({ kind: 'text', value: run })
  }
  return parts
}

/** Vertical offsets of a script, in px, and the return to the baseline after it. */
const SCRIPT_SHIFT = { sub: 3, sup: -5 }

interface SvgLabelProps {
  readonly x: number
  readonly y: number
  /** The label, with `_` and `^` introducing a subscript or a superscript. */
  readonly text: string
  readonly anchor?: 'start' | 'middle' | 'end'
  readonly className?: string
}

/** A short label inside the plot, with subscripts and superscripts as tspans. */
export function SvgLabel({
  x,
  y,
  text,
  anchor = 'start',
  className = 'viz-text'
}: SvgLabelProps): ReactNode {
  let pending = 0
  return (
    <text x={x} y={y} textAnchor={anchor} className={className}>
      {parseScripts(text).map((part, index) => {
        const shift = part.kind === 'text' ? 0 : SCRIPT_SHIFT[part.kind]
        const dy = shift - pending
        pending = shift
        return (
          <tspan key={index} dy={dy} fontSize={part.kind === 'text' ? undefined : '75%'}>
            {part.value}
          </tspan>
        )
      })}
    </text>
  )
}

/** A path through (x, y) pairs already in pixel coordinates. */
export function linePath(points: ReadonlyArray<readonly [number, number]>): string {
  const generator = d3
    .line<readonly [number, number]>()
    .x((point) => point[0])
    .y((point) => point[1])
  return generator(points) ?? ''
}
