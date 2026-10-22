import useBaseUrl from '@docusaurus/useBaseUrl'
import React, { type ReactNode } from 'react'

interface FigureProps {
  /** Path under the static directories, such as `/figures/form-factor.png`. */
  readonly src: string
  readonly alt: string
  /** Two-panel figures keep the full column width. */
  readonly wide?: boolean
}

/** A static figure drawn by the Python package, centered and sized for the column. */
export default function Figure({ src, alt, wide = false }: FigureProps): ReactNode {
  return (
    <figure className={wide ? 'scientific wide' : 'scientific'}>
      <img src={useBaseUrl(src)} alt={alt} />
    </figure>
  )
}
