import { api } from './api';
import type { StatsResponse, FiltroEstatisticas, CompeticaoInfo, EscudoResponse } from '@/types';

/**
 * Busca estatísticas de uma partida
 */
export async function getMatchStats(
  matchId: string,
  filtro: FiltroEstatisticas = 'geral'
): Promise<StatsResponse> {
  const response = await api.get<StatsResponse>(`/api/partida/${matchId}/stats`, {
    params: { filtro },
  });
  return response.data;
}

/**
 * Lista todas as competições disponíveis
 */
export async function getCompeticoes(): Promise<CompeticaoInfo[]> {
  const response = await api.get<CompeticaoInfo[]>('/api/competicoes');
  return response.data;
}

/**
 * Busca o escudo de um time
 */
export async function getTeamBadge(teamId: string): Promise<EscudoResponse> {
  const response = await api.get<EscudoResponse>(`/api/time/${teamId}/escudo`);
  return response.data;
}
