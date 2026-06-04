import fs from 'node:fs'
import path from 'node:path'

import type * as Preset from '@docusaurus/preset-classic'
import type { Config } from '@docusaurus/types'
import { themes as prismThemes } from 'prism-react-renderer'
import rehypeKatex from 'rehype-katex'
import remarkMath from 'remark-math'

const baseUrl = process.env.DOCS_BASE_URL ?? '/jr-hz-relation/'

const pyprojectPath = path.resolve(__dirname, '../jr_hz_relation/pyproject.toml')
const pyprojectContent = fs.readFileSync(pyprojectPath, 'utf-8')
const versionMatch = pyprojectContent.match(/^version\s*=\s*"([^"]+)"/m)
const libraryVersion = versionMatch?.[1] ?? '0.0.0'

const rootPkgPath = path.resolve(__dirname, '../../package.json')
const rootPkg = JSON.parse(fs.readFileSync(rootPkgPath, 'utf-8'))
const projectVersion = rootPkg.version ?? '0.0.0'

const config: Config = {
  title: 'The Provenance Bias',
  tagline: 'An analytic provenance bias and the spiral J_R-h_Z relation',

  url: 'https://caverac.github.io',
  baseUrl,

  organizationName: 'cavera',
  projectName: 'jr-hz-relation',

  onBrokenLinks: 'warn',

  customFields: {
    libraryVersion,
    projectVersion
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en']
  },

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css',
      type: 'text/css',
      integrity: 'sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+',
      crossorigin: 'anonymous'
    }
  ],

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn'
    }
  },

  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        language: ['en'],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
        docsRouteBasePath: '/',
        indexBlog: false
      }
    ]
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex]
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css'
        }
      } satisfies Preset.Options
    ]
  ],

  themeConfig: {
    navbar: {
      title: 'The Provenance Bias',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Documentation'
        },
        {
          href: 'https://github.com/caverac/jr-hz-relation',
          label: 'GitHub',
          position: 'right'
        }
      ]
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Introduction', to: '/' },
            { label: 'The vertical form factor', to: '/theory/form-factor' }
          ]
        }
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Carlos Vera-Ciro. Built with Docusaurus.`
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash']
    }
  } satisfies Preset.ThemeConfig
}

export default config
