import { useQuery } from '@tanstack/react-query';
import { getMatchStats, getCompeticoes, getTeamBadge } from '@/services/statsService';
import type { FiltroEstatisticas, MandoFilter, PeriodoFilter } from '@/types';

/**
 * Hook para buscar estatísticas de uma partida
 *
 * @param matchId - ID da partida
 * @param filtro - Filtro de período (geral, 5, 10)
 * @param periodo - Subfiltro de período do jogo (integral, 1T, 2T)
 * @param homeMando - Subfiltro de mando para o mandante (casa/fora/null)
 * @param awayMando - Subfiltro de mando para o visitante (casa/fora/null)
 */
export function useStats(
  matchId: string | undefined,
  filtro: FiltroEstatisticas = 'geral',
  periodo: PeriodoFilter = 'integral',
  homeMando: MandoFilter = null,
  awayMando: MandoFilter = null
) {
  return useQuery({
    // Query key inclui todos os filtros para cache granular por combinação
    queryKey: ['stats', matchId, filtro, periodo, homeMando, awayMando],
    queryFn: () => getMatchStats(matchId!, filtro, periodo, homeMando, awayMando),
    // Usa defaults do QueryClient: staleTime=5min, gcTime=30min
    // Permite cache ao trocar filtros (ex: Geral → Últimos 5 → Geral = instantâneo)
    enabled: Boolean(matchId),
  });
}

/**
 * Hook para buscar lista de competições
 * staleTime: 24 horas (competições raramente mudam)
 */
export function useCompeticoes() {
  return useQuery({
    queryKey: ['competicoes'],
    queryFn: getCompeticoes,
    staleTime: 1000 * 60 * 60 * 24, // 24 hours
  });
}

/**
 * Hook para buscar escudo de um time
 * staleTime: infinito (escudos são permanentes)
 */
export function useTeamBadge(teamId: string | undefined) {
  return useQuery({
    queryKey: ['badge', teamId],
    queryFn: () => getTeamBadge(teamId!),
    staleTime: Infinity,
    gcTime: Infinity,
    enabled: Boolean(teamId),
  });
}
