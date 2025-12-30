# Componentes React - Catálogo Atomic Design

**Versão:** 1.6
**Data:** 28 de dezembro de 2025
**Pattern:** Atomic Design (Atoms → Molecules → Organisms → Pages)
**Total de Componentes:** 26 (v1.5 - inclui StatFilter interno)

Catálogo completo de componentes React + TypeScript para implementação do frontend.

---

## 📋 Índice

1. [ATOMS (6)](#atoms---6-componentes)
2. [MOLECULES (7)](#molecules---7-componentes) *(+1 novo: OpportunityCard)*
3. [ORGANISMS (7)](#organisms---7-componentes) *(+1 novo: SmartSearchResults)*
4. [LAYOUT (3)](#layout---3-componentes)
5. [PAGES (2)](#pages---2-páginas-v1)
6. [Padrões de Implementação](#padrões-de-implementação)
7. [Ver Também](#ver-também)

---

## ATOMS - 6 Componentes

### 1. Badge

Badge semântico para indicar níveis de estabilidade, confiança ou probabilidade.

```typescript
// src/components/atoms/Badge.tsx

import type { EstabilidadeLabel } from '@/types/stats';

interface BadgeProps {
  estabilidade: EstabilidadeLabel;  // 'Alta' | 'Média' | 'Baixa' | 'N/A'
  size?: 'sm' | 'md';
  label?: string;  // Prefixo opcional: "Estabilidade", "Confiança", "Probabilidade"
}

// Cores por nível de estabilidade
const badgeStyles: Record<EstabilidadeLabel, string> = {
  Alta: 'bg-cv-muitoEstavel/20 text-cv-muitoEstavel',      // Verde
  Média: 'bg-cv-moderado/20 text-cv-moderado',              // Amarelo
  Baixa: 'bg-danger/20 text-danger',                        // Vermelho
  'N/A': 'bg-gray-500/20 text-gray-400',
};

export function Badge({ estabilidade, size = 'sm', label }: BadgeProps) {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClasses} ${badgeStyles[estabilidade]}`}
    >
      {label ? `${label} ${estabilidade}` : estabilidade}
    </span>
  );
}

// Exemplos de Uso:
// <Badge estabilidade="Alta" />                        → "Alta"
// <Badge estabilidade="Alta" label="Estabilidade" />   → "Estabilidade Alta"
// <Badge estabilidade="Baixa" label="Confiança" />     → "Confiança Baixa"
// <Badge estabilidade="Média" label="Probabilidade" /> → "Probabilidade Média"
```

**Props:**
- `estabilidade`: Nível ('Alta' | 'Média' | 'Baixa' | 'N/A')
- `size`: Tamanho do badge ('sm' | 'md')
- `label`: Prefixo semântico opcional - quando fornecido, exibe "Label Nível" (ex: "Estabilidade Alta")

**Uso por Contexto:**
- **StatsCard**: `label="Estabilidade"` → "Estabilidade Alta/Média/Baixa"
- **OverUnderCard**: `label="Confiança"` → "Confiança Alta/Média/Baixa"
- **PredictionsCard**: `label="Probabilidade"` → "Probabilidade Alta/Média/Baixa"
- **DisciplineCard**: `label="Estabilidade"` → "Estabilidade Alta/Média/Baixa"

---

### 2. RaceDot

Ponto colorido representando resultado recente (W/D/L).

```typescript
// src/components/atoms/RaceDot.tsx

interface RaceDotProps {
  result: 'W' | 'D' | 'L';
  tooltip?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const RaceDot: React.FC<RaceDotProps> = ({
  result,
  tooltip,
  size = 'md',
}) => {
  const getColor = () => {
    switch (result) {
      case 'W':
        return 'bg-emerald-500';  // Win
      case 'D':
        return 'bg-amber-500';    // Draw
      case 'L':
        return 'bg-red-500';      // Loss
    }
  };

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div
      className={`
        rounded-full ${getColor()} ${sizeClasses[size]}
        hover:scale-110 transition-transform duration-150
        cursor-pointer shadow hover:shadow-md
      `}
      title={tooltip}
    />
  );
};

// Exemplo de Uso:
// <RaceDot result="W" tooltip="3-1 vs Arsenal" size="md" />
```

**Props:**
- `result`: 'W' (Win), 'D' (Draw), ou 'L' (Loss)
- `tooltip`: Texto ao passar mouse
- `size`: Tamanho (sm/md/lg)

---

### 3. Button

Botão reutilizável com múltiplos variants.

```typescript
// src/components/atoms/Button.tsx

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  loading?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  icon,
  loading = false,
  disabled = false,
  className = '',
  children,
  ...props
}) => {
  const variantClasses = {
    primary: 'bg-lime-500 text-white hover:bg-lime-600 active:bg-lime-700',
    secondary: 'bg-dark-secondary border border-lime-500 text-lime-500 hover:bg-dark-tertiary',
    ghost: 'bg-transparent text-text-secondary hover:bg-dark-secondary',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm rounded',
    md: 'px-4 py-2 text-base rounded-md',
    lg: 'px-6 py-3 text-lg rounded-lg',
  };

  return (
    <button
      className={`
        inline-flex items-center gap-2 font-medium
        transition-all duration-200 ease-out
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <LoadingSpinner size="sm" /> : icon}
      {children}
    </button>
  );
};

// Exemplo de Uso:
// <Button variant="primary" size="md" icon={<FilterIcon />}>
//   Filtrar
// </Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'ghost'
- `size`: 'sm' | 'md' | 'lg'
- `icon`: ReactNode (ícone à esquerda)
- `loading`: Boolean (mostra spinner)
- `disabled`: Boolean
- Todas as props HTML standard de button

---

### 4. TeamBadge

Escudo do time (circular).

```typescript
// src/components/atoms/TeamBadge.tsx

interface TeamBadgeProps {
  src: string;
  alt: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  fallback?: string;  // Iniciais do time
}

export const TeamBadge: React.FC<TeamBadgeProps> = ({
  src,
  alt,
  size = 'md',
  fallback,
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24',
  };

  const [imageFailed, setImageFailed] = React.useState(false);

  if (imageFailed && fallback) {
    return (
      <div
        className={`
          ${sizeClasses[size]}
          rounded-full bg-lime-500 text-dark-primary
          flex items-center justify-center font-bold
          border-2 border-lime-500
        `}
      >
        {fallback}
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      className={`
        ${sizeClasses[size]}
        rounded-full border-2 border-lime-500
        shadow-md object-cover
      `}
      onError={() => setImageFailed(true)}
    />
  );
};

// Exemplo de Uso:
// <TeamBadge src={team.escudo} alt={team.nome} size="lg" fallback="MAN" />
```

**Props:**
- `src`: URL da imagem do escudo
- `alt`: Texto alternativo
- `size`: 'sm' (32px) | 'md' (48px) | 'lg' (64px) | 'xl' (96px)
- `fallback`: Iniciais do time se imagem falhar

---

### 5. Icon

Wrapper para Material Icons Outlined.

```typescript
// src/components/atoms/Icon.tsx

interface IconProps {
  name: string;  // Material Icon name
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  className?: string;
}

export const Icon: React.FC<IconProps> = ({
  name,
  size = 'md',
  color = 'text-text-primary',
  className = '',
}) => {
  const sizeClasses = {
    sm: 'text-base',
    md: 'text-2xl',
    lg: 'text-4xl',
  };

  return (
    <span className={`material-icons-outlined ${sizeClasses[size]} ${color} ${className}`}>
      {name}
    </span>
  );
};

// Exemplo de Uso:
// <Icon name="sports_soccer" size="md" color="text-lime-500" />
// <Icon name="filter_list" />
```

**Props:**
- `name`: Material Icon name (ex: 'sports_soccer', 'filter_list')
- `size`: 'sm' | 'md' | 'lg'
- `color`: Classe Tailwind de cor
- `className`: Classes adicionais

**Material Icons a Usar:**
- `sports_soccer` - Para escanteios, partidas
- `trending_up` - Para finalizações, stats
- `filter_list` - Para filtros
- `arrow_back` - Para voltar
- `arrow_forward` - Para próximo
- `search` - Para busca
- `style` - Para cartões
- `more_vert` - Para menu

---

### 6. LoadingSpinner

Spinner de carregamento.

```typescript
// src/components/atoms/LoadingSpinner.tsx

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'border-lime-500',
  message,
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className={`
          rounded-full border-t-transparent
          ${color} ${sizeClasses[size]}
          animate-spin
        `}
      />
      {message && <p className="text-xs text-text-muted">{message}</p>}
    </div>
  );
};

// Exemplo de Uso:
// <LoadingSpinner size="md" message="Carregando partidas..." />
```

**Props:**
- `size`: 'sm' | 'md' | 'lg'
- `color`: Cor Tailwind (ex: 'border-lime-500')
- `message`: Mensagem opcional

---

## MOLECULES - 7 Componentes

### 7. TeamCard

Card com informações do time.

```typescript
// src/components/molecules/TeamCard.tsx

interface TeamCardProps {
  team: {
    id: string;
    nome: string;
    escudo: string;
  };
  stats?: {
    gols: number;
    escanteios: number;
  };
  recentForm?: ('W' | 'D' | 'L')[];
  size?: 'sm' | 'md';
}

export const TeamCard: React.FC<TeamCardProps> = ({
  team,
  stats,
  recentForm,
  size = 'md',
}) => {
  return (
    <div className="flex flex-col items-center gap-3 p-4 bg-dark-secondary rounded-lg">
      <TeamBadge src={team.escudo} alt={team.nome} size={size === 'md' ? 'lg' : 'md'} />
      <h3 className="font-semibold text-center text-text-primary">{team.nome}</h3>

      {recentForm && <RaceRow results={recentForm} maxResults={5} />}

      {stats && (
        <div className="flex gap-4 text-sm">
          <div className="text-center">
            <p className="text-text-muted text-xs">Gols</p>
            <p className="font-mono font-bold text-lime-500">{stats.gols}</p>
          </div>
          <div className="text-center">
            <p className="text-text-muted text-xs">Escanteios</p>
            <p className="font-mono font-bold text-lime-500">{stats.escanteios}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Exemplo de Uso:
// <TeamCard
//   team={mandante}
//   recentForm={['W', 'W', 'D', 'L', 'W']}
//   stats={{ gols: 2.1, escanteios: 5.3 }}
// />
```

**Props:**
- `team`: { id, nome, escudo }
- `stats`: { gols, escanteios }
- `recentForm`: Array de resultados recentes
- `size`: 'sm' | 'md'

---

### 8. StatMetric

Componente de comparação de estatísticas entre mandante e visitante.

```typescript
// src/components/molecules/StatMetric.tsx

import { Badge } from '@/components/atoms';
import type { EstatisticaMetrica } from '@/types';

interface StatMetricProps {
  label: string;
  home: EstatisticaMetrica;
  away: EstatisticaMetrica;
  showCV?: boolean;
}

export function StatMetric({ label, home, away, showCV = true }: StatMetricProps) {
  const total = home.media + away.media;
  const percentHome = total > 0 ? (home.media / total) * 100 : 50;
  const percentAway = total > 0 ? (away.media / total) * 100 : 50;

  return (
    <div className="py-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-white font-semibold text-lg">{home.media.toFixed(1)}</span>
          {showCV && <Badge classificacao={home.classificacao} size="sm" />}
        </div>
        <span className="text-gray-400 text-sm font-medium uppercase tracking-wider">
          {label}
        </span>
        <div className="flex items-center gap-2">
          {showCV && <Badge classificacao={away.classificacao} size="sm" />}
          <span className="text-white font-semibold text-lg">{away.media.toFixed(1)}</span>
        </div>
      </div>
      {/* Comparison Bar */}
      <div className="h-2 bg-dark-tertiary rounded-full overflow-hidden flex">
        <div className="bg-primary-500 transition-all duration-500" style={{ width: `${percentHome}%` }} />
        <div className="bg-gray-600 transition-all duration-500" style={{ width: `${percentAway}%` }} />
      </div>
      {/* CV Values */}
      {showCV && (
        <div className="flex justify-between mt-1 text-xs text-gray-500">
          <span>CV: {(home.cv * 100).toFixed(0)}%</span>
          <span>CV: {(away.cv * 100).toFixed(0)}%</span>
        </div>
      )}
    </div>
  );
}

// Exemplo de Uso:
// <StatMetric
//   label="Gols Feitos"
//   home={mandante.estatisticas.gols.feitos}
//   away={visitante.estatisticas.gols.feitos}
//   showCV
// />
```

**Props:**
- `label`: Descrição da métrica (ex: "Gols Feitos", "Escanteios Sofridos")
- `home`: EstatisticaMetrica do mandante { media, cv, classificacao }
- `away`: EstatisticaMetrica do visitante { media, cv, classificacao }
- `showCV`: Mostrar badges de classificação CV (default: true)

---

### 9. ComparisonBar

Barra horizontal de comparação entre dois valores (mandante vs visitante).

```typescript
// src/components/molecules/ComparisonBar.tsx

interface ComparisonBarProps {
  home: number;
  away: number;
  label?: string;
  showValues?: boolean;
  height?: 'sm' | 'md';
}

export function ComparisonBar({
  home,
  away,
  label,
  showValues = true,
  height = 'sm',
}: ComparisonBarProps) {
  const total = home + away;
  const percentHome = total > 0 ? (home / total) * 100 : 50;
  const percentAway = total > 0 ? (away / total) * 100 : 50;
  const heightClass = height === 'sm' ? 'h-1.5' : 'h-2.5';

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-1">
          {showValues && <span className="text-white font-medium text-sm">{home}</span>}
          <span className="text-gray-400 text-xs uppercase tracking-wider flex-1 text-center">
            {label}
          </span>
          {showValues && <span className="text-white font-medium text-sm">{away}</span>}
        </div>
      )}
      <div className={`${heightClass} bg-dark-quaternary rounded-full overflow-hidden flex`}>
        <div className="bg-primary-500 rounded-l-full transition-all duration-500" style={{ width: `${percentHome}%` }} />
        <div className="bg-gray-500 rounded-r-full transition-all duration-500" style={{ width: `${percentAway}%` }} />
      </div>
    </div>
  );
}

// Exemplo de Uso:
// <ComparisonBar
//   home={5.2}
//   away={4.8}
//   label="Escanteios"
//   height="md"
// />
```

**Props:**
- `home`: Valor do time mandante
- `away`: Valor do time visitante
- `label`: Descrição (opcional)
- `showValues`: Mostrar valores numéricos (default: true)
- `height`: Altura da barra 'sm' | 'md'

---

### 10. FilterToggle

Botões para filtrar (Geral / 5M / 10M).

```typescript
// src/components/molecules/FilterToggle.tsx

interface FilterToggleProps {
  options: { label: string; value: string }[];
  selected: string;
  onChange: (value: string) => void;
  fullWidth?: boolean;
}

export const FilterToggle: React.FC<FilterToggleProps> = ({
  options,
  selected,
  onChange,
  fullWidth = false,
}) => {
  return (
    <div className={`flex gap-2 flex-wrap ${fullWidth ? 'w-full justify-between' : ''}`}>
      {options.map((option) => (
        <Button
          key={option.value}
          variant={selected === option.value ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => onChange(option.value)}
        >
          {option.label}
        </Button>
      ))}
    </div>
  );
};

// Exemplo de Uso:
// const filterOptions = [
//   { label: 'Geral', value: 'geral' },
//   { label: 'Últimas 5', value: '5' },
//   { label: 'Últimas 10', value: '10' }
// ];
// <FilterToggle
//   options={filterOptions}
//   selected={filtro}
//   onChange={setFiltro}
// />
```

**Props:**
- `options`: Array de { label, value }
- `selected`: Valor selecionado
- `onChange`: Callback ao mudar
- `fullWidth`: Expande para toda largura

---

### 11. RaceRow

Sequência de race dots.

```typescript
// src/components/molecules/RaceRow.tsx

interface RaceRowProps {
  results: ('W' | 'D' | 'L')[];
  tooltips?: string[];
  maxResults?: number;
}

export const RaceRow: React.FC<RaceRowProps> = ({
  results,
  tooltips = [],
  maxResults = 5,
}) => {
  // Pegar últimos N resultados
  const displayResults = results.slice(-maxResults).reverse();

  return (
    <div className="flex gap-1 items-center justify-center">
      {displayResults.map((result, idx) => (
        <RaceDot
          key={idx}
          result={result}
          tooltip={tooltips[idx]}
          size="md"
        />
      ))}
    </div>
  );
};

// Exemplo de Uso:
// <RaceRow
//   results={['W', 'D', 'W', 'L', 'W', 'W', 'D']}
//   tooltips={['3-1 vs Arsenal', '0-0 vs Chelsea', ...]}
//   maxResults={5}
// />
```

**Props:**
- `results`: Array de 'W' | 'D' | 'L'
- `tooltips`: Array de descrições
- `maxResults`: Número máximo de dots a mostrar

---

### 12. PeriodoToggle (v1.3)

Toggle para selecionar período do jogo (Integral/1T/2T).

```typescript
// src/components/molecules/PeriodoToggle.tsx

import type { PeriodoFilter } from '@/types';

interface PeriodoToggleProps {
  value: PeriodoFilter;
  onChange: (value: PeriodoFilter) => void;
}

const options: { value: PeriodoFilter; label: string }[] = [
  { value: 'integral', label: 'Integral' },
  { value: '1T', label: '1T' },
  { value: '2T', label: '2T' },
];

export function PeriodoToggle({ value, onChange }: PeriodoToggleProps) {
  return (
    <div className="inline-flex bg-dark-tertiary rounded-lg p-1 gap-1">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`
            px-4 py-2 rounded-md text-sm font-medium transition-all duration-200
            ${
              value === option.value
                ? 'bg-info text-dark-primary shadow-glow'
                : 'text-gray-400 hover:text-white hover:bg-dark-quaternary'
            }
          `}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

// Exemplo de Uso:
// <PeriodoToggle value={periodo} onChange={setPeriodo} />
// Integração com useFilterStore:
// const { periodo, setPeriodo } = useFilterStore();
```

**Props:**
- `value`: Período selecionado (`'integral'` | `'1T'` | `'2T'`)
- `onChange`: Callback ao mudar seleção

**Uso no Sistema de Filtros:**
Este componente faz parte do sistema de 3 filtros:
1. **FilterToggle**: Filtro principal (Temporada/Últimos 5/Últimos 10)
2. **PeriodoToggle**: Sub-filtro de período (Integral/1T/2T)
3. **MandoToggle**: Sub-filtro casa/fora (por time)

**Casos de Uso para Apostas:**
- Over/Under 0.5 gols no 1T
- Time marca mais no 2T em casa?
- Comparar 1T vs 2T para padrões

---

### 13. OpportunityCard (v1.5)

Card de oportunidade de aposta identificada pela Busca Inteligente. Usa `<Link>` do React Router para navegação semântica, permitindo abrir em nova aba com botão direito.

**Otimização v1.5:** Componente memoizado com `React.memo` para evitar re-renders desnecessários.

```typescript
// src/components/molecules/OpportunityCard.tsx

import { memo } from 'react';
import { Link } from 'react-router-dom';
import { Icon, TeamBadge, type IconName } from '@/components/atoms';
import type { Oportunidade } from '@/types';
import { formatarProbabilidade, getScoreColor, getTipoBgColor } from '@/utils/smartSearch';

interface OpportunityCardProps {
  oportunidade: Oportunidade;
  rank?: number;  // Posição no ranking (opcional)
}

// Mapeamento de estatísticas para ícones
const STAT_ICONS: Record<string, IconName> = {
  gols: 'goal',
  escanteios: 'corner',
  finalizacoes: 'shot',
  finalizacoes_gol: 'target',
  cartoes_amarelos: 'card',
  faltas: 'foul',
};

export const OpportunityCard = memo(function OpportunityCard({ oportunidade, rank }: OpportunityCardProps) {
  const {
    matchId,
    mandante,
    visitante,
    competicao,
    horario,
    estatistica,
    estatisticaLabel,
    tipo,
    linha,
    probabilidade,
    confiancaLabel,
    score,
  } = oportunidade;

  return (
    <Link
      to={`/partida/${matchId}`}
      className="block bg-dark-secondary rounded-xl p-4 border border-dark-tertiary hover:border-primary-500/50 transition-all cursor-pointer"
    >
      {/* Header: Times + Horário */}
      {/* Body: Estatística + Tipo (over/under) + Linha */}
      {/* Footer: Probabilidade + Confiança + Score bar */}
    </Link>
  );
});

// Exemplo de Uso:
// <OpportunityCard oportunidade={op} rank={1} />
// Clique esquerdo: navega para /partida/{matchId}
// Clique direito: abre menu com opção "Abrir em nova aba"
```

**Props:**
- `oportunidade`: Objeto `Oportunidade` com todos os dados da aposta identificada
- `rank`: Posição opcional no ranking (exibe badge numérico)

**Layout:**
- **Header:** Escudos dos times, nomes truncados, horário
- **Competição:** Nome da competição
- **Oportunidade:** Ícone da estatística + label + badge Over/Under + linha
- **Métricas:** Probabilidade (%) + Confiança (Alta/Média/Baixa) + Score bar

**Cores por Tipo:**
- **Over:** `bg-success/20 text-success` (verde)
- **Under:** `bg-info/20 text-info` (azul)

**Cores de Confiança:**
- **Alta:** `text-success` (verde)
- **Média:** `text-warning` (amarelo)
- **Baixa:** `text-danger` (vermelho)

**Navegação (v1.5):**
- Usa `<Link to={...}>` ao invés de `<div onClick={...}>`
- **Clique esquerdo:** Navega para `/partida/{matchId}`
- **Clique direito → "Abrir em nova aba":** Abre a partida em nova aba
- **Ctrl+Click / Cmd+Click:** Abre em nova aba (comportamento nativo do browser)

---

## ORGANISMS - 7 Componentes

### 14. MatchCard

Card completo de partida para grid.

```typescript
// src/components/organisms/MatchCard.tsx

interface MatchCardProps {
  partida: PartidaResumo;
  onClick?: () => void;
  animated?: boolean;
}

export const MatchCard: React.FC<MatchCardProps> = ({
  partida,
  onClick,
  animated = true,
}) => {
  return (
    <div
      onClick={onClick}
      className={`
        bg-dark-secondary rounded-lg shadow-md
        hover:shadow-lg hover:border-lime-500
        border border-transparent
        p-4 cursor-pointer
        transition-all duration-300 ease-out
        hover:scale-102
        ${animated ? 'animate-slide-up' : ''}
      `}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-3 pb-3 border-b border-dark-tertiary">
        <div>
          <p className="text-xs text-text-muted font-medium">
            {partida.competicao}
          </p>
          <p className="text-sm font-semibold text-text-primary">
            {partida.data} • {partida.horario}
          </p>
        </div>
      </div>

      {/* Body - Match Info */}
      <div className="flex items-center justify-between gap-2 mb-4">
        <div className="flex-1">
          <TeamCard team={partida.mandante} size="sm" />
        </div>

        <div className="text-center font-semibold text-text-secondary">
          vs
        </div>

        <div className="flex-1">
          <TeamCard team={partida.visitante} size="sm" />
        </div>
      </div>

      {/* Footer */}
      <div className="flex justify-between items-center pt-3 border-t border-dark-tertiary">
        <p className="text-xs text-text-muted">
          🏟️ {partida.estadio}
        </p>
        <Button
          variant="primary"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onClick?.();
          }}
        >
          Ver Estatísticas
        </Button>
      </div>
    </div>
  );
};

// Exemplo de Uso:
// <MatchCard
//   partida={partida}
//   onClick={() => navigate(`/partida/${partida.id}`)}
//   animated
// />
```

**Props:**
- `partida`: PartidaResumo (da API)
- `onClick`: Callback ao clicar
- `animated`: Mostrar animação slide-up

---

### 15. StatsPanel

Painel de estatísticas comparando mandante e visitante.

**Otimização v1.5:** Usa `useMemo` para memoizar cálculos de `calcularPrevisoes()` e `calcularOverUnder()`, evitando recálculos desnecessários em re-renders.

```typescript
// src/components/organisms/StatsPanel.tsx

import { StatMetric } from '@/components/molecules';
import { LoadingSpinner, TeamBadge, Icon } from '@/components/atoms';
import type { StatsResponse, EstatisticaFeitos } from '@/types';

interface StatsPanelProps {
  stats: StatsResponse | undefined;
  isLoading: boolean;
  error: Error | null;
}

export function StatsPanel({ stats, isLoading, error }: StatsPanelProps) {
  if (isLoading) return <LoadingSpinner size="lg" />;
  if (error) return <p className="text-danger">Erro: {error.message}</p>;
  if (!stats) return <p className="text-gray-500">Nenhuma estatística</p>;

  const { mandante, visitante, filtro_aplicado, partidas_analisadas } = stats;

  return (
    <div className="card">
      {/* Team Headers */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-dark-tertiary">
        <div className="flex items-center gap-3">
          <TeamBadge src={mandante.escudo ?? undefined} alt={mandante.nome} size="md" />
          <div>
            <p className="font-semibold text-white">{mandante.nome}</p>
            <p className="text-xs text-gray-500">Mandante</p>
          </div>
        </div>

        <div className="text-center">
          <span className="text-xs text-gray-500 uppercase tracking-wider">
            {filtro_aplicado === 'geral' ? 'Temporada' : `Últimos ${filtro_aplicado}`}
          </span>
          <p className="text-xs text-gray-600 mt-1">{partidas_analisadas} jogos analisados</p>
        </div>

        <div className="flex items-center gap-3 flex-row-reverse">
          <TeamBadge src={visitante.escudo ?? undefined} alt={visitante.nome} size="md" />
          <div className="text-right">
            <p className="font-semibold text-white">{visitante.nome}</p>
            <p className="text-xs text-gray-500">Visitante</p>
          </div>
        </div>
      </div>

      {/* Stats Categories */}
      <div className="divide-y divide-dark-tertiary">
        <StatsCategory title="Gols" icon="goal"
          homeFeitos={mandante.estatisticas.gols} awayFeitos={visitante.estatisticas.gols} />
        <StatsCategory title="Escanteios" icon="corner"
          homeFeitos={mandante.estatisticas.escanteios} awayFeitos={visitante.estatisticas.escanteios} />
        <StatsCategory title="Finalizações" icon="shot"
          homeFeitos={mandante.estatisticas.finalizacoes} awayFeitos={visitante.estatisticas.finalizacoes} />
        <StatsCategory title="Finalizações no Gol" icon="target"
          homeFeitos={mandante.estatisticas.finalizacoes_gol} awayFeitos={visitante.estatisticas.finalizacoes_gol} />

        {/* Disciplina - Simple Metrics */}
        <div className="pt-4">
          <div className="flex items-center gap-2 mb-3">
            <Icon name="card" size="sm" className="text-primary-400" />
            <h3 className="text-sm font-medium text-gray-400 uppercase">Disciplina</h3>
          </div>
          <div className="space-y-1">
            <StatMetric label="Cartões Amarelos"
              home={mandante.estatisticas.cartoes_amarelos} away={visitante.estatisticas.cartoes_amarelos} />
            <StatMetric label="Cartões Vermelhos"
              home={mandante.estatisticas.cartoes_vermelhos} away={visitante.estatisticas.cartoes_vermelhos} />
            <StatMetric label="Faltas"
              home={mandante.estatisticas.faltas} away={visitante.estatisticas.faltas} />
          </div>
        </div>
      </div>
    </div>
  );
}

// Exemplo de Uso:
// <StatsPanel stats={stats} isLoading={isLoading} error={error} />
```

---

### 16. StatsCategory

Seção de uma categoria de estatística com feitos/sofridos.

```typescript
// src/components/organisms/StatsCategory.tsx

import { Icon } from '@/components/atoms';
import { ComparisonBar } from '@/components/molecules';
import type { EstatisticaFeitos } from '@/types';

interface StatsCategoryProps {
  title: string;
  icon: string;
  homeStats: EstatisticaFeitos;
  awayStats: EstatisticaFeitos;
}

export function StatsCategory({ title, icon, homeStats, awayStats }: StatsCategoryProps) {
  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-dark-tertiary">
        <Icon name={icon} size="md" className="text-primary-400" />
        <h3 className="font-semibold text-white">{title}</h3>
      </div>

      {/* Stats List */}
      <div className="space-y-4">
        <ComparisonBar
          home={homeStats.feitos.media}
          away={awayStats.feitos.media}
          label="Feitos"
          height="md"
        />
        <ComparisonBar
          home={homeStats.sofridos.media}
          away={awayStats.sofridos.media}
          label="Sofridos"
          height="md"
        />
      </div>
    </div>
  );
}

// Exemplo de Uso:
// <StatsCategory
//   title="Escanteios"
//   icon="corner"
//   homeStats={mandante.estatisticas.escanteios}
//   awayStats={visitante.estatisticas.escanteios}
// />
```

**Props:**
- `title`: Nome da categoria (ex: "Gols", "Escanteios")
- `icon`: Nome do ícone
- `homeStats`: EstatisticaFeitos do mandante { feitos, sofridos }
- `awayStats`: EstatisticaFeitos do visitante { feitos, sofridos }

---

### 17. RaceBadges (v1.1)

Badges de sequência de resultados (V/E/D) para exibir forma recente dos times.

```typescript
// src/components/organisms/StatsPanel.tsx (componente interno)

type FormResult = 'W' | 'D' | 'L';

interface RaceBadgesProps {
  results?: FormResult[];
  limit?: number;  // Máximo de badges a exibir
}

function RaceBadges({ results, limit }: RaceBadgesProps) {
  if (!results?.length) return null;

  const colors: Record<FormResult, string> = {
    W: 'bg-success',   // Verde - Vitória
    D: 'bg-warning',   // Amarelo - Empate
    L: 'bg-danger',    // Vermelho - Derrota
  };

  const labels: Record<FormResult, string> = {
    W: 'V',  // Vitória
    D: 'E',  // Empate
    L: 'D',  // Derrota
  };

  // Aplica limite se especificado
  const displayResults = limit ? results.slice(0, limit) : results;

  return (
    <div className="flex gap-0.5 mt-1">
      {displayResults.map((r, i) => (
        <span
          key={i}
          className={`${colors[r]} text-[10px] font-bold text-white px-1.5 py-0.5 rounded`}
        >
          {labels[r]}
        </span>
      ))}
    </div>
  );
}

// Exemplo de Uso:
// <RaceBadges results={mandante.recent_form} limit={5} />
// Renderiza: V V E D V (badges coloridos)
```

**Props:**
- `results`: Array de resultados ('W' | 'D' | 'L')
- `limit`: Número máximo de badges (Temporada/5 partidas → 5, 10 partidas → 10)

**Cores:**
- **V (Vitória)**: `bg-success` (verde)
- **E (Empate)**: `bg-warning` (amarelo)
- **D (Derrota)**: `bg-danger` (vermelho)

---

### 18. PredictionsCard (v1.1)

Card de previsões com análise preditiva baseada em médias.

```typescript
// src/components/molecules/PredictionsCard.tsx

interface Previsao {
  tipo: string;           // ex: "Gols", "Escanteios"
  valorPrevisto: number;  // ex: 2.8
  confianca: 'alta' | 'media' | 'baixa';
  descricao: string;
}

interface PredictionsCardProps {
  previsoes: Previsao[];
  homeTeamName: string;
  awayTeamName: string;
}

export function PredictionsCard({
  previsoes,
  homeTeamName,
  awayTeamName,
}: PredictionsCardProps) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Icon name="analytics" className="text-primary-400" />
        <h3 className="font-semibold text-white">Previsões</h3>
      </div>

      <div className="grid gap-3">
        {previsoes.map((p, i) => (
          <div key={i} className="flex justify-between items-center">
            <span className="text-gray-400">{p.tipo}</span>
            <div className="flex items-center gap-2">
              <span className="text-white font-bold">
                {p.valorPrevisto.toFixed(1)}
              </span>
              <Badge
                variant={p.confianca === 'alta' ? 'success' : p.confianca === 'media' ? 'warning' : 'danger'}
                size="sm"
              >
                {p.confianca}
              </Badge>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Props:**
- `previsoes`: Array de previsões calculadas
- `homeTeamName`: Nome do time mandante
- `awayTeamName`: Nome do time visitante

---

### 19. DisciplineCard (v1.2)

Card de disciplina com métricas de cartões e faltas, incluindo dados do árbitro (competição + temporada).

```typescript
// src/components/molecules/DisciplineCard.tsx

interface DisciplineMetric {
  label: string;
  home: EstatisticaMetrica;
  away: EstatisticaMetrica;
}

interface ArbitroInfo {
  id: string;
  nome: string;
  partidas: number;           // Partidas na competição
  partidas_temporada: number; // Total na temporada
  media_cartoes_amarelos: number;  // Média na competição
  media_cartoes_temporada: number; // Média ponderada temporada
  media_faltas?: number | null;
}

interface DisciplineCardProps {
  metrics: DisciplineMetric[];
  homeTeamName: string;
  awayTeamName: string;
  arbitro?: ArbitroInfo | null;
}

function RefereeInfo({ arbitro }: { arbitro: ArbitroInfo }) {
  return (
    <div className="flex flex-col items-center justify-center p-3 bg-dark-tertiary/50 rounded-lg">
      <div className="w-10 h-10 rounded-full bg-dark-quaternary flex items-center justify-center mb-2">
        <Icon name="whistle" size="md" className="text-warning" />
      </div>
      <p className="text-sm font-medium text-white">{arbitro.nome}</p>
      <p className="text-xs text-gray-500">
        {arbitro.partidas} jogos · {arbitro.media_cartoes_amarelos.toFixed(1)} cartões/jogo (competição)
      </p>
      <p className="text-xs text-gray-400">
        {arbitro.partidas_temporada} jogos · {arbitro.media_cartoes_temporada.toFixed(1)} cartões/jogo (temporada)
      </p>
    </div>
  );
}

export function DisciplineCard({
  metrics,
  homeTeamName,
  awayTeamName,
  arbitro,
}: DisciplineCardProps) {
  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary col-span-full">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Icon name="card" size="sm" className="text-primary-400" />
        <h3 className="text-sm font-medium text-white">Disciplina</h3>
      </div>

      {/* Árbitro (centralizado) */}
      {arbitro && <RefereeInfo arbitro={arbitro} />}

      {/* Métricas em grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mt-4">
        {metrics.map((m) => (
          <DisciplineMetricRow key={m.label} {...m} homeTeamName={homeTeamName} awayTeamName={awayTeamName} />
        ))}
      </div>
    </div>
  );
}
```

**Props:**
- `metrics`: Array de métricas de disciplina (amarelos, faltas)
- `homeTeamName`: Nome do time mandante
- `awayTeamName`: Nome do time visitante
- `arbitro`: Informações do árbitro (opcional) - agora com dados de competição E temporada

**Display do Árbitro (v1.2):**
- Layout centralizado com ícone de apito maior
- **Linha 1:** Dados da competição atual (ex: "2 jogos · 0.5 cartões/jogo (competição)")
- **Linha 2:** Dados da temporada (ex: "9 jogos · 3.8 cartões/jogo (temporada)")

---

### 20. SmartSearchResults (v1.5)

Container de resultados da Busca Inteligente. Exibe progresso durante análise, estado vazio, filtro por estatística, e grid de OpportunityCards ordenados por score.

**Novidade v1.5:** Inclui `StatFilter` para filtrar oportunidades por tipo de estatística (client-side, sem recarregar dados).

```typescript
// src/components/organisms/SmartSearchResults.tsx

import { useState, useMemo } from 'react';
import { Icon, type IconName } from '@/components/atoms';
import { OpportunityCard } from '@/components/molecules';
import type { SmartSearchResult, SmartSearchProgress } from '@/types/smartSearch';

interface SmartSearchResultsProps {
  result: SmartSearchResult | null;
  progress: SmartSearchProgress | null;
  isAnalyzing: boolean;
  onClose?: () => void;
}

// Opções de estatísticas para filtro
const STAT_OPTIONS: { key: string; label: string; icon: IconName }[] = [
  { key: 'gols', label: 'Gols', icon: 'goal' },
  { key: 'escanteios', label: 'Escanteios', icon: 'corner' },
  { key: 'finalizacoes', label: 'Chutes', icon: 'shot' },
  { key: 'finalizacoes_gol', label: 'Chutes ao Gol', icon: 'target' },
  { key: 'cartoes_amarelos', label: 'Cartões', icon: 'card' },
  { key: 'faltas', label: 'Faltas', icon: 'foul' },
];

// Sub-componente: Filtro de estatísticas (toggle chips)
function StatFilter({
  ativos,
  onToggle,
}: {
  ativos: Set<string>;
  onToggle: (key: string) => void;
}) {
  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary mb-4">
      <div className="flex items-center gap-2 mb-3">
        <Icon name="filter" size="sm" className="text-gray-400" />
        <span className="text-sm text-gray-400">Filtrar por estatística:</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {STAT_OPTIONS.map(({ key, label, icon }) => {
          const isActive = ativos.has(key);
          return (
            <button
              key={key}
              onClick={() => onToggle(key)}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
                border transition-all duration-200
                ${isActive
                  ? 'bg-primary-500/20 text-primary-400 border-primary-500/50'
                  : 'bg-dark-tertiary text-gray-500 border-dark-quaternary hover:border-gray-600'
                }
              `}
            >
              <Icon name={icon} size="sm" />
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function SmartSearchResults({
  result,
  progress,
  isAnalyzing,
  onClose,
}: SmartSearchResultsProps) {
  // Estado dos filtros (todas ativas por padrão)
  const [filtrosAtivos, setFiltrosAtivos] = useState<Set<string>>(
    new Set(STAT_OPTIONS.map(s => s.key))
  );

  // Filtra oportunidades (client-side, sem recarregar)
  const oportunidadesFiltradas = useMemo(() => {
    if (!result) return [];
    return result.oportunidades.filter(op => filtrosAtivos.has(op.estatistica));
  }, [result, filtrosAtivos]);

  // Toggle de filtro (mínimo 1 ativo)
  const handleToggle = (key: string) => {
    setFiltrosAtivos(prev => {
      const next = new Set(prev);
      if (next.has(key) && next.size === 1) return prev; // Mínimo 1
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  // Estado: Analisando
  if (isAnalyzing && progress) {
    return <ProgressBar progress={progress} />;
  }

  // Estado: Com resultados
  if (result && result.oportunidades.length > 0) {
    return (
      <div>
        <ResultHeader result={result} filteredCount={oportunidadesFiltradas.length} onClose={onClose} />
        <StatFilter ativos={filtrosAtivos} onToggle={handleToggle} />

        {oportunidadesFiltradas.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2">
            {oportunidadesFiltradas.map((op, index) => (
              <OpportunityCard
                key={`${op.matchId}-${op.estatistica}-${op.tipo}-${op.linha}`}
                oportunidade={op}
                rank={index + 1}
              />
            ))}
          </div>
        ) : (
          <EmptyState isFiltered />
        )}
      </div>
    );
  }

  return null;
}
```

**Props:**
- `result`: Resultado completo da busca (`SmartSearchResult | null`)
- `progress`: Estado de progresso da análise (`SmartSearchProgress | null`)
- `isAnalyzing`: Boolean indicando se está analisando
- `onClose`: Callback opcional para fechar/resetar a busca

**Estados:**
1. **Analisando:** Progress bar com contador "X de Y partidas"
2. **Vazio:** Ícone + mensagem "Nenhuma oportunidade encontrada"
3. **Filtrado sem resultados:** Mensagem sugerindo alterar filtros
4. **Com resultados:** Header + StatFilter + Grid de OpportunityCards

**StatFilter (v1.5):**
- 6 chips toggle para cada estatística (Gols, Escanteios, Chutes, etc.)
- Todos ativos por padrão
- Clique alterna ativo/inativo
- Mínimo 1 filtro sempre ativo
- Filtragem instantânea (client-side, sem recarregar dados)
- Header mostra "X de Y oportunidades" quando filtrado

**Layout do Grid:**
- Mobile: 1 coluna (`grid-cols-1`)
- Desktop: 2 colunas (`md:grid-cols-2`)
- Gap: `gap-4`

**Ordenação:**
- Cards ordenados por `score` (maior primeiro)
- Score = `confiança × probabilidade`

---

## LAYOUT - 3 Componentes

### 21. PageLayout

Layout principal com header e footer.

```typescript
// src/components/layout/PageLayout.tsx

interface PageLayoutProps {
  children: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

export const PageLayout: React.FC<PageLayoutProps> = ({
  children,
  header,
  footer,
  maxWidth = 'xl',
}) => {
  const maxWidthClass = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-2xl',
    full: 'w-full',
  }[maxWidth];

  return (
    <div className="min-h-screen bg-dark-primary flex flex-col">
      {header && <header className="sticky top-0 z-50 bg-dark-secondary shadow-md">{header}</header>}

      <main className={`flex-1 mx-auto w-full ${maxWidthClass} px-4 py-6`}>
        {children}
      </main>

      {footer && <footer className="bg-dark-secondary border-t border-dark-tertiary">{footer}</footer>}
    </div>
  );
};
```

---

### 22. Container

Container responsivo.

```typescript
// src/components/layout/Container.tsx

interface ContainerProps {
  children: React.ReactNode;
  className?: string;
}

export const Container: React.FC<ContainerProps> = ({
  children,
  className = '',
}) => {
  return (
    <div className={`mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
};
```

---

### 23. Grid

Grid system responsivo.

```typescript
// src/components/layout/Grid.tsx

interface GridProps {
  children: React.ReactNode;
  cols?: 1 | 2 | 3 | 4;
  gap?: 2 | 4 | 6 | 8;
  responsive?: boolean;
  className?: string;
}

export const Grid: React.FC<GridProps> = ({
  children,
  cols = 3,
  gap = 6,
  responsive = true,
  className = '',
}) => {
  const gapClass = {
    2: 'gap-2',
    4: 'gap-4',
    6: 'gap-6',
    8: 'gap-8',
  }[gap];

  const responsiveClass = responsive
    ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3'
    : `grid-cols-${cols}`;

  return (
    <div
      className={`
        grid ${responsiveClass} ${gapClass}
        ${className}
      `}
    >
      {children}
    </div>
  );
};
```

---

## PAGES - 2 Páginas (v1)

### 24. HomePage/PartidasPage (Combinadas)

Página única com DatePicker e grid de MatchCards animados. Inclui botões de Busca Inteligente.

```typescript
// src/pages/HomePage.tsx

export const HomePage: React.FC = () => {
  const [selectedDate, setSelectedDate] = useStore((s) => [s.selectedDate, s.setDate]);
  const { data: partidas, isLoading, error } = usePartidas(selectedDate);

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* DatePicker */}
        <div className="flex gap-2 items-center">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-4 py-2 rounded-md bg-dark-secondary border border-dark-tertiary text-text-primary"
          />
          <p className="text-sm text-text-muted">
            {partidas?.total_partidas || 0} partidas
          </p>
        </div>

        {/* Loading State */}
        {isLoading && <LoadingSpinner size="lg" message="Carregando partidas..." />}

        {/* Error State */}
        {error && (
          <p className="text-red-500 text-sm">
            Erro ao carregar partidas. Tente novamente.
          </p>
        )}

        {/* MatchCards Grid com Animação Staggered */}
        {partidas && partidas.partidas.length > 0 ? (
          <Grid cols={3} gap={6} responsive>
            {partidas.partidas.map((partida) => (
              <MatchCard
                key={partida.id}
                partida={partida}
                onClick={() => navigate(`/partida/${partida.id}`)}
                animated
              />
            ))}
          </Grid>
        ) : (
          <p className="text-center text-text-muted py-8">
            Nenhuma partida encontrada para esta data.
          </p>
        )}
      </div>
    </PageLayout>
  );
};
```

---

### 25. EstatisticasPage

Página de estatísticas detalhadas com previsões e sequência de resultados.

```typescript
// src/pages/EstatisticasPage.tsx

export const EstatisticasPage: React.FC = () => {
  const { matchId } = useParams<{ matchId: string }>();
  const [filtro, setFiltro] = useState<'geral' | '5' | '10'>('geral');

  const { data: partida } = usePartidas(new Date().toISOString().split('T')[0]);
  const { data: stats, isLoading } = useStats(matchId!, filtro);

  const selectedPartida = partida?.partidas.find((p) => p.id === matchId);

  if (!selectedPartida || !stats) {
    return <LoadingSpinner size="lg" message="Carregando estatísticas..." />;
  }

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Back Button */}
        <Button
          variant="ghost"
          size="sm"
          icon={<Icon name="arrow_back" />}
          onClick={() => navigate('/')}
        >
          Voltar
        </Button>

        {/* Stats Panel */}
        <StatsPanel
          partida={selectedPartida}
          stats={stats}
          filtro={filtro}
          onFiltroChange={setFiltro}
        />
      </div>
    </PageLayout>
  );
};
```

---

## Otimizações de Performance (v1.5)

### React.memo

Os seguintes componentes são memoizados com `React.memo` para evitar re-renders desnecessários quando as props não mudam:

**Atoms (4 componentes):**
- `Icon` - Ícone estático, raramente muda
- `Badge` - Badge de estabilidade/confiança
- `RaceDot` - Ponto de resultado (W/D/L)
- `TeamBadge` - Escudo do time

**Molecules (5 componentes):**
- `StatsCard` - Card de estatística comparativa
- `OverUnderCard` - Card de over/under com probabilidades
- `PredictionsCard` - Card de previsões
- `DisciplineCard` - Card de disciplina (cartões/faltas)
- `OpportunityCard` - Card de oportunidade (Busca Inteligente)

**Padrão de implementação:**

```typescript
import { memo } from 'react';

interface ComponentProps {
  // ...props
}

export const Component = memo(function Component(props: ComponentProps) {
  // Renderização
  return <div>...</div>;
});
```

**Quando usar `memo`:**
- Componentes que recebem props estáveis (não mudam frequentemente)
- Componentes renderizados em listas
- Componentes com renderização custosa

**Quando NÃO usar:**
- Componentes com estado interno que muda frequentemente
- Componentes muito simples (overhead do memo pode ser maior que o benefício)

---

## Padrões de Implementação

### 1. Estrutura de Pastas

```
src/
├── components/
│   ├── atoms/
│   │   ├── Badge.tsx
│   │   ├── RaceDot.tsx
│   │   ├── Button.tsx
│   │   ├── TeamBadge.tsx
│   │   ├── Icon.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── index.ts
│   │
│   ├── molecules/
│   │   ├── TeamCard.tsx
│   │   ├── StatMetric.tsx
│   │   ├── ComparisonBar.tsx
│   │   ├── FilterToggle.tsx
│   │   ├── PeriodoToggle.tsx     # Sub-filtro de período (1T/2T/Integral)
│   │   ├── RaceRow.tsx
│   │   ├── OpportunityCard.tsx   # Card de oportunidade (v1.4)
│   │   └── index.ts
│   │
│   ├── organisms/
│   │   ├── MatchCard.tsx
│   │   ├── StatsPanel.tsx
│   │   ├── StatsCategory.tsx
│   │   ├── RaceBadges.tsx
│   │   ├── PredictionsCard.tsx
│   │   ├── DisciplineCard.tsx
│   │   ├── SmartSearchResults.tsx # Container busca inteligente (v1.4)
│   │   └── index.ts
│   │
│   └── layout/
│       ├── PageLayout.tsx
│       ├── Container.tsx
│       ├── Grid.tsx
│       └── index.ts
│
└── pages/
    ├── HomePage.tsx
    ├── EstatisticasPage.tsx
    └── index.ts
```

### 2. Export Pattern (index.ts)

```typescript
// src/components/atoms/index.ts
export { Badge } from './Badge';
export { RaceDot } from './RaceDot';
export { Button } from './Button';
export { TeamBadge } from './TeamBadge';
export { Icon } from './Icon';
export { LoadingSpinner } from './LoadingSpinner';

// Uso:
import { Badge, RaceDot, Button } from '@/components/atoms';
```

### 3. TypeScript Pattern

```typescript
// Sempre use interfaces para props
interface ComponentProps {
  prop1: string;
  prop2?: number;
  children?: React.ReactNode;
}

// Use React.FC para type safety
export const Component: React.FC<ComponentProps> = ({
  prop1,
  prop2 = 10,
  children,
}) => {
  return <div>{children}</div>;
};
```

---

## Ver Também

Para entender melhor este documento e implementar os componentes:

- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - Design tokens (cores, tipografia, spacing) que definem o visual de cada componente
- **[INTEGRACAO_API.md](INTEGRACAO_API.md)** - Services e hooks para buscar dados e passar aos componentes
- **[ARQUITETURA_FRONTEND.md](ARQUITETURA_FRONTEND.md)** - Folder structure e organização dos componentes
- **[RESPONSIVIDADE_E_ACESSIBILIDADE.md](RESPONSIVIDADE_E_ACESSIBILIDADE.md)** - Responsive design e WCAG AA compliance
- **[../MODELOS_DE_DADOS.md](../MODELOS_DE_DADOS.md)** - Schemas Pydantic (interfaces TypeScript)

**Próximos Passos:**
1. Implemente **6 atoms** (order: Badge, RaceDot, Button, TeamBadge, Icon, LoadingSpinner)
2. Implemente **7 molecules** (dependem dos atoms, inclui OpportunityCard)
3. Implemente **7 organisms** (dependem dos molecules, inclui SmartSearchResults)
4. Crie **2 pages** (HomePage + EstatisticasPage)
5. Integre com **INTEGRACAO_API.md** para conectar dados reais

---

**[⬆ Voltar ao topo](#componentes-react---catálogo-atomic-design)**
