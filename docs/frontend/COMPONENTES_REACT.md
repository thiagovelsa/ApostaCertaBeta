# Componentes React - Catálogo Atomic Design

**Versão:** 1.0
**Data:** 24 de dezembro de 2025
**Pattern:** Atomic Design (Atoms → Molecules → Organisms → Pages)
**Total de Componentes:** 19 (v1)

Catálogo completo de componentes React + TypeScript para implementação do frontend.

---

## 📋 Índice

1. [ATOMS (6)](#atoms---6-componentes)
2. [MOLECULES (5)](#molecules---5-componentes)
3. [ORGANISMS (3)](#organisms---3-componentes)
4. [LAYOUT (3)](#layout---3-componentes)
5. [PAGES (2)](#pages---2-páginas-v1)
6. [Padrões de Implementação](#padrões-de-implementação)
7. [Ver Também](#ver-também)

---

## ATOMS - 6 Componentes

### 1. Badge

Pequena tag para indicar status, CV, ou tipo.

```typescript
// src/components/atoms/Badge.tsx

interface BadgeProps {
  variant: 'cv' | 'status';
  value: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant,
  value,
  size = 'md',
  className = '',
}) => {
  // Variantes e cores por tipo
  const getBgColor = () => {
    if (variant === 'cv') {
      switch (value) {
        case 'Muito Estável':
          return 'bg-emerald-500/20 text-emerald-400';
        case 'Estável':
          return 'bg-green-500/20 text-green-400';
        case 'Moderado':
          return 'bg-yellow-500/20 text-yellow-400';
        case 'Instável':
          return 'bg-orange-500/20 text-orange-400';
        case 'Muito Instável':
          return 'bg-red-500/20 text-red-400';
        default:
          return 'bg-gray-500/20 text-gray-400';
      }
    }
    return 'bg-blue-500/20 text-blue-400';
  };

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span
      className={`
        inline-block rounded-full font-medium
        ${sizeClasses[size]}
        ${getBgColor()}
        ${className}
      `}
    >
      {value}
    </span>
  );
};

// Exemplo de Uso:
// <Badge variant="cv" value="Estável" size="md" />
// <Badge variant="status" value="Online" />
```

**Props:**
- `variant`: Tipo de badge ('cv' para CV classification, 'status' para online/offline)
- `value`: Texto a exibir
- `size`: Tamanho (sm/md/lg)
- `className`: Classes Tailwind adicionais

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

## MOLECULES - 5 Componentes

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

## ORGANISMS - 3 Componentes

### 12. MatchCard

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

### 13. StatsPanel

Painel de estatísticas comparando mandante e visitante.

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

### 14. StatsCategory

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

## LAYOUT - 3 Componentes

### 15. PageLayout

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

### 16. Container

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

### 17. Grid

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

### 18. HomePage/PartidasPage (Combinadas ✅)

Página única com DatePicker e grid de MatchCards animados.

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

### 19. EstatisticasPage

Página de estatísticas detalhadas (sem predictions v1).

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
│   │   ├── RaceRow.tsx
│   │   └── index.ts
│   │
│   ├── organisms/
│   │   ├── MatchCard.tsx
│   │   ├── StatsPanel.tsx
│   │   ├── StatsCategory.tsx
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
2. Implemente **5 molecules** (dependem dos atoms)
3. Implemente **3 organisms** (dependem dos molecules)
4. Crie **2 pages** (HomePage/PartidasPage combinadas + EstatisticasPage)
5. Integre com **INTEGRACAO_API.md** para conectar dados reais

---

**[⬆ Voltar ao topo](#componentes-react---catálogo-atomic-design)**
