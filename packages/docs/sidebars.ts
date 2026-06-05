import type { SidebarsConfig } from '@docusaurus/plugin-content-docs'

// One entry per manuscript section, in reading order. The Theory and Results
// categories group the five physics sections; Discussion and Library are flat.
const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
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
      items: ['results/provenance-bias']
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
