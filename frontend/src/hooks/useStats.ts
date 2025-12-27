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
    // Periodo no cache key para invalidação correta
    queryKey: ['stats', matchId, filtro, periodo, homeMando, awayMando],
    queryFn: () => getMatchStats(matchId!, filtro, periodo, homeMando, awayMando),
    staleTime: 0, // Sem cache - sempre busca dados frescos
    gcTime: 0,
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
