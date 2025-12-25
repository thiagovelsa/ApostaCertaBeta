import { useQuery } from '@tanstack/react-query';
import { getMatchStats, getCompeticoes, getTeamBadge } from '@/services/statsService';
import type { FiltroEstatisticas } from '@/types';

/**
 * Hook para buscar estatísticas de uma partida
 * staleTime: 6 horas (estatísticas de temporada são estáveis)
 */
export function useStats(matchId: string | undefined, filtro: FiltroEstatisticas = 'geral') {
  return useQuery({
    queryKey: ['stats', matchId, filtro],
    queryFn: () => getMatchStats(matchId!, filtro),
    staleTime: 1000 * 60 * 60 * 6, // 6 hours
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
