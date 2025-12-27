# Integração API - Services e React Query Hooks

**Versão:** 1.2
**Data:** 27 de dezembro de 2025
**Framework:** React Query 5 (TanStack Query)
**HTTP Client:** Axios 1.6+

Guia completo de integração entre frontend React e API backend FastAPI.

---

## 📋 Índice

1. [Setup e Configuração](#setup-e-configuração)
2. [Services (4 camada de acesso a dados)](#services---camada-de-acesso-a-dados)
3. [Custom Hooks (4 React Query hooks)](#custom-hooks---react-query-hooks)
4. [Type Mappings](#type-mappings)
5. [Error Handling](#error-handling)
6. [Cache Strategy](#cache-strategy)
7. [Ver Também](#ver-também)

---

## Setup e Configuração

### 1. Instalação de Dependências

```bash
# React Query (TanStack Query)
npm install @tanstack/react-query

# HTTP Client
npm install axios

# DevTools (opcional, para debugging)
npm install @tanstack/react-query-devtools
```

### 2. QueryClient Setup

```typescript
// src/lib/queryClient.ts

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,  // Não refetch ao focar window
      retry: 1,                     // Retry 1 vez em erro
      staleTime: 1000 * 60 * 5,     // 5 min default (override por hook)
    },
    mutations: {
      retry: 1,
    },
  },
});
```

### 3. App Setup com QueryClientProvider

```typescript
// src/main.tsx

import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '@/lib/queryClient';
import App from './App';

export default function AppWrapper() {
  return (
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### 4. Environment Variables

```env
# .env.local
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
```

---

## Services - Camada de Acesso a Dados

### Axios Client Base

```typescript
// src/services/api.ts

import axios, { AxiosInstance, AxiosError } from 'axios';

// Custom error type
export interface ApiError extends AxiosError {
  message: string;
  status: number;
}

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor para error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error('API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

export default api;
```

### 1. PartidosService

Busca partidas por data.

```typescript
// src/services/partidasService.ts

import api from './api';
import { PartidaListResponse, PartidaResumo } from '@/types';

interface GetPartidasByDateParams {
  data: string;  // YYYY-MM-DD format
}

export const partidasService = {
  /**
   * Busca partidas de uma data específica
   * GET /api/partidas?data=2025-12-27
   */
  async getByDate(data: string): Promise<PartidaListResponse> {
    try {
      const response = await api.get('/api/partidas', {
        params: { data },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching partidas:', error);
      throw error;
    }
  },

  /**
   * Utility: Filtra partidas por competição
   */
  filterByCompetition(
    partidas: PartidaResumo[],
    competition: string
  ): PartidaResumo[] {
    return partidas.filter((p) => p.competicao === competition);
  },

  /**
   * Utility: Ordena partidas por horário
   */
  sortByTime(partidas: PartidaResumo[]): PartidaResumo[] {
    return [...partidas].sort((a, b) => a.horario.localeCompare(b.horario));
  },
};
```

**Endpoint Mapping:**
- Backend: `GET /api/partidas?data=YYYY-MM-DD`
- Response: `PartidaListResponse`
- Cache TTL: 1 hora (match backend `CACHE_TTL_SCHEDULE=3600`)

---

### 2. StatsService

Busca estatísticas detalhadas de uma partida.

```typescript
// src/services/statsService.ts

import api from './api';
import { StatsResponse, MandoFilter } from '@/types';

type FilterType = 'geral' | '5' | '10';

export const statsService = {
  /**
   * Busca estatísticas de uma partida
   * GET /api/partida/{matchId}/stats?filtro=geral|5|10&home_mando=casa|fora&away_mando=casa|fora
   *
   * @param matchId - ID da partida
   * @param filtro - Filtro principal (geral, últimas 5, últimas 10)
   * @param homeMando - Sub-filtro Casa/Fora para o mandante (opcional)
   * @param awayMando - Sub-filtro Casa/Fora para o visitante (opcional)
   */
  async getMatchStats(
    matchId: string,
    filtro: FilterType = 'geral',
    homeMando: MandoFilter = null,
    awayMando: MandoFilter = null
  ): Promise<StatsResponse> {
    try {
      const params: Record<string, string> = { filtro };

      // Adiciona parâmetros de mando apenas se definidos
      if (homeMando) params.home_mando = homeMando;
      if (awayMando) params.away_mando = awayMando;

      const response = await api.get(`/api/partida/${matchId}/stats`, {
        params,
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching stats for match ${matchId}:`, error);
      throw error;
    }
  },

  /**
   * Utility: Calcula classificação CV
   */
  getCVClassification(cv: number): string {
    if (cv < 0.15) return 'Muito Estável';
    if (cv < 0.30) return 'Estável';
    if (cv < 0.45) return 'Moderado';
    if (cv < 0.60) return 'Instável';
    return 'Muito Instável';
  },

  /**
   * Utility: Formata números com 2 casas decimais
   */
  formatNumber(value: number): string {
    return value.toFixed(2);
  },
};
```

**Endpoint Mapping:**
- Backend: `GET /api/partida/{matchId}/stats?filtro=geral|5|10&home_mando=casa|fora&away_mando=casa|fora`
- Response: `StatsResponse`
- Cache TTL: 6 horas (match backend `CACHE_TTL_SEASONSTATS=21600`)

**Parâmetros de Mando (Sub-filtro Casa/Fora):**
- `home_mando` - Filtra partidas do mandante: `casa` (apenas jogos em casa) ou `fora` (apenas fora)
- `away_mando` - Filtra partidas do visitante: `casa` ou `fora`
- Ambos são opcionais e independentes (pode aplicar a um time, ambos, ou nenhum)
- Combinável com o filtro principal (`geral`, `5`, `10`)

---

### 3. CompeticoesService

Busca lista de competições disponíveis.

```typescript
// src/services/competicoesService.ts

import api from './api';
import { CompeticaoInfo } from '@/types';

export const competicoesService = {
  /**
   * Busca todas as competições disponíveis
   * GET /api/competicoes
   */
  async getAll(): Promise<CompeticaoInfo[]> {
    try {
      const response = await api.get('/api/competicoes');
      return response.data;
    } catch (error) {
      console.error('Error fetching competicoes:', error);
      throw error;
    }
  },

  /**
   * Utility: Filtra competições por ID
   */
  findById(competicoes: CompeticaoInfo[], id: string): CompeticaoInfo | undefined {
    return competicoes.find((c) => c.id === id);
  },

  /**
   * Utility: Ordena alfabeticamente
   */
  sortAlphabetically(competicoes: CompeticaoInfo[]): CompeticaoInfo[] {
    return [...competicoes].sort((a, b) => a.nome.localeCompare(b.nome));
  },
};
```

**Endpoint Mapping:**
- Backend: `GET /api/competicoes`
- Response: `CompeticaoInfo[]`
- Cache TTL: 24 horas (dados estáveis)

---

### 4. EscudosService

Busca escudos/logos de times.

```typescript
// src/services/escudosService.ts

import api from './api';

interface GetBadgeResponse {
  escudo: string;  // URL da imagem
}

export const escudosService = {
  /**
   * Busca escudo de um time
   * GET /api/time/{teamId}/escudo?nome=Team%20Name
   */
  async getByTeamId(
    teamId: string,
    fallbackName?: string
  ): Promise<string> {
    try {
      const params = fallbackName ? { nome: fallbackName } : {};
      const response = await api.get<GetBadgeResponse>(
        `/api/time/${teamId}/escudo`,
        { params }
      );
      return response.data.escudo;
    } catch (error) {
      console.error(`Error fetching badge for team ${teamId}:`, error);
      // Return placeholder image on error
      return `https://via.placeholder.com/48?text=${fallbackName || 'TEAM'}`;
    }
  },

  /**
   * Utility: Valida URL de imagem
   */
  async validateImageUrl(url: string): Promise<boolean> {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve(true);
      img.onerror = () => resolve(false);
      img.src = url;
    });
  },
};
```

**Endpoint Mapping:**
- Backend: `GET /api/time/{teamId}/escudo?nome=Team%20Name`
- Response: `{ escudo: "https://..." }`
- Cache TTL: 7 dias (match backend `CACHE_TTL_BADGES=604800`)

---

## Custom Hooks - React Query Hooks

### 1. usePartidas

```typescript
// src/hooks/usePartidas.ts

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { partidasService } from '@/services';
import { PartidaListResponse } from '@/types';

interface UsePartidasOptions {
  enabled?: boolean;
}

export const usePartidas = (
  data: string,
  options?: UsePartidasOptions
): UseQueryResult<PartidaListResponse, Error> => {
  return useQuery({
    queryKey: ['partidas', data],  // Unique key for cache
    queryFn: () => partidasService.getByDate(data),
    staleTime: 1000 * 60 * 60,  // 1 hora (match backend CACHE_TTL_SCHEDULE)
    gcTime: 1000 * 60 * 60 * 2,  // 2 horas (garbage collection)
    enabled: !!data && (options?.enabled !== false),  // Only fetch if data is set
    refetchOnWindowFocus: false,
  });
};

// Exemplo de Uso:
/*
function MyComponent() {
  const { data, isLoading, error } = usePartidas('2025-12-27');

  if (isLoading) return <LoadingSpinner />;
  if (error) return <p>Erro: {error.message}</p>;
  if (!data) return <p>Sem dados</p>;

  return (
    <div>
      <h1>{data.total_partidas} partidas</h1>
      {data.partidas.map((p) => (
        <MatchCard key={p.id} partida={p} />
      ))}
    </div>
  );
}
*/
```

**Cache Behavior:**
- `staleTime: 1h` - Dados considerados "fresh" por 1 hora
- `gcTime: 2h` - Dados mantidos em cache por 2 horas (garbage collection)
- `enabled` - Só faz requisição se data estiver definida

---

### 2. useStats

```typescript
// src/hooks/useStats.ts

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { statsService } from '@/services';
import { StatsResponse, MandoFilter } from '@/types';

interface UseStatsOptions {
  enabled?: boolean;
}

export const useStats = (
  matchId: string | undefined,
  filtro: 'geral' | '5' | '10' = 'geral',
  homeMando: MandoFilter = null,
  awayMando: MandoFilter = null,
  options?: UseStatsOptions
): UseQueryResult<StatsResponse, Error> => {
  return useQuery({
    // Query key inclui todos os filtros para cache separado
    queryKey: ['stats', matchId, filtro, homeMando, awayMando],
    queryFn: () => statsService.getMatchStats(matchId!, filtro, homeMando, awayMando),
    staleTime: 1000 * 60 * 60 * 6,  // 6 horas (match backend CACHE_TTL_SEASONSTATS)
    gcTime: 1000 * 60 * 60 * 12,  // 12 horas
    enabled: !!matchId && (options?.enabled !== false),
    refetchOnWindowFocus: false,
  });
};

// Exemplo de Uso:
/*
function EstatisticasPage() {
  const { matchId } = useParams();
  const { filtro, homeMando, awayMando, toggleHomeMando, toggleAwayMando } = useFilterStore();

  // Hook refaz fetch automaticamente quando qualquer filtro muda
  const { data: stats, isLoading } = useStats(matchId, filtro, homeMando, awayMando);

  return (
    <StatsPanel
      stats={stats}
      isLoading={isLoading}
      homeMando={homeMando}
      awayMando={awayMando}
      onToggleHomeMando={toggleHomeMando}
      onToggleAwayMando={toggleAwayMando}
    />
  );
}
*/
```

**Cache Behavior:**
- `staleTime: 6h` - Alinhado com backend TTL de season stats
- Cache key inclui `filtro`, `homeMando`, `awayMando` - Diferentes combinações = diferentes caches
- Refetch automático ao mudar qualquer filtro (query key muda)
- `homeMando` e `awayMando` são independentes (podem ser `null`, `'casa'`, ou `'fora'`)

---

### 3. useCompetitions

```typescript
// src/hooks/useCompetitions.ts

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { competicoesService } from '@/services';
import { CompeticaoInfo } from '@/types';

export const useCompetitions = (): UseQueryResult<CompeticaoInfo[], Error> => {
  return useQuery({
    queryKey: ['competicoes'],  // Static query key (não muda)
    queryFn: competicoesService.getAll,
    staleTime: 1000 * 60 * 60 * 24,  // 24 horas (dados muito estáveis)
    gcTime: 1000 * 60 * 60 * 24 * 7,  // 7 dias
    refetchOnWindowFocus: false,
  });
};

// Exemplo de Uso:
/*
function CompetitionFilter() {
  const { data: competicoes } = useCompetitions();

  return (
    <select>
      {competicoes?.map((c) => (
        <option key={c.id} value={c.id}>
          {c.nome}
        </option>
      ))}
    </select>
  );
}
*/
```

**Cache Behavior:**
- Longa duração de cache (24h + 7d GC)
- Raramente refetch (dados não mudam)
- Ideal para dropdowns e filtros

---

### 4. useBadge

```typescript
// src/hooks/useBadge.ts

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { escudosService } from '@/services';

interface UseBadgeOptions {
  fallbackName?: string;
}

export const useBadge = (
  teamId: string,
  options?: UseBadgeOptions
): UseQueryResult<string, Error> => {
  return useQuery({
    queryKey: ['badge', teamId],  // Separa cache por teamId
    queryFn: () =>
      escudosService.getByTeamId(teamId, options?.fallbackName),
    staleTime: 1000 * 60 * 60 * 24 * 7,  // 7 dias (match backend CACHE_TTL_BADGES)
    gcTime: 1000 * 60 * 60 * 24 * 30,  // 30 dias
    refetchOnWindowFocus: false,
  });
};

// Exemplo de Uso:
/*
function TeamBadgeWrapper({ teamId, teamName }: { teamId: string; teamName: string }) {
  const { data: escudoUrl, isLoading } = useBadge(teamId, {
    fallbackName: teamName.substring(0, 3).toUpperCase(),
  });

  if (isLoading) return <div className="w-12 h-12 bg-gray-300 rounded-full" />;

  return (
    <TeamBadge src={escudoUrl || ''} alt={teamName} size="md" />
  );
}
*/
```

**Cache Behavior:**
- Muito longa duração (7 dias + 30 dias GC)
- Imagens não mudam frequentemente
- Um badge por teamId

---

## Type Mappings

Mapeamento entre Schemas Pydantic (Backend) e TypeScript Interfaces (Frontend).

### API Response Types

```typescript
// src/types/index.ts

/**
 * MATCH/PARTIDA TYPES
 */

export interface TimeInfo {
  id: string;
  nome: string;
  codigo: string;
  escudo?: string;  // URL ou undefined
}

export interface PartidaResumo {
  id: string;
  data: string;     // YYYY-MM-DD
  horario: string;  // HH:MM
  competicao: string;
  estadio: string;
  mandante: TimeInfo;
  visitante: TimeInfo;
}

export interface PartidaListResponse {
  data: string;     // YYYY-MM-DD
  total_partidas: number;
  partidas: PartidaResumo[];
}

/**
 * FILTER TYPES
 */

// Tipo para filtro principal (temporada/últimos 5/últimos 10)
export type FiltroEstatisticas = 'geral' | '5' | '10';

// Tipo para sub-filtro Casa/Fora (independente por time)
export type MandoFilter = 'casa' | 'fora' | null;

/**
 * STATISTICS TYPES
 */

// Tipo para resultado de partida (W=Win, D=Draw, L=Loss)
export type FormResult = 'W' | 'D' | 'L';

// Classificação do Coeficiente de Variação
export type CVClassificacao =
  | 'Muito Estável'
  | 'Estável'
  | 'Moderado'
  | 'Instável'
  | 'Muito Instável';

export interface EstatisticaMetrica {
  media: number;
  cv: number;                     // Coeficiente de Variação (0.0-1.0)
  classificacao: CVClassificacao; // Classificação baseada no CV
}

export interface EstatisticaFeitos {
  feitos: EstatisticaMetrica;
  sofridos: EstatisticaMetrica;
}

export interface EstatisticasAgregadas {
  gols: EstatisticaFeitos;
  escanteios: EstatisticaFeitos;
  finalizacoes: EstatisticaFeitos;
  finalizacoes_gol: EstatisticaFeitos;
  cartoes_amarelos: EstatisticaMetrica;
  cartoes_vermelhos: EstatisticaMetrica;
  faltas: EstatisticaFeitos;
}

export interface TimeComEstatisticas {
  id: string;
  nome: string;
  escudo: string | null;
  estatisticas: EstatisticasAgregadas;
  recent_form: FormResult[];  // Sequência de resultados (V/E/D)
}

export interface ArbitroInfo {
  id: string;
  nome: string;
  partidas: number;           // Partidas na competição específica
  partidas_temporada: number; // Total na temporada (todas competições)
  media_cartoes_amarelos: number;  // Média na competição
  media_cartoes_temporada: number; // Média ponderada na temporada
  media_faltas?: number | null;
}

export interface StatsResponse {
  filtro_aplicado: 'geral' | '5' | '10';
  partidas_analisadas: number;
  mandante: TimeComEstatisticas;
  visitante: TimeComEstatisticas;
  arbitro?: ArbitroInfo;
}

/**
 * COMPETITION TYPES
 */

export interface CompeticaoInfo {
  id: string;
  nome: string;
  codigo?: string;
  pais?: string;
}
```

---

## Error Handling

### Error Handling Strategy

```typescript
// src/hooks/usePartidas.ts (exemplo completo com error handling)

import { useQuery } from '@tanstack/react-query';
import { AxiosError } from 'axios';

export const usePartidas = (data: string) => {
  return useQuery({
    queryKey: ['partidas', data],
    queryFn: async () => {
      try {
        const response = await api.get('/api/partidas', { params: { data } });
        return response.data;
      } catch (error) {
        // Handle specific error types
        if (axios.isAxiosError(error)) {
          if (error.response?.status === 404) {
            throw new Error('Partidas não encontradas para esta data');
          } else if (error.response?.status === 400) {
            throw new Error('Data inválida. Use formato YYYY-MM-DD');
          } else if (error.response?.status === 500) {
            throw new Error('Erro no servidor. Tente novamente mais tarde.');
          }
        }
        throw error;
      }
    },
    retry: (failureCount, error) => {
      // Retry apenas em erros de rede (não 4xx/5xx específicos)
      if (axios.isAxiosError(error)) {
        return error.response?.status! >= 500 && failureCount < 3;
      }
      return failureCount < 3;
    },
  });
};
```

### Component Error Display

```typescript
// src/pages/HomePage.tsx

function HomePage() {
  const { data, isLoading, error } = usePartidas(selectedDate);

  if (isLoading) return <LoadingSpinner size="lg" />;

  if (error) {
    return (
      <div className="p-4 bg-red-500/20 border border-red-500 rounded-lg">
        <p className="text-red-400 font-medium">
          {error instanceof Error ? error.message : 'Erro ao carregar partidas'}
        </p>
        <button onClick={() => window.location.reload()} className="mt-2">
          Tentar Novamente
        </button>
      </div>
    );
  }

  if (!data?.partidas.length) {
    return (
      <p className="text-center text-text-muted py-8">
        Nenhuma partida encontrada.
      </p>
    );
  }

  return <div>{/* content */}</div>;
}
```

---

## Cache Strategy

Alinhamento de cache frontend com TTLs backend:

| Recurso | Backend TTL | Frontend staleTime | Frontend gcTime | Uso |
|---------|-------------|-------------------|-----------------|-----|
| **Partidas** | 3600s (1h) | 1h | 2h | Muda frequentemente |
| **Stats** | 21600s (6h) | 6h | 12h | Relativamente estável |
| **Competições** | N/A | 24h | 7d | Muito estável |
| **Badges/Logos** | 604800s (7d) | 7d | 30d | Nunca muda |

### Cache Invalidation (quando necessário)

```typescript
// src/hooks/usePartidas.ts (com refetch manual)

const queryClient = useQueryClient();

function MatchCard({ partida }: { partida: PartidaResumo }) {
  const handleRefresh = () => {
    // Invalida cache de partidas e força refetch
    queryClient.invalidateQueries({
      queryKey: ['partidas', partida.data],
    });

    // Ou refetch específico de stats
    queryClient.refetchQueries({
      queryKey: ['stats', partida.id],
    });
  };

  return (
    <button onClick={handleRefresh}>
      🔄 Atualizar
    </button>
  );
}
```

---

## Ver Também

Para entender melhor este documento e o contexto:

- **[COMPONENTES_REACT.md](COMPONENTES_REACT.md)** - Componentes que usam estes hooks (17 molecules/organisms/pages)
- **[API_SPECIFICATION.md](../API_SPECIFICATION.md)** - Especificação detalhada de todos os endpoints
- **[MODELOS_DE_DADOS.md](../MODELOS_DE_DADOS.md)** - Schemas Pydantic (mapeados para TypeScript aqui)
- **[ARQUITETURA_BACKEND.md](../ARQUITETURA_BACKEND.md)** - Lógica backend destes endpoints
- **[ARQUITETURA_FRONTEND.md](ARQUITETURA_FRONTEND.md)** - Como organizar services/ e hooks/

**Próximos Passos:**
1. Implemente os **4 services** (partidasService, statsService, competicoesService, escudosService)
2. Implemente os **4 custom hooks** (usePartidas, useStats, useCompetitions, useBadge)
3. Use os hooks nos **componentes** (Page, StatsPanel, etc)
4. Implemente **error handling** nos componentes
5. Monitore cache com **React Query DevTools**

**Troubleshooting:**
- **"useQuery não funciona"** - Garanta que `<QueryClientProvider>` envolve App
- **"Cache não está sendo usado"** - Verifique `staleTime` e `gcTime` em milissegundos
- **"Dados antigos sendo exibidos"** - Use `queryClient.invalidateQueries()` para forçar refetch
- **"CORS error"** - Verifique `VITE_API_URL` em `.env.local`

---

**[⬆ Voltar ao topo](#integração-api---services-e-react-query-hooks)**
