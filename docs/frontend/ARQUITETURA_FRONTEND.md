# Arquitetura Frontend - Sistema de Análise de Estatísticas de Futebol

**Versão:** 1.0
**Data:** 24 de dezembro de 2025
**Framework:** React 18 + TypeScript 5 + Vite 5

Guia técnico completo da arquitetura frontend, organização de código, state management, routing e otimizações de performance.

---

## 1. Estrutura de Pastas (Folder Structure)

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── manifest.json           # PWA manifest
│   └── assets/
│       ├── icons/              # PWA icons (192x192, 512x512)
│       └── fonts/              # Local font files (Outfit, Inter, Space Mono)
│
├── src/
│   ├── assets/
│   │   ├── images/             # Imagens estáticas (backgrounds, etc)
│   │   └── icons/              # Ícones customizados (se houver)
│   │
│   ├── components/             # Atomic Design - Organização Principal
│   │   ├── atoms/
│   │   │   ├── Badge.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Icon.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── RaceDot.tsx
│   │   │   └── TeamBadge.tsx
│   │   │
│   │   ├── molecules/
│   │   │   ├── ComparisonBar.tsx
│   │   │   ├── FilterToggle.tsx
│   │   │   ├── RaceRow.tsx
│   │   │   ├── StatMetric.tsx
│   │   │   └── TeamCard.tsx
│   │   │
│   │   ├── organisms/
│   │   │   ├── MatchCard.tsx
│   │   │   ├── StatsCategory.tsx
│   │   │   └── StatsPanel.tsx
│   │   │
│   │   └── layout/
│   │       ├── Container.tsx
│   │       ├── Grid.tsx
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── PageLayout.tsx
│   │
│   ├── pages/                  # Page Components (2 páginas v1)
│   │   ├── HomePage.tsx        # Merged: DatePicker + MatchCards grid
│   │   ├── EstatisticasPage.tsx # StatsPanel + FilterToggle
│   │   └── NotFoundPage.tsx     # 404 (optional)
│   │
│   ├── hooks/                  # Custom React Hooks
│   │   ├── usePartidas.ts      # Fetch partidas por data
│   │   ├── useStats.ts         # Fetch stats com filtro
│   │   ├── useCompetitions.ts  # Fetch competições
│   │   ├── useBadge.ts         # Fetch escudo do time
│   │   └── useLocalStorage.ts  # Persista dados locais (opcional)
│   │
│   ├── services/               # API Integration Layer
│   │   ├── api.ts              # Axios client setup
│   │   ├── partidasService.ts
│   │   ├── statsService.ts
│   │   ├── competicoesService.ts
│   │   └── escudosService.ts
│   │
│   ├── stores/                 # Zustand State Management
│   │   ├── filterStore.ts      # Filtro (geral/5/10)
│   │   ├── dateStore.ts        # Data selecionada
│   │   ├── uiStore.ts          # UI states (loading, modal)
│   │   └── index.ts            # Barrel export
│   │
│   ├── types/                  # TypeScript Interfaces
│   │   ├── index.ts            # Exports principais
│   │   ├── partida.ts          # TimeInfo, PartidaResumo, PartidaListResponse
│   │   ├── stats.ts            # EstatisticaMetrica, StatsResponse
│   │   ├── competicao.ts       # CompeticaoInfo
│   │   └── api.ts              # API types (AxiosError, etc)
│   │
│   ├── utils/                  # Utility Functions
│   │   ├── dateFormatter.ts    # Formata datas (YYYY-MM-DD → 25 dez)
│   │   ├── timeFormatter.ts    # Formata horários (HH:MM)
│   │   ├── cvClassifier.ts     # Classifica CV (Estável, Instável)
│   │   ├── numberFormatter.ts  # Formata números (2.5 gols)
│   │   ├── cn.ts               # Class name merger (clsx)
│   │   └── constants.ts        # Constantes globais
│   │
│   ├── lib/                    # External Library Setup
│   │   ├── queryClient.ts      # React Query configuration
│   │   ├── reactRouter.tsx     # Router setup (optional)
│   │   └── errorHandler.ts     # Global error handling
│   │
│   ├── App.tsx                 # Root component + routing
│   ├── main.tsx                # Entry point
│   ├── index.css               # Global styles (reset + Tailwind)
│   └── vite-env.d.ts           # Vite type definitions
│
├── .env                        # Local environment (NÃO commitar)
├── .env.example                # Template (commitar)
├── .env.production             # Production config
├── .gitignore
├── package.json
├── tsconfig.json               # TypeScript config
├── vite.config.ts              # Vite build config
├── tailwind.config.js          # Tailwind design tokens
├── postcss.config.js           # PostCSS + Tailwind
├── prettier.config.js          # Code formatting
├── .eslintrc.cjs               # ESLint rules
├── index.html                  # HTML entry
└── README.md                   # Project-level documentation
```

### Convenções de Nomenclatura

**Componentes:** PascalCase (BadgeComponent.tsx, MatchCard.tsx)
**Hooks:** camelCase com prefixo `use` (usePartidas.ts, useStats.ts)
**Services:** camelCase + sufixo `Service` (partidasService.ts)
**Stores:** camelCase + sufixo `Store` (filterStore.ts)
**Types:** PascalCase (PartidaResumo.ts, CompeticaoInfo.ts)
**Utils:** camelCase (dateFormatter.ts)
**Diretórios:** kebab-case ou lowercase (src/components/, src/pages/)

---

## 2. State Management com Zustand

### Setup Global (src/lib/queryClient.ts)

```typescript
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60 * 5, // 5 min default
      gcTime: 1000 * 60 * 10,   // 10 min garbage collection
    },
  },
});
```

### Store 1: filterStore (src/stores/filterStore.ts)

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export type FilterType = 'geral' | '5' | '10';

interface FilterStore {
  filtro: FilterType;
  setFiltro: (filtro: FilterType) => void;
  reset: () => void;
}

export const useFilterStore = create<FilterStore>()(
  devtools(
    persist(
      (set) => ({
        filtro: 'geral',
        setFiltro: (filtro) => set({ filtro }),
        reset: () => set({ filtro: 'geral' }),
      }),
      { name: 'filter-storage' }
    )
  )
);
```

**Uso em Componentes:**
```typescript
import { useFilterStore } from '@/stores';

export function FilterToggle() {
  const { filtro, setFiltro } = useFilterStore();

  return (
    <button onClick={() => setFiltro('5')}>
      Últimas 5 Partidas
    </button>
  );
}
```

### Store 2: dateStore (src/stores/dateStore.ts)

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface DateStore {
  selectedDate: string;  // YYYY-MM-DD
  setDate: (date: string) => void;
  resetDate: () => void;
}

export const useDateStore = create<DateStore>()(
  devtools(
    persist(
      (set) => ({
        selectedDate: new Date().toISOString().split('T')[0],
        setDate: (date) => set({ selectedDate: date }),
        resetDate: () => {
          const today = new Date().toISOString().split('T')[0];
          set({ selectedDate: today });
        },
      }),
      { name: 'date-storage' }
    )
  )
);
```

**Uso em DatePicker:**
```typescript
import { useDateStore } from '@/stores';
import { useState } from 'react';

export function DatePicker() {
  const { selectedDate, setDate } = useDateStore();
  const [input, setInput] = useState(selectedDate);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDate = e.target.value;
    setInput(newDate);
    setDate(newDate);
  };

  return (
    <input
      type="date"
      value={input}
      onChange={handleChange}
      min="2025-01-01"
      max={new Date().toISOString().split('T')[0]}
    />
  );
}
```

### Store 3: uiStore (src/stores/uiStore.ts)

```typescript
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface UIStore {
  isLoading: boolean;
  error: string | null;
  modalOpen: boolean;

  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  openModal: () => void;
  closeModal: () => void;
  reset: () => void;
}

export const useUIStore = create<UIStore>()(
  devtools((set) => ({
    isLoading: false,
    error: null,
    modalOpen: false,

    setLoading: (loading) => set({ isLoading: loading }),
    setError: (error) => set({ error }),
    openModal: () => set({ modalOpen: true }),
    closeModal: () => set({ modalOpen: false }),
    reset: () => set({ isLoading: false, error: null, modalOpen: false }),
  }))
);
```

**Uso em Error Boundary:**
```typescript
import { useUIStore } from '@/stores';

export function ErrorBoundary({ children }: { children: React.ReactNode }) {
  const { error, setError } = useUIStore();

  if (error) {
    return (
      <div className="p-4 bg-red-900 text-white rounded">
        <p>{error}</p>
        <button onClick={() => setError(null)}>Fechar</button>
      </div>
    );
  }

  return children;
}
```

### Barrel Export (src/stores/index.ts)

```typescript
export { useFilterStore, type FilterType } from './filterStore';
export { useDateStore } from './dateStore';
export { useUIStore } from './uiStore';
```

---

## 3. Routing com React Router v6

### App.tsx - Root Component

```typescript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';

import HomePage from '@/pages/HomePage';
import EstatisticasPage from '@/pages/EstatisticasPage';
import NotFoundPage from '@/pages/NotFoundPage';

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Route 1: Home + Partidas Combinadas */}
          <Route path="/" element={<HomePage />} />

          {/* Route 2: Match Statistics */}
          <Route path="/partida/:matchId" element={<EstatisticasPage />} />

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}
```

### Route 1: HomePage (`/`) - Home + Partidas Merged

**Fluxo:**
1. User lands on `/`
2. DatePicker visible (initial date = today)
3. User selects date → trigger usePartidas hook
4. React Query fetches MatchCards list
5. MatchCards rendered with staggered animation
6. User clicks MatchCard → navigate to `/partida/:matchId`

```typescript
// src/pages/HomePage.tsx
import { useDateStore } from '@/stores';
import { usePartidas } from '@/hooks/usePartidas';
import DatePicker from '@/components/molecules/DatePicker';
import MatchCard from '@/components/organisms/MatchCard';
import Grid from '@/components/layout/Grid';
import LoadingSpinner from '@/components/atoms/LoadingSpinner';
import { useNavigate } from 'react-router-dom';

export default function HomePage() {
  const { selectedDate, setDate } = useDateStore();
  const { data, isLoading, error } = usePartidas(selectedDate);
  const navigate = useNavigate();

  const handleDateChange = (date: string) => {
    setDate(date);
  };

  const handleMatchClick = (matchId: string) => {
    navigate(`/partida/${matchId}`);
  };

  return (
    <PageLayout header={<Header />} footer={<Footer />}>
      <Container>
        {/* DatePicker Section */}
        <section className="mb-12">
          <h1 className="text-3xl font-bold text-lime-500 mb-4">
            Análise de Partidas
          </h1>
          <DatePicker
            selectedDate={selectedDate}
            onChange={handleDateChange}
          />
        </section>

        {/* Loading State */}
        {isLoading && <LoadingSpinner />}

        {/* Error State */}
        {error && (
          <div className="p-4 bg-red-900 text-white rounded">
            {error instanceof Error ? error.message : 'Erro ao carregar partidas'}
          </div>
        )}

        {/* Matches Grid - Staggered Animation */}
        {data && data.partidas.length > 0 && (
          <section>
            <h2 className="text-xl font-semibold mb-6">
              {data.partidas.length} partidas em {selectedDate}
            </h2>
            <Grid cols={3} gap={6} responsive>
              {data.partidas.map((partida, index) => (
                <MatchCard
                  key={partida.id}
                  partida={partida}
                  onClick={() => handleMatchClick(partida.id)}
                  style={{ animationDelay: `${index * 100}ms` }}
                />
              ))}
            </Grid>
          </section>
        )}

        {/* Empty State */}
        {data && data.partidas.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg">
              Nenhuma partida disponível para {selectedDate}
            </p>
          </div>
        )}
      </Container>
    </PageLayout>
  );
}
```

### Route 2: EstatisticasPage (`/partida/:matchId`) - Match Stats

**Fluxo:**
1. User clicks MatchCard on HomePage
2. Navigates to `/partida/{matchId}`
3. EstatisticasPage loads
4. useStats hook fetches stats com filtro default 'geral'
5. StatsPanel rendered (3 colunas)
6. User pode mudar filtro (geral → 5 → 10)
7. useStats refetches automaticamente

```typescript
// src/pages/EstatisticasPage.tsx
import { useParams, useNavigate } from 'react-router-dom';
import { useFilterStore } from '@/stores';
import { useStats } from '@/hooks/useStats';
import StatsPanel from '@/components/organisms/StatsPanel';
import LoadingSpinner from '@/components/atoms/LoadingSpinner';
import Button from '@/components/atoms/Button';
import PageLayout from '@/components/layout/PageLayout';
import Container from '@/components/layout/Container';

export default function EstatisticasPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const { filtro, setFiltro } = useFilterStore();
  const navigate = useNavigate();

  if (!matchId) {
    return <div className="p-4">Match ID inválido</div>;
  }

  const { data: stats, isLoading, error } = useStats(
    matchId,
    filtro as 'geral' | '5' | '10'
  );

  const handleBack = () => {
    navigate('/');
  };

  return (
    <PageLayout header={<Header />} footer={<Footer />}>
      <Container>
        {/* Back Button */}
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={handleBack}
            icon={<ArrowBackIcon />}
          >
            Voltar
          </Button>
        </div>

        {/* Loading State */}
        {isLoading && <LoadingSpinner />}

        {/* Error State */}
        {error && (
          <div className="p-4 bg-red-900 text-white rounded">
            Erro ao carregar estatísticas
          </div>
        )}

        {/* Stats Panel */}
        {stats && (
          <StatsPanel
            partida={stats.partida}
            stats={stats}
            filtro={filtro as 'geral' | '5' | '10'}
            onFiltroChange={(newFiltro) => setFiltro(newFiltro)}
          />
        )}
      </Container>
    </PageLayout>
  );
}
```

---

## 4. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   HOMEPAGE (/)                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  DatePicker                                             │
│      ↓                                                  │
│  useDateStore.setDate(YYYY-MM-DD)                       │
│      ↓                                                  │
│  usePartidas(date) ← React Query Hook                   │
│      ↓                                                  │
│  partidasService.getByDate(date)                        │
│      ↓                                                  │
│  GET /api/partidas?data=YYYY-MM-DD                      │
│      ↓                                                  │
│  API Response: PartidaListResponse                      │
│      ↓                                                  │
│  Grid de MatchCards (staggered animation 100ms)         │
│      ↓                                                  │
│  onClick(matchId) → navigate('/partida/{matchId}')      │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               ESTATISTICAS PAGE (/partida/:matchId)      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  useParams() → matchId                                  │
│      ↓                                                  │
│  useFilterStore → filtro (geral/5/10)                   │
│      ↓                                                  │
│  useStats(matchId, filtro) ← React Query Hook           │
│      ↓                                                  │
│  statsService.getMatchStats(matchId, filtro)            │
│      ↓                                                  │
│  GET /api/partida/{matchId}/stats?filtro=geral|5|10     │
│      ↓                                                  │
│  API Response: StatsResponse                            │
│      ↓                                                  │
│  StatsPanel (3 colunas: mandante | info | visitante)    │
│  ├─ TeamCard (mandante) + stats                         │
│  ├─ Match info + FilterToggle                           │
│  └─ TeamCard (visitante) + stats                        │
│      ↓                                                  │
│  FilterToggle onChange → setFiltro(novoFiltro)          │
│      ↓                                                  │
│  useStats refetch automático (mudança de query key)     │
│                                                         │
└─────────────────────────────────────────────────────────┘

SERVICES & QUERIES (Background):

┌────────────────────────────────────┐
│     React Query Cache Manager      │
├────────────────────────────────────┤
│ queryKey: ['partidas', date]       │
│ staleTime: 1h                      │
│ gcTime: 2h                         │
├────────────────────────────────────┤
│ queryKey: ['stats', matchId, filtro]
│ staleTime: 6h                      │
│ gcTime: 12h                        │
├────────────────────────────────────┤
│ queryKey: ['competicoes']          │
│ staleTime: 24h                     │
│ gcTime: 7d                         │
├────────────────────────────────────┤
│ queryKey: ['badge', teamId]        │
│ staleTime: 7d                      │
│ gcTime: 30d                        │
└────────────────────────────────────┘
```

---

## 5. Performance Optimizations

### 5.1 React.memo para Componentes Caros

```typescript
// src/components/organisms/MatchCard.tsx
import { memo } from 'react';

interface MatchCardProps {
  partida: PartidaResumo;
  onClick?: () => void;
  style?: React.CSSProperties;
}

export default memo(function MatchCard({ partida, onClick, style }: MatchCardProps) {
  return (
    <div
      className="glass-card hover:scale-105 transition-transform"
      onClick={onClick}
      style={style}
    >
      {/* Card content */}
    </div>
  );
});
```

### 5.2 useMemo para Cálculos Caros

```typescript
// src/components/molecules/StatMetric.tsx
import { useMemo } from 'react';
import { cvClassifier } from '@/utils/cvClassifier';

interface StatMetricProps {
  label: string;
  value: number;
  cv: number;
  type: 'feitos' | 'sofridos';
}

export default function StatMetric({ label, value, cv, type }: StatMetricProps) {
  // Memizar classificação para evitar recalcular a cada render
  const classificacao = useMemo(() => cvClassifier(cv), [cv]);

  return (
    <div className="stat-metric">
      <h3>{label}</h3>
      <p className="text-mono text-2xl">{value.toFixed(2)}</p>
      <Badge variant="cv" value={classificacao} />
    </div>
  );
}
```

### 5.3 useCallback para Event Handlers

```typescript
// src/pages/HomePage.tsx
import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

export default function HomePage() {
  const navigate = useNavigate();

  // Memizar callback para evitar re-criar função a cada render
  const handleMatchClick = useCallback((matchId: string) => {
    navigate(`/partida/${matchId}`);
  }, [navigate]);

  return (
    <Grid>
      {partidas.map((partida) => (
        <MatchCard
          key={partida.id}
          partida={partida}
          onClick={() => handleMatchClick(partida.id)}
        />
      ))}
    </Grid>
  );
}
```

### 5.4 Code Splitting com React.lazy

```typescript
// src/App.tsx
import { Suspense, lazy } from 'react';
import LoadingSpinner from '@/components/atoms/LoadingSpinner';

const HomePage = lazy(() => import('@/pages/HomePage'));
const EstatisticasPage = lazy(() => import('@/pages/EstatisticasPage'));

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/partida/:matchId" element={<EstatisticasPage />} />
          </Routes>
        </Suspense>
      </Router>
    </QueryClientProvider>
  );
}
```

### 5.5 Image Lazy Loading

```typescript
// src/components/atoms/TeamBadge.tsx
export function TeamBadge({ src, alt, size = 'md' }: TeamBadgeProps) {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      className={cn('rounded-full object-cover', sizeClasses[size])}
      onError={(e) => {
        // Fallback to initials on error
        (e.target as HTMLImageElement).src = getFallbackImageUrl(alt);
      }}
    />
  );
}
```

### 5.6 React Query Optimizations

**Prefetch em Hover:**
```typescript
// src/components/organisms/MatchCard.tsx
import { useQueryClient } from '@tanstack/react-query';
import { statsService } from '@/services';

export function MatchCard({ partida, onClick }: MatchCardProps) {
  const queryClient = useQueryClient();

  const handleMouseEnter = () => {
    // Prefetch stats quando user faz hover na card
    queryClient.prefetchQuery({
      queryKey: ['stats', partida.id, 'geral'],
      queryFn: () => statsService.getMatchStats(partida.id, 'geral'),
      staleTime: 1000 * 60 * 60 * 6,
    });
  };

  return (
    <div onMouseEnter={handleMouseEnter} onClick={onClick}>
      {/* Card content */}
    </div>
  );
}
```

**Disable Automatic Refetching:**
```typescript
// React Query já está configurado em lib/queryClient.ts com:
// refetchOnWindowFocus: false
// Isso evita refetch quando o usuário volta para a aba
```

---

## 6. Integração Frontend-Backend

### Environment Variables

**`.env.example`:**
```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
VITE_ENV=development
```

**`.env` (local, não commitar):**
```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
VITE_ENV=development
```

**`.env.production`:**
```env
VITE_API_URL=https://api.palpitremestre.com
VITE_API_TIMEOUT=10000
VITE_ENV=production
```

### Axios Configuration

**src/services/api.ts:**
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 404) {
      console.error('Resource not found:', error.config?.url);
    } else if (error.response?.status === 500) {
      console.error('Server error:', error.response?.data?.detail);
    } else if (error.code === 'ECONNABORTED') {
      console.error('Request timeout after', import.meta.env.VITE_API_TIMEOUT, 'ms');
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 7. Development Workflow

### Setup Desenvolvimento

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Type checking
npx tsc --noEmit

# Linting
npm run lint

# Format code
npm run format

# Build for production
npm run build

# Preview production build
npm run preview
```

### Development Server Características

- **Hot Module Replacement (HMR)** automático
- **Type checking** em tempo real
- **Console errors** e **warnings** visíveis
- **Network tab** mostra todas requisições à API
- **React DevTools** disponível para debugging

---

## 8. Passos de Inicialização (Bootstrap)

### main.tsx
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### index.html
```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#84cc16" />
    <meta name="description" content="Sistema de análise de estatísticas de futebol" />
    <title>Palpite Mestre - Análise de Futebol</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

---

## Ver Também

Para aprofundar na arquitetura após ler este documento:

- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - Tokens de design (cores, tipografia, spacing, animações)
- **[COMPONENTES_REACT.md](COMPONENTES_REACT.md)** - Catálogo completo de 19 componentes
- **[INTEGRACAO_API.md](INTEGRACAO_API.md)** - Services, hooks React Query, type mappings
- **[../ARQUITETURA_BACKEND.md](../ARQUITETURA_BACKEND.md)** - Arquitetura do backend FastAPI
- **[../MODELOS_DE_DADOS.md](../MODELOS_DE_DADOS.md)** - Schemas Pydantic (que mapeiam para TypeScript)
- **[../API_SPECIFICATION.md](../API_SPECIFICATION.md)** - Documentação dos 4 endpoints
- **[../LOCAL_SETUP.md](../LOCAL_SETUP.md)** - Setup completo (backend + frontend)

**Próximos Passos Recomendados:**
1. Setup projeto Vite + TypeScript (npm create vite@latest frontend -- --template react-ts)
2. Instalar dependências: npm install react-router-dom @tanstack/react-query zustand axios
3. Configurar Tailwind com design tokens em tailwind.config.js
4. Criar folder structure baseado em "Seção 1" deste documento
5. Implementar 3 Zustand stores conforme "Seção 2"
6. Configurar Router conforme "Seção 3"
7. Implementar componentes seguindo [COMPONENTES_REACT.md](COMPONENTES_REACT.md)
8. Integrar services e hooks seguindo [INTEGRACAO_API.md](INTEGRACAO_API.md)

---

**[⬆ Voltar ao topo](#arquitetura-frontend---sistema-de-análise-de-estatísticas-de-futebol)**

---

**Status do Projeto:**
- ✅ Documentação técnica (✓ Frontend Arquitetura)
- 🔄 Backend (Em desenvolvimento)
- 🔄 Frontend (Planejado)

**Última atualização:** 24 de dezembro de 2025
