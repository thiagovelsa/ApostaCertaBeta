/**
 * Classificação do Coeficiente de Variação
 * Thresholds: <0.15 MuitoEstável, <0.30 Estável, <0.50 Moderado, <0.75 Instável, >=0.75 MuitoInstável
 */
export type CVClassificacao =
  | 'Muito Estável'
  | 'Estável'
  | 'Moderado'
  | 'Instável'
  | 'Muito Instável';

/**
 * Métrica estatística individual (alinhado com backend EstatisticaMetrica)
 */
export interface EstatisticaMetrica {
  media: number;
  cv: number;
  classificacao: CVClassificacao;
}

/**
 * Estatísticas feitas vs sofridas (alinhado com backend EstatisticaFeitos)
 */
export interface EstatisticaFeitos {
  feitos: EstatisticaMetrica;
  sofridos: EstatisticaMetrica;
}

/**
 * Estatísticas completas de um time (alinhado com backend EstatisticasTime)
 */
export interface EstatisticasTime {
  escanteios: EstatisticaFeitos;
  gols: EstatisticaFeitos;
  finalizacoes: EstatisticaFeitos;
  finalizacoes_gol: EstatisticaFeitos;
  cartoes_amarelos: EstatisticaMetrica;
  cartoes_vermelhos: EstatisticaMetrica;
  faltas: EstatisticaMetrica;
}

/**
 * Time com suas estatísticas (alinhado com backend TimeComEstatisticas)
 */
export interface TimeComEstatisticas {
  id: string;
  nome: string;
  escudo?: string | null;
  estatisticas: EstatisticasTime;
}

/**
 * Filtro de período para estatísticas
 */
export type FiltroEstatisticas = 'geral' | '5' | '10';

/**
 * Resposta completa de estatísticas (alinhado com backend StatsResponse)
 */
export interface StatsResponse {
  partida: import('./partida').PartidaResumo;
  filtro_aplicado: FiltroEstatisticas;
  partidas_analisadas: number;
  mandante: TimeComEstatisticas;
  visitante: TimeComEstatisticas;
}

/**
 * Informação de competição (alinhado com backend CompeticaoInfo)
 */
export interface CompeticaoInfo {
  id: string;
  nome: string;
  pais: string;
  tipo: string;
}

/**
 * Resposta de escudo (alinhado com backend EscudoResponse)
 */
export interface EscudoResponse {
  team_id: string;
  team_name: string;
  badge_url: string;
  source: string;
}
