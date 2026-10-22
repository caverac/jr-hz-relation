import MathLabel from '@site/src/components/MathLabel'
import React, { type ReactNode } from 'react'

interface SliderProps {
  /** Label with inline math between dollar signs. */
  readonly label: string
  readonly value: number
  readonly min: number
  readonly max: number
  readonly step: number
  readonly onChange: (value: number) => void
  /** Formats the value shown next to the slider; defaults to two decimals. */
  readonly format?: (value: number) => string
}

/** A labeled range input with its current value. */
export function Slider({ label, value, min, max, step, onChange, format }: SliderProps): ReactNode {
  const shown = format === undefined ? value.toFixed(2) : format(value)
  return (
    <label className="viz-slider">
      <span className="viz-slider__label">
        <MathLabel label={label} />
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      <span className="viz-slider__value">{shown}</span>
    </label>
  )
}

interface ReadoutProps {
  /** Pairs of label (with math) and formatted value. */
  readonly items: ReadonlyArray<readonly [string, string]>
}

/** A row of labeled values computed from the current controls. */
export function Readout({ items }: ReadoutProps): ReactNode {
  return (
    <dl className="viz-readout">
      {items.map(([label, value]) => (
        <div key={label} className="viz-readout__item">
          <dt>
            <MathLabel label={label} />
          </dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  )
}

interface ButtonProps {
  readonly label: string
  readonly onClick: () => void
  readonly primary?: boolean
}

/** A small button in the site's style. */
export function Button({ label, onClick, primary = false }: ButtonProps): ReactNode {
  return (
    <button
      type="button"
      className={`button button--sm ${primary ? 'button--primary' : 'button--secondary'}`}
      onClick={onClick}
    >
      {label}
    </button>
  )
}

interface ControlsProps {
  readonly children: ReactNode
}

/** The strip of sliders, buttons and readouts under a figure. */
export function Controls({ children }: ControlsProps): ReactNode {
  return <div className="viz-controls">{children}</div>
}

interface SelectProps {
  readonly label: string
  readonly value: string
  readonly options: ReadonlyArray<readonly [string, string]>
  readonly onChange: (value: string) => void
}

/** A labeled drop-down of (value, text) options. */
export function Select({ label, value, options, onChange }: SelectProps): ReactNode {
  return (
    <label className="viz-slider">
      <span className="viz-slider__label">
        <MathLabel label={label} />
      </span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map(([option, text]) => (
          <option key={option} value={option}>
            {text}
          </option>
        ))}
      </select>
    </label>
  )
}
