# Design System - Sistema de Análise de Estatísticas de Futebol

**Versão:** 1.2
**Data:** 11 de fevereiro de 2026
**Status:** ✅ Completo

Sistema completo de design tokens e componentes visuais para a implementação do frontend em React + TypeScript.

---

## 📋 Índice

1. [Design Tokens](#design-tokens)
2. [Biblioteca de Componentes](#biblioteca-de-componentes)
3. [Animações e Transições](#animações-e-transições)
4. [Implementação no Tailwind](#implementação-no-tailwind)
5. [Guia de Uso](#guia-de-uso)
6. [Ver Também](#ver-também)

---

## Design Tokens

### 1. Paleta de Cores

#### Cor Primária (Lime - Decisão do Usuário ✅)

```typescript
// Primary Brand Color - Lime Green
primary-50:   #f0fdf4   // Lightest
primary-100:  #dcfce7
primary-200:  #bbf7d0
primary-300:  #86efac
primary-400:  #4ade80
primary-500:  #22c55e   // Base primary
primary-600:  #16a34a   // Hover
primary-700:  #15803d   // Active
primary-800:  #166534
primary-900:  #145231   // Darkest

// DECISÃO DO USUÁRIO: Usar LIME #84cc16 (mais vibrante)
lime-50:      #f7fee7
lime-100:     #ecfccf
lime-200:     #d9f99d
lime-300:     #bfef45
lime-400:     #a3e635
lime-500:     #84cc16   // ⭐ PRIMARY COLOR (DECISÃO DO USUÁRIO)
lime-600:     #65a30d
lime-700:     #4d7c0f
lime-800:     #3f6212
lime-900:     #365314
```

#### Cores Semânticas

```typescript
// Status & Sentiment Colors
success-primary:    #10b981   // Win (W) - Verde Esmeralda
success-hover:      #059669
success-dark:       #047857

warning-primary:    #f59e0b   // Draw (D) - Âmbar
warning-hover:      #d97706
warning-dark:       #b45309

danger-primary:     #ef4444   // Loss (L) - Vermelho
danger-hover:       #dc2626
danger-dark:        #b91c1c

info-primary:       #3b82f6   // Informações - Azul
info-hover:         #2563eb
info-dark:          #1d4ed8
```

#### Camadas de Background (Dark Mode - Tema Padrão ✅)

```typescript
// Primary Layer - Fundo Principal da Página
bg-primary:         #0a0a0a   // Contraste excelente para Lime
bg-primary-hover:   #121212

// Secondary Layer - Cards e Painéis
bg-secondary:       #171717
bg-secondary-hover: #1f1f1f

// Tertiary Layer - Elementos Elevados
bg-tertiary:        #262626
bg-tertiary-hover:  #2d2d2d

// Quaternary Layer - Inputs e Modais
bg-quaternary:      #404040
bg-quaternary-hover: #4d4d4d

// Overlay (Modal Backdrop)
overlay-dark:       rgba(0, 0, 0, 0.5)
overlay-darker:     rgba(0, 0, 0, 0.7)
overlay-darkest:    rgba(0, 0, 0, 0.9)
```

#### Hierarquia de Texto

```typescript
// Text Hierarchy
text-primary:       #fafafa   // Texto principal (high contrast)
text-secondary:     #a3a3a3   // Texto secundário
text-tertiary:      #737373   // Labels, hints
text-muted:         #525252   // Disabled, faded
text-inverse:       #0a0a0a   // Para backgrounds claros (não usar em dark mode)

// Contraste com Lime #84cc16:
// Lime on #0a0a0a: 8.5:1 ✅ (WCAG AAA - Excelente)
// Lime on #171717: 7.8:1 ✅ (WCAG AAA)
// Lime on #262626: 7.2:1 ✅ (WCAG AAA)
```

---

### 2. Tipografia

#### Famílias de Fontes

```typescript
// Font Stack (Fallbacks Inclusos)
font-display:  'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
font-body:     'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
font-mono:     'Space Mono', 'Courier New', monospace

// Google Fonts imports:
// Import real do projeto (index.html):
// https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap
// Observação: 'Inter' está como fallback no Tailwind, mas não é carregada por padrão.
```

#### Tamanhos de Fonte (Escala Modular - Razão 1.125)

```typescript
// Font Sizes (Typography Scale)
text-xs:        0.75rem    // 12px
text-sm:        0.875rem   // 14px
text-base:      1rem       // 16px
text-lg:        1.125rem   // 18px
text-xl:        1.25rem    // 20px
text-2xl:       1.5rem     // 24px
text-3xl:       1.875rem   // 30px
text-4xl:       2.25rem    // 36px
text-5xl:       2.813rem   // 45px (Headings only)

// Uso recomendado:
// text-5xl: h1 (Títulos principais)
// text-4xl: h2 (Seções principais)
// text-3xl: h3 (Subseções)
// text-2xl: h4, labels grandes
// text-lg, text-xl: Corpo texto principal
// text-base: Corpo padrão
// text-sm: Texto secundário
// text-xs: Labels, hints
```

#### Pesos de Fonte (Font Weights)

```typescript
font-light:        300   // Títulos elegantes, faded
font-normal:       400   // Corpo padrão (default)
font-medium:       500   // Ênfase, labels
font-semibold:     600   // Subtítulos, strong
font-bold:         700   // Títulos, destaque
font-extrabold:    800   // Títulos impactantes

// Recomendações por Contexto:
// Outfit display (titulos):     300-700
// Inter body (corpo):           400-600
// Space Mono (números):         400-700
```

#### Line Heights

```typescript
leading-tight:    1.25     // Títulos, compact
leading-normal:   1.5      // Padrão (recomendado)
leading-relaxed:  1.75     // Corpo texto, legibilidade
leading-loose:    2        // Descrições longas
```

#### Letter Spacing

```typescript
tracking-tight:   -0.01em
tracking-normal:  0
tracking-wide:    0.025em
tracking-wider:   0.05em
```

---

### 3. Espaçamento (Spacing Scale)

Sistema baseado em **4px** (0.25rem = 1 unit).

```typescript
// Spacing Units
spacing-0:        0          // 0px
spacing-1:        0.25rem    // 4px
spacing-2:        0.5rem     // 8px
spacing-3:        0.75rem    // 12px
spacing-4:        1rem       // 16px
spacing-6:        1.5rem     // 24px
spacing-8:        2rem       // 32px
spacing-12:       3rem       // 48px
spacing-16:       4rem       // 64px
spacing-20:       5rem       // 80px
spacing-24:       6rem       // 96px

// Recomendações de Uso:
// spacing-1:   Micro spacing (between icon + text)
// spacing-2:   Component internal padding
// spacing-3:   Label - input gaps
// spacing-4:   Default padding (cards, buttons)
// spacing-6:   Section spacing
// spacing-8:   Major spacing (between sections)
// spacing-12+: Page-level spacing
```

---

### 4. Border Radius

```typescript
rounded-none:     0
rounded-sm:       0.25rem    // 4px
rounded:          0.375rem   // 6px
rounded-md:       0.5rem     // 8px (DEFAULT para cards)
rounded-lg:       0.75rem    // 12px
rounded-xl:       1rem       // 16px (Para components elevados)
rounded-2xl:      1.5rem     // 24px
rounded-full:     9999px     // Circles, pills

// Recomendações:
// rounded-md: Cards, inputs, buttons (padrão)
// rounded-lg: Modal, dropdown, elevated surfaces
// rounded-xl: Large rounded components
// rounded-full: Badges redondos, avatares circulares, team badges
```

---

### 5. Sombras (Shadow System)

```typescript
// Shadows (Elevation System)
shadow-none:      none
shadow-sm:        0 1px 2px rgba(0, 0, 0, 0.5)
shadow:           0 4px 6px rgba(0, 0, 0, 0.6)
shadow-md:        0 6px 12px rgba(0, 0, 0, 0.7)
shadow-lg:        0 10px 20px rgba(0, 0, 0, 0.8)
shadow-xl:        0 14px 28px rgba(0, 0, 0, 0.85)

// Glow Effect (Lime Green - Caractéristico)
shadow-glow:      0 0 20px rgba(132, 204, 22, 0.3)
shadow-glow-lg:   0 0 40px rgba(132, 204, 22, 0.4)

// Inset Shadow (para depth)
shadow-inset:     inset 0 2px 4px rgba(0, 0, 0, 0.4)
```

---

### 6. Animações e Transições

#### Durations (Velocidades)

```typescript
duration-75:      75ms
duration-100:     100ms
duration-150:     150ms   // FAST (hover states)
duration-200:     200ms   // FAST (fade in)
duration-300:     300ms   // NORMAL (default)
duration-500:     500ms   // SLOW (enter animations)
duration-700:     700ms   // SLOW (full page transitions)
duration-1000:    1000ms  // VERY SLOW (intro animations)

// Recomendações:
// duration-150: Hover states, quick feedback
// duration-300: Default transitions, hover effects
// duration-500: Enter/exit animations, important transitions
// duration-1000: Staggered reveals, intro animations
```

#### Easing Functions

```typescript
// Timing Functions
ease-linear:      linear
ease-in:          cubic-bezier(0.4, 0, 1, 1)
ease-out:         cubic-bezier(0, 0, 0.2, 1)
ease-in-out:      cubic-bezier(0.4, 0, 0.2, 1)
ease-bounce:      cubic-bezier(0.68, -0.55, 0.265, 1.55)

// Recomendações:
// ease-out: Enters (elementos aparecem)
// ease-in: Exits (elementos desaparecem)
// ease-in-out: Hover states, smooth transitions
// ease-linear: Progress bars, continuous motion
```

#### Keyframes Principais

```typescript
// Fade In
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

// Slide Up (Para MatchCards)
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Scale Up (Para modal entrance)
@keyframes scaleUp {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

// Pulse (Para loading states, status indicators)
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

// Glow Pulse (Para lime green elements)
@keyframes glowPulse {
  0%, 100% {
    box-shadow: 0 0 20px rgba(132, 204, 22, 0.3);
  }
  50% {
    box-shadow: 0 0 40px rgba(132, 204, 22, 0.6);
  }
}

// Bounce (Para staggered reveals)
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
```

#### Staggered Animation (Cascata - MatchCards ✅)

Para efeito cascata ao carregar partidas, usar CSS `animation-delay`:

```typescript
// Stagger Pattern
.match-card {
  animation: slideUp duration-500 ease-out;
}

.match-card:nth-child(1) { animation-delay: 0ms; }
.match-card:nth-child(2) { animation-delay: 100ms; }
.match-card:nth-child(3) { animation-delay: 200ms; }
.match-card:nth-child(4) { animation-delay: 300ms; }
.match-card:nth-child(5) { animation-delay: 400ms; }
// ... etc

// Ou com Framer Motion (recomendado):
<Grid
  initial="hidden"
  animate="visible"
  variants={{
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,  // 100ms entre cards
      },
    },
  }}
>
  {partidas.map((p) => (
    <MatchCard
      key={p.id}
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 },
      }}
    />
  ))}
</Grid>
```

---

## Biblioteca de Componentes

### Organização (Atomic Design)

```
components/
├── atoms/          # Elementos básicos
├── molecules/      # Combinações simples
├── organisms/      # Componentes complexos
└── layout/         # Layout e containers
```

### ATOMS (Elementos Básicos - 6 componentes)

#### 1. Badge

Pequena tag para indicar status, CV, ou tipo.

```typescript
Props:
  - variant: 'cv' | 'status' | 'pick'
  - value: string
  - size?: 'sm' | 'md' | 'lg'
  - className?: string

Cores por Variant:
  cv:
    - "Muito Estável" → emerald-500
    - "Estável" → green-500
    - "Moderado" → yellow-500
    - "Instável" → orange-500
    - "Muito Instável" → red-500

  status:
    - Online → green-500
    - Offline → gray-500

  pick: (v2)
    - High confidence → emerald-500
    - Medium → amber-500
    - Low → red-500

Tamanhos:
  sm: px-2 py-1, text-xs
  md: px-3 py-1.5, text-sm (DEFAULT)
  lg: px-4 py-2, text-base
```

#### 2. RaceDot

Ponto colorido representando resultado (W/D/L) em forma recente.

```typescript
Props:
  - result: 'W' | 'D' | 'L'
  - tooltip?: string
  - size?: 'sm' | 'md' | 'lg'

Cores:
  W (Win): success-primary (#10b981)
  D (Draw): warning-primary (#f59e0b)
  L (Loss): danger-primary (#ef4444)

Tamanhos:
  sm: width-4 height-4 (16px)
  md: width-6 height-6 (24px) (DEFAULT)
  lg: width-8 height-8 (32px)

Hover Effect:
  - scale-110
  - shadow-md
```

#### 3. Button

Botão reutilizável com múltiplos variants.

```typescript
Props:
  - variant: 'primary' | 'secondary' | 'ghost'
  - size?: 'sm' | 'md' | 'lg'
  - icon?: ReactNode
  - loading?: boolean
  - disabled?: boolean
  - onClick?: () => void
  - children: ReactNode

Variants:
  primary:
    Background: lime-500
    Text: white
    Hover: lime-600
    Active: lime-700

  secondary:
    Background: bg-secondary
    Border: lime-500
    Text: lime-500
    Hover: bg-tertiary

  ghost:
    Background: transparent
    Text: text-secondary
    Hover: bg-secondary

Tamanhos:
  sm: px-3 py-1.5, text-sm, rounded
  md: px-4 py-2, text-base, rounded-md (DEFAULT)
  lg: px-6 py-3, text-lg, rounded-lg
```

#### 4. TeamBadge

Escudo do time (circular).

```typescript
Props:
  - src: string (URL da imagem)
  - alt: string (nome do time)
  - size?: 'sm' | 'md' | 'lg' | 'xl'
  - fallback?: string (iniciais do time se imagem falhar)

Tamanhos:
  sm: 32px × 32px
  md: 48px × 48px (DEFAULT)
  lg: 64px × 64px
  xl: 96px × 96px

Bordas:
  - rounded-full (círculo perfeito)
  - border-2 border-primary (Lime green)
  - shadow: shadow-md
```

#### 5. Icon

Wrapper para Material Icons Outlined.

```typescript
Props:
  - name: string (Material Icon name)
  - size?: 'sm' | 'md' | 'lg'
  - color?: string
  - className?: string

Tamanhos:
  sm: 16px
  md: 24px (DEFAULT)
  lg: 32px

Cores:
  - Padrão: text-primary
  - Hover: text-primary (sem mudança automática)
  - Error: danger-primary
  - Success: success-primary
```

#### 6. LoadingSpinner

Spinner de carregamento.

```typescript
Props:
  - size?: 'sm' | 'md' | 'lg'
  - color?: string
  - message?: string

Tamanhos:
  sm: 16px
  md: 24px (DEFAULT)
  lg: 48px

Animação:
  - Rotação contínua (360deg em 1s)
  - Cor: lime-500
  - Easing: linear
```

### MOLECULES (Combinações - 5 componentes)

#### 7. TeamCard

Card com informações do time.

```typescript
Props:
  - team: { id, nome, escudo }
  - stats?: { gols, escanteios }
  - recentForm?: ('W' | 'D' | 'L')[]

Composição:
  - TeamBadge (48px)
  - Texto: nome do time (font-semibold)
  - RaceRow (últimos 5 jogos)
  - Stats resumidas (opcional)

Layout:
  - Flex column, gap-3
  - padding: spacing-4
  - background: bg-secondary
  - rounded: rounded-lg
```

#### 8. StatMetric

Métrica com label, valor e CV badge.

```typescript
Props:
  - label: string
  - value: number
  - cv: number (0.0 - 1.0)
  - type: 'feitos' | 'sofridos'
  - showCVBadge?: boolean

Composição:
  - Label (text-xs, text-muted)
  - Value (font-mono, text-2xl, lime-500)
  - CV Badge (right side, conditional)

CV Classification:
  < 0.15: "Muito Estável" → emerald
  < 0.30: "Estável" → green
  < 0.45: "Moderado" → yellow
  < 0.60: "Instável" → orange
  >= 0.60: "Muito Instável" → red
```

#### 9. ComparisonBar

Barras horizontais comparando dois valores.

```typescript
Props:
  - homeValue: number
  - awayValue: number
  - maxValue?: number (para normalização)
  - label: string
  - showGradient?: boolean

Composição:
  - Label (centro, text-sm)
  - Barra Home (esquerda): lime-500
  - Barra Away (direita): lime-500
  - Gradientes (opcional): rgba(132, 204, 22, 0.6) → rgba(132, 204, 22, 0.3)
  - Glow effect (opcional): shadow-glow

Layout:
  - Flex row, items-center, gap-4
  - Home bar width: (homeValue / maxValue) * 100%
  - Away bar width: (awayValue / maxValue) * 100%
```

#### 10. FilterToggle

Botões para filtrar (Geral / 5M / 10M).

```typescript
Props:
  - options: { label, value }[]
  - selected: string
  - onChange: (value: string) => void

Composição:
  - Array de buttons (variant: 'primary' | 'secondary')
  - Selected: primary (lime-500)
  - Unselected: secondary (bg-secondary)

Opções Padrão:
  [
    { label: 'Geral', value: 'geral' },
    { label: 'Últimas 5', value: '5' },
    { label: 'Últimas 10', value: '10' }
  ]

Layout:
  - Flex row, gap-2
  - Flex wrap (responsive)
  - Justificado: space-between (md+)
```

### ORGANISMS (Componentes Complexos - 3 componentes)

#### 11. MatchCard

Card completo de partida (para grid na home).

```typescript
Props:
  - partida: PartidaResumo
  - onClick?: () => void

Composição:
  Header:
    - Competição badge (text-xs, text-muted)
    - Data + Horário (text-sm)

  Body:
    - TeamCard mandante (lado esquerdo)
    - "vs" center separator
    - TeamCard visitante (lado direito)

  Footer:
    - Estádio (text-xs, text-muted)
    - Botão "Ver Estatísticas" (variant: primary)

Estilo:
  - background: bg-secondary
  - rounded: rounded-lg
  - shadow: shadow-md (hover: shadow-lg)
  - border: 1px border transparent (hover: border-lime-500)
  - transition: all duration-300 ease-out
  - animation: slideUp (ao aparecer)

Hover Effects:
  - scale-102
  - shadow-lg
  - border-lime-500
  - glow effect (opcional)
```

#### 12. StatsPanel

Painel principal de estatísticas (3 colunas).

```typescript
Props:
  - partida: PartidaResumo
  - stats: StatsResponse
  - filtro: 'geral' | '5' | '10'
  - onFiltroChange: (filtro: string) => void

Composição:
  Header:
    - FilterToggle (topo)

  Body (Grid 3 colunas):
    Coluna Esquerda (Mandante):
      - TeamCard com escudo grande
      - Stats detalhadas

    Coluna Centro (Info):
      - Data, horário, competição
      - Estádio
      - Árbitro (futuro)

    Coluna Direita (Visitante):
      - TeamCard com escudo grande
      - Stats detalhadas

  Stats Categories:
    - StatsCategory × N (Escanteios, Gols, Finalizações, Cartões)

Responsive:
  - lg+: 3 colunas
  - md: 2 colunas (mandante + visitante stacked)
  - sm: 1 coluna (stack total)
```

#### 13. StatsCategory

Seção de uma categoria de estatística.

```typescript
Props:
  - title: string ('Escanteios', 'Gols', etc)
  - icon: ReactNode
  - homeStat: { feitos, sofridos }
  - awayStat: { feitos, sofridos }

Composição:
  Header:
    - Icon (lg)
    - Título (h4, font-semibold)

  Body:
    ComparisonBar (Feitos):
      - Home value
      - Away value
      - Gradientes + glow

    ComparisonBar (Sofridos):
      - Home value
      - Away value

    CV Badges (opcional):
      - CV do home team
      - CV do away team

Categorias Principais:
  - Escanteios: sports_soccer icon
  - Gols: emoji_events icon
  - Finalizações: trending_up icon
  - Cartões: style icon
```

---

## Implementação no Tailwind

### tailwind.config.js (Exemplo)

```typescript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0fdf4',
          500: '#84cc16',  // LIME (Decisão do Usuário)
          600: '#65a30d',
          700: '#4d7c0f',
        },
        lime: {
          50: '#f7fee7',
          500: '#84cc16',   // ⭐ Lime Primary
          600: '#65a30d',
          700: '#4d7c0f',
        },
        success: {
          primary: '#10b981',  // Win (W)
          hover: '#059669',
          dark: '#047857',
        },
        warning: {
          primary: '#f59e0b',  // Draw (D)
          hover: '#d97706',
          dark: '#b45309',
        },
        danger: {
          primary: '#ef4444',  // Loss (L)
          hover: '#dc2626',
          dark: '#b91c1c',
        },
      },
      backgroundColor: {
        'dark-primary': '#0a0a0a',
        'dark-secondary': '#171717',
        'dark-tertiary': '#262626',
        'dark-quaternary': '#404040',
      },
      fontFamily: {
        display: ['Outfit', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['Space Mono', 'monospace'],
      },
      boxShadow: {
        'glow': '0 0 20px rgba(132, 204, 22, 0.3)',
        'glow-lg': '0 0 40px rgba(132, 204, 22, 0.4)',
      },
      animation: {
        'fade-in': 'fadeIn 300ms ease-out',
        'slide-up': 'slideUp 500ms ease-out',
        'scale-up': 'scaleUp 300ms ease-out',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        scaleUp: {
          from: { opacity: '0', transform: 'scale(0.95)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(132, 204, 22, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(132, 204, 22, 0.6)' },
        },
      },
    },
  },
  plugins: [],
  darkMode: 'class',  // Dark mode sempre ativo (tema padrão)
}
```

---

## Guia de Uso

### Estrutura de Pastas Recomendada

```
src/
├── components/
│   ├── atoms/
│   │   ├── Badge.tsx
│   │   ├── RaceDot.tsx
│   │   ├── Button.tsx
│   │   ├── TeamBadge.tsx
│   │   ├── Icon.tsx
│   │   └── LoadingSpinner.tsx
│   │
│   ├── molecules/
│   │   ├── TeamCard.tsx
│   │   ├── StatMetric.tsx
│   │   ├── ComparisonBar.tsx
│   │   ├── FilterToggle.tsx
│   │   └── RaceRow.tsx
│   │
│   ├── organisms/
│   │   ├── MatchCard.tsx
│   │   ├── StatsPanel.tsx
│   │   └── StatsCategory.tsx
│   │
│   └── layout/
│       ├── PageLayout.tsx
│       ├── Container.tsx
│       └── Grid.tsx
│
└── styles/
    ├── globals.css        # Design tokens CSS
    ├── animations.css     # Animações customizadas
    └── tailwind.css       # Tailwind imports
```

### Padrões de Nomenclatura

**Componentes:**
- Use PascalCase: `Badge.tsx`, `MatchCard.tsx`
- Props interface: `interface BadgeProps {}`
- Componentes: `export const Badge: React.FC<BadgeProps> = (props) => {}`

**Classes CSS:**
- Use Tailwind por padrão
- Classes customizadas em `components/styles.ts`
- Nomeie com prefix do componente: `.badge-cv`, `.match-card-hover`

**Cores:**
- Sempre use tokens: `className="text-lime-500"` (not hardcoded `#84cc16`)
- Permita props para cores: `<Badge variant="cv" />` (não `color="#84cc16"`)

---

## Ver Também

Para entender melhor este documento e o contexto do projeto, consulte:

- **[COMPONENTES_REACT.md](COMPONENTES_REACT.md)** - Catálogo detalhado de todos os 19 componentes com props e exemplos
- **[ARQUITETURA_FRONTEND.md](ARQUITETURA_FRONTEND.md)** - Folder structure e organização do projeto React
- **[INTEGRACAO_API.md](INTEGRACAO_API.md)** - Services e hooks para integração com API backend
- **[RESPONSIVIDADE_E_ACESSIBILIDADE.md](RESPONSIVIDADE_E_ACESSIBILIDADE.md)** - Breakpoints, WCAG AA, PWA setup
- **[../MODELOS_DE_DADOS.md](../MODELOS_DE_DADOS.md)** - Schemas Pydantic que definem dados a exibir
- **[../API_SPECIFICATION.md](../API_SPECIFICATION.md)** - Endpoints da API que serão integrados
- **[../ARQUITETURA_BACKEND.md](../ARQUITETURA_BACKEND.md)** - Arquitetura backend (contexto complementar)

**Próximos Passos Recomendados:**
1. Implemente os **6 componentes atoms** (mais básicos)
2. Configure **tailwind.config.js** com todos os tokens deste design system
3. Implemente os **5 componentes molecules** (dependem dos atoms)
4. Crie os **3 componentes organisms** (dependem dos molecules)
5. Consulte **COMPONENTES_REACT.md** para prop signatures e exemplos de uso

---

## Notas de Implementação

- **Dark mode é o tema padrão** - Não implementar toggle (decisão do usuário ✅)
- **Cor primária Lime #84cc16** foi escolhida pela excelente legibilidade (~8.5:1 contrast WCAG AAA ✅)
- **Staggered animations** são críticas para UX quando carregar partidas (100-200ms delays recomendados)
- **Todos os componentes devem suportar dark mode** (já que é padrão)
- **Tipografia Outfit/Space Mono** já está carregada no `frontend/index.html` (Inter é fallback opcional)
- **Material Icons Outlined** - usar `@mui/icons-material` ou import CDN

---

**[⬆ Voltar ao topo](#design-system---sistema-de-análise-de-estatísticas-de-futebol)**
