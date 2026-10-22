import { useColorMode } from '@docusaurus/theme-common'
import { type RefObject, useEffect, useRef, useState } from 'react'

/** Width the server renders with, before the container has been measured. */
export const FALLBACK_WIDTH = 640

/** Horizontal padding of the figure box plus the gap between its columns, in px. */
const BOX_PADDING = 24
const COLUMN_GAP = 12

/** Number of chart columns that fit in a figure box of the given width. */
export function columnsFor(width: number): number {
  return width >= 620 ? 2 : 1
}

/** Width of one chart when the box is split into `columns`. */
export function columnWidth(width: number, columns: number): number {
  return Math.floor((width - BOX_PADDING - COLUMN_GAP * (columns - 1)) / columns)
}

/** A small deterministic generator (mulberry32), so that a reset replays the same draw. */
export function makeRandom(seed: number): () => number {
  let state = seed >>> 0
  return () => {
    state = (state + 0x6d2b79f5) >>> 0
    let t = state
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/**
 * The current width of a container, followed through a ResizeObserver. The
 * first render uses the fallback on both server and client, so hydration sees
 * the same markup; the measured width arrives in an effect.
 */
export function useElementWidth<T extends HTMLElement>(): [RefObject<T | null>, number] {
  const ref = useRef<T>(null)
  const [width, setWidth] = useState(FALLBACK_WIDTH)
  useEffect(() => {
    const element = ref.current
    if (element === null) {
      return undefined
    }
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0]
      if (entry !== undefined) {
        setWidth(Math.max(Math.floor(entry.contentRect.width), 240))
      }
    })
    observer.observe(element)
    setWidth(Math.max(Math.floor(element.getBoundingClientRect().width), 240))
    return () => observer.disconnect()
  }, [])
  return [ref, width]
}

/** Whether an element is at least partly inside the viewport. */
export function useInView<T extends Element>(ref: RefObject<T | null>): boolean {
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const element = ref.current
    if (element === null) {
      return undefined
    }
    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0]
        if (entry !== undefined) {
          setInView(entry.isIntersecting)
        }
      },
      { threshold: 0.1 }
    )
    observer.observe(element)
    return () => observer.disconnect()
  }, [ref])
  return inView
}

/**
 * Calls `onFrame(dt)` once per animation frame while `active`, with `dt` the
 * elapsed time in seconds, capped so that a background tab does not deliver one
 * enormous step when it comes back.
 */
export function useAnimationFrame(active: boolean, onFrame: (dt: number) => void): void {
  const callback = useRef(onFrame)
  callback.current = onFrame
  useEffect(() => {
    if (!active) {
      return undefined
    }
    let handle = 0
    let last = performance.now()
    const tick = (now: number): void => {
      const dt = Math.min((now - last) / 1000, 0.05)
      last = now
      callback.current(dt)
      handle = requestAnimationFrame(tick)
    }
    handle = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(handle)
  }, [active])
}

/** The colors of the figures, read from the CSS custom properties of the theme. */
export interface Palette {
  readonly fg: string
  readonly muted: string
  readonly grid: string
  readonly cold: string
  readonly hot: string
  readonly accent: string
  readonly background: string
}

const LIGHT_PALETTE: Palette = {
  fg: '#1c1e21',
  muted: '#7a7f87',
  grid: 'rgba(0, 0, 0, 0.1)',
  cold: '#2563eb',
  hot: '#dc2626',
  accent: '#d97706',
  background: '#ffffff'
}

function readPalette(): Palette {
  const style = getComputedStyle(document.documentElement)
  const read = (name: string, fallback: string): string =>
    style.getPropertyValue(name).trim() || fallback
  return {
    fg: read('--viz-fg', LIGHT_PALETTE.fg),
    muted: read('--viz-muted', LIGHT_PALETTE.muted),
    grid: read('--viz-grid', LIGHT_PALETTE.grid),
    cold: read('--viz-cold', LIGHT_PALETTE.cold),
    hot: read('--viz-hot', LIGHT_PALETTE.hot),
    accent: read('--viz-accent', LIGHT_PALETTE.accent),
    background: read('--viz-background', LIGHT_PALETTE.background)
  }
}

/**
 * The palette of the current color mode, for drawing on a canvas, where CSS
 * variables cannot be used. SVG drawings use the variables directly.
 */
export function usePalette(): Palette {
  const { colorMode } = useColorMode()
  const [palette, setPalette] = useState(LIGHT_PALETTE)
  useEffect(() => {
    setPalette(readPalette())
  }, [colorMode])
  return palette
}
