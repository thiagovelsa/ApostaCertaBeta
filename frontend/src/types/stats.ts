/**
 * Classificação do Coeficiente de Variação (calibrado por estatística)
 * Thresholds variam por tipo de estatística (gols, escanteios, etc)
 */
export type CVClassificacao =
  | 'Muito Estável'
  | 'Estável'
  | 'Moderado'
  | 'Instável'
  | 'Muito Instável'
  | 'N/A';

/**
 * Label de estabilidade simplificado (3 categorias)
 * Usado para visualização mais intuitiva
 */
export type EstabilidadeLabel = 'Alta' | 'Média' | 'Baixa' | 'N/A';

/**
 * Converte classificação CV para EstabilidadeLabel simplificado
 */
export function toEstabilidadeLabel(classificacao: CVClassificacao): EstabilidadeLabel {
  switch (classificacao) {
    case 'Muito Estável':
    case 'Estável':
      return 'Alta';
    case 'Moderado':
      return 'Média';
    case 'Instável':
    case 'Muito Instável':
      return 'Baixa';
    default:
      return 'N/A';
  }
}

/**
 * Métrica estatística individual (alinhado com backend EstatisticaMetrica)
 */
export interface EstatisticaMetrica {
  media: number;
  cv: number;
  classificacao: CVClassificacao;
  estabilidade: number; // 0-100%, onde 100% = muito estável
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
  faltas: EstatisticaMetrica;
  // cartoes_vermelhos removido - evento muito raro para análise de CV
}

/**
 * Resultado de uma partida (W=Win, D=Draw, L=Loss)
 */
export type FormResult = 'W' | 'D' | 'L';

/**
 * Time com suas estatísticas (alinhado com backend TimeComEstatisticas)
 */
export interface TimeComEstatisticas {
  id: string;
  nome: string;
  escudo?: string | null;
  estatisticas: EstatisticasTime;
  recent_form?: FormResult[];
}

/**
 * Filtro de período para estatísticas
 */
export type FiltroEstatisticas = 'geral' | '5' | '10';

/**
 * Subfiltro de mando (casa/fora)
 * null = sem subfiltro (usa todos os jogos)
 */
export type MandoFilter = 'casa' | 'fora' | null;

/**
 * Subfiltro de período (tempo do jogo)
 * integral = jogo completo (90 min)
 * 1T = primeiro tempo (0-45 min)
 * 2T = segundo tempo (45-90 min)
 */
export type PeriodoFilter = 'integral' | '1T' | '2T';

/**
 * Informações do árbitro da partida (alinhado com backend ArbitroInfo)
 */
export interface ArbitroInfo {
  id: string;
  nome: string;
  partidas: number;  // Partidas na competição específica
  partidas_temporada: number;  // Total na temporada (todas competições)
  media_cartoes_amarelos: number;  // Média na competição
  media_cartoes_temporada: number;  // Média ponderada na temporada
  media_faltas?: number | null;
}

/**
 * Contexto pré-jogo (derivado de schedule/standings/match preview)
 */
export interface H2HInfo {
  total_matches: number;
  avg_goals_per_match: number;
  home_wins?: number;
  away_wins?: number;
  draws?: number;
}

export interface ClassificacaoTimeInfo {
  posicao: number;
  pontos: number;
  jogos: number;
  saldo_gols?: number | null;
}

export interface ContextoTime {
  dias_descanso?: number | null;
  jogos_7d?: number | null;
  jogos_14d?: number | null;
  posicao?: number | null;
}

export interface ContextoPartida {
  mandante: ContextoTime;
  visitante: ContextoTime;
  classificacao_mandante?: ClassificacaoTimeInfo | null;
  classificacao_visitante?: ClassificacaoTimeInfo | null;
  h2h_all_comps?: H2HInfo | null;
  fase?: string | null;
  ajustes_aplicados?: string[];
}

// ============================================================
// DEBUG / TRANSPARENCIA (debug=1)
// ============================================================

export type DebugSampleSource = 'matches' | 'seasonstats_fallback';

export interface DebugAmostraTime {
  source: DebugSampleSource;
  limit: number;
  periodo: PeriodoFilter;
  mando: MandoFilter;
  n_used: number;
  match_ids: string[];
  match_dates: Array<string | null>;
  weights: number[];
  reason?: string | null;
}

export interface DebugAmostra {
  mandante: DebugAmostraTime;
  visitante: DebugAmostraTime;
}

/**
 * Resposta completa de estatísticas (alinhado com backend StatsResponse)
 */
export interface StatsResponse {
  partida: import('./partida').PartidaResumo;
  filtro_aplicado: FiltroEstatisticas;
  partidas_analisadas: number;
  partidas_analisadas_mandante?: number | null;
  partidas_analisadas_visitante?: number | null;
  mandante: TimeComEstatisticas;
  visitante: TimeComEstatisticas;
  arbitro?: ArbitroInfo | null;
  contexto?: ContextoPartida | null;
  h2h_all_comps?: H2HInfo | null;
  debug_amostra?: DebugAmostra | null;
  previsoes?: PrevisaoPartida;
  over_under?: OverUnderPartida;
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
  escudo_url: string | null;
  fonte: string;
}

// ============================================================
// TIPOS DE PREVISÃO
// ============================================================

/**
 * Label de confiança para previsões
 */
export type ConfiancaLabel = 'Baixa' | 'Média' | 'Alta';

/**
 * Previsão individual com valor e confiança
 */
export interface PrevisaoValor {
  valor: number;
  confianca: number;
  confiancaLabel: ConfiancaLabel;
}

/**
 * 3 previsões separadas para cada estatística
 * - home: previsão do mandante (feitos_casa + sofridos_fora)
 * - away: previsão do visitante (feitos_fora + sofridos_casa)
 * - total: soma das duas previsões
 */
export interface PrevisaoEstatistica {
  home: PrevisaoValor;
  away: PrevisaoValor;
  total: PrevisaoValor;
}

/**
 * Todas as previsões da partida
 */
export interface PrevisaoPartida {
  gols: PrevisaoEstatistica;
  escanteios: PrevisaoEstatistica;
  finalizacoes: PrevisaoEstatistica;
  finalizacoes_gol: PrevisaoEstatistica;
  cartoes_amarelos: PrevisaoEstatistica;
  faltas: PrevisaoEstatistica;
}

// ============================================================
// TIPOS DE OVER/UNDER
// ============================================================

import type { IconName } from '@/components/atoms';

/**
 * Tipo de distribuição estatística
 */
export type DistributionType = 'poisson' | 'normal' | 'negbin';

/**
 * Linha individual de probabilidade Over/Under
 */
export interface OverUnderLine {
  line: number;   // Ex: 2.5
  over: number;   // Probabilidade 0-1
  under: number;  // Probabilidade 0-1
  ci_lower?: number | null;
  ci_upper?: number | null;
  uncertainty?: number | null;
}

/**
 * Probabilidades Over/Under para uma estatística
 */
export interface OverUnderStat {
  label: string;
  icon: IconName;
  lambda: number;           // Valor esperado (média)
  lambdaHome?: number;
  lambdaAway?: number;
  // Intervalo de previsao para contagem total (mu), usado para Min/Max na UI.
  predMin: number;
  predMax: number;
  intervalLevel: number;    // ex: 0.9
  sigma: number | null;     // Desvio padrão (null para Poisson)
  distribution: DistributionType;
  lines: OverUnderLine[];   // 3-4 linhas dinâmicas
  confidence: number;       // 0-1
  confidenceLabel: ConfiancaLabel;
}

/**
 * Todas as probabilidades Over/Under da partida
 */
export interface OverUnderPartida {
  gols: OverUnderStat;
  escanteios: OverUnderStat;
  finalizacoes: OverUnderStat;
  finalizacoes_gol: OverUnderStat;
  cartoes_amarelos: OverUnderStat;
  faltas: OverUnderStat;
}
