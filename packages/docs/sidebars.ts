import type { SidebarsConfig } from '@docusaurus/plugin-content-docs'

const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Theory',
      items: ['theory/form-factor', 'theory/provenance-bias']
    },
    {
      type: 'category',
      label: 'Results',
      items: ['results/slope', 'results/predictions']
    },
    {
      type: 'category',
      label: 'Library',
      items: ['library/usage']
    }
  ]
}

export default sidebars
