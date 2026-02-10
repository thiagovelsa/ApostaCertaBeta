import { api } from './api';
import type {
  StatsResponse,
  FiltroEstatisticas,
  MandoFilter,
  PeriodoFilter,
  CompeticaoInfo,
  EscudoResponse,
} from '@/types';

function buildStatsParams(
  filtro: FiltroEstatisticas,
  periodo: PeriodoFilter,
  homeMando: MandoFilter,
  awayMando: MandoFilter,
  debug: boolean
): Record<string, string> {
  const params: Record<string, string> = { filtro };

  // Só envia periodo se não for o default (integral)
  if (periodo !== 'integral') {
    params.periodo = periodo;
  }

  if (homeMando) {
    params.home_mando = homeMando;
  }
  if (awayMando) {
    params.away_mando = awayMando;
  }

  if (debug) {
    params.debug = '1';
  }

  return params;
}

async function fetchMatchStats(
  matchId: string,
  params: Record<string, string>
): Promise<StatsResponse> {
  const response = await api.get<StatsResponse>(`/api/partida/${matchId}/analysis`, {
    params,
  });
  return response.data;
}

/**
 * Busca estatísticas de uma partida
 *
 * @param matchId - ID da partida
 * @param filtro - Filtro de período (geral, 5, 10)
 * @param periodo - Subfiltro de período do jogo (integral, 1T, 2T)
 * @param homeMando - Subfiltro de mando para o mandante (casa/fora/null)
 * @param awayMando - Subfiltro de mando para o visitante (casa/fora/null)
 */
export async function getMatchStats(
  matchId: string,
  filtro: FiltroEstatisticas = 'geral',
  periodo: PeriodoFilter = 'integral',
  homeMando: MandoFilter = null,
  awayMando: MandoFilter = null,
  debug: boolean = false
): Promise<StatsResponse> {
  // Always fetch once; backend handles "split fetch" when only one side has mando filter.
  // Doing it here can contaminate results due to backend's implicit default mando (pre-jogo).
  return fetchMatchStats(
    matchId,
    buildStatsParams(filtro, periodo, homeMando, awayMando, debug)
  );
}

/**
 * Lista todas as competições disponíveis
 */
export async function getCompeticoes(): Promise<CompeticaoInfo[]> {
  const response = await api.get<{ total: number; competicoes: CompeticaoInfo[] }>(
    '/api/competicoes'
  );
  return response.data.competicoes;
}

/**
 * Busca o escudo de um time
 */
export async function getTeamBadge(teamId: string): Promise<EscudoResponse> {
  const response = await api.get<EscudoResponse>(`/api/time/${teamId}/escudo`);
  return response.data;
}
