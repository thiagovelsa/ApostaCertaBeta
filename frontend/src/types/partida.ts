/**
 * Informações de um time (alinhado com backend)
 */
export interface TimeInfo {
  id: string;
  nome: string;
  codigo: string;
  escudo?: string | null;
}

/**
 * Resumo de uma partida (alinhado com backend PartidaResumo)
 */
export interface PartidaResumo {
  id: string;
  data: string; // formato YYYY-MM-DD
  horario: string; // formato HH:MM:SS
  competicao: string;
  estadio?: string | null;
  mandante: TimeInfo;
  visitante: TimeInfo;
}

/**
 * Resposta da listagem de partidas (alinhado com backend)
 */
export interface PartidaListResponse {
  data: string;
  total_partidas: number;
  partidas: PartidaResumo[];
}
