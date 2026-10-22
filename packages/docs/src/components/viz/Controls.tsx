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

export type Icon = 'play' | 'pause' | 'step' | 'reset'

/** Icon outlines on a 24 by 24 grid. */
const ICON_PATHS: Record<Icon, string> = {
  play: 'M8 5v14l11-7z',
  pause: 'M6 5h4v14H6zm8 0h4v14h-4z',
  step: 'M6 18l8.5-6L6 6v12zm10-12v12h2V6h-2z',
  reset:
    'M12 5V2L7 7l5 5V8c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z'
}

interface IconButtonProps {
  readonly icon: Icon
  /** The accessible name of the button, also shown as its tooltip. */
  readonly label: string
  readonly onClick: () => void
  readonly primary?: boolean
}

/** A small button in the site's style that shows an icon. */
export function IconButton({ icon, label, onClick, primary = false }: IconButtonProps): ReactNode {
  return (
    <button
      type="button"
      className={`button button--sm viz-icon-button ${primary ? 'button--primary' : 'button--secondary'}`}
      onClick={onClick}
      aria-label={label}
      title={label}
    >
      <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
        <path d={ICON_PATHS[icon]} fill="currentColor" />
      </svg>
    </button>
  )
}

interface NoteProps {
  /** The note, with inline math between dollar signs. */
  readonly text: string
}

/** The short note under a figure that names its colors, lines and units. */
export function Note({ text }: NoteProps): ReactNode {
  return (
    <p className="viz-note">
      <MathLabel label={text} />
    </p>
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
