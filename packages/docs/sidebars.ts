import type { SidebarsConfig } from '@docusaurus/plugin-content-docs'

// The Primer carries the background a reader with some physics needs for the
// numbered sections, which mirror the manuscript in reading order: the Theory
// and Results categories group the five physics sections, and Discussion and
// Library are flat.
const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Primer',
      collapsed: false,
      items: ['primer/orbits', 'primer/resonance', 'primer/diffusion']
    },
    {
      type: 'category',
      label: 'Theory',
      collapsed: false,
      items: ['theory/form-factor', 'theory/corotation-hamiltonian', 'theory/resonance-overlap']
    },
    {
      type: 'category',
      label: 'Results',
      collapsed: false,
      items: ['results/provenance-bias', 'results/nbody-test']
    },
    'discussion',
    {
      type: 'category',
      label: 'Library',
      items: ['library/usage']
    }
  ]
}

export default sidebars
