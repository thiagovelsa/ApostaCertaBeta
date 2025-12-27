import { api } from './api';
import type { StatsResponse, FiltroEstatisticas, MandoFilter, CompeticaoInfo, EscudoResponse } from '@/types';

function buildStatsParams(
  filtro: FiltroEstatisticas,
  homeMando: MandoFilter,
  awayMando: MandoFilter
): Record<string, string> {
  const params: Record<string, string> = { filtro };

  if (homeMando) {
    params.home_mando = homeMando;
  }
  if (awayMando) {
    params.away_mando = awayMando;
  }

  return params;
}

async function fetchMatchStats(
  matchId: string,
  params: Record<string, string>
): Promise<StatsResponse> {
  const response = await api.get<StatsResponse>(`/api/partida/${matchId}/stats`, {
    params,
  });
  return response.data;
}

/**
 * Busca estatísticas de uma partida
 *
 * @param matchId - ID da partida
 * @param filtro - Filtro de período (geral, 5, 10)
 * @param homeMando - Subfiltro de mando para o mandante (casa/fora/null)
 * @param awayMando - Subfiltro de mando para o visitante (casa/fora/null)
 */
export async function getMatchStats(
  matchId: string,
  filtro: FiltroEstatisticas = 'geral',
  homeMando: MandoFilter = null,
  awayMando: MandoFilter = null
): Promise<StatsResponse> {
  const noSubfilters = !homeMando && !awayMando;
  const sameSubfilter = homeMando && awayMando && homeMando === awayMando;

  if (noSubfilters || sameSubfilter) {
    return fetchMatchStats(matchId, buildStatsParams(filtro, homeMando, awayMando));
  }

  // Fetch each side separately so one subfilter does not affect the other.
  const [homeResponse, awayResponse] = await Promise.all([
    fetchMatchStats(matchId, buildStatsParams(filtro, homeMando, null)),
    fetchMatchStats(matchId, buildStatsParams(filtro, null, awayMando)),
  ]);

  return {
    ...homeResponse,
    visitante: awayResponse.visitante,
    arbitro: homeResponse.arbitro ?? awayResponse.arbitro ?? null,
  };
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
