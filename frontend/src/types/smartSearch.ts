/**
 * Tipos para a funcionalidade de Busca Inteligente
 * Análise automática de oportunidades de aposta
 */

import type { ConfiancaLabel } from './stats';

/**
 * Informação resumida de um time para exibição
 */
export interface TimeResumo {
  id: string;
  nome: string;
  escudo?: string | null;
}

/**
 * Uma oportunidade de aposta identificada pela análise
 */
export interface Oportunidade {
  /** ID único da partida */
  matchId: string;
  /** Informações do time mandante */
  mandante: TimeResumo;
  /** Informações do time visitante */
  visitante: TimeResumo;
  /** Nome da competição */
  competicao: string;
  /** Horário da partida (HH:mm) */
  horario: string;
  /** Estatística analisada: gols, escanteios, finalizacoes, etc. */
  estatistica: string;
  /** Label legível da estatística */
  estatisticaLabel: string;
  /** Tipo da aposta */
  tipo: 'over' | 'under';
  /** Linha da aposta (ex: 2.5) */
  linha: number;
  /** Probabilidade calculada (0-1) */
  probabilidade: number;
  /** Confiança da previsão (0-1) */
  confianca: number;
  /** Label de confiança */
  confiancaLabel: ConfiancaLabel;
  /** Score de ranqueamento (confiança × probabilidade) */
  score: number;
}

/**
 * Resultado completo da busca inteligente
 */
export interface SmartSearchResult {
  /** Número de partidas analisadas */
  partidas_analisadas: number;
  /** Número de partidas com pelo menos uma oportunidade */
  partidas_com_oportunidades: number;
  /** Total de oportunidades encontradas */
  total_oportunidades: number;
  /** Lista de oportunidades ordenadas por score */
  oportunidades: Oportunidade[];
  /** Timestamp da análise */
  timestamp: string;
}

/**
 * Estado de progresso da busca inteligente
 */
export interface SmartSearchProgress {
  /** Total de partidas a analisar */
  total: number;
  /** Partidas já analisadas */
  analisadas: number;
  /** Porcentagem de progresso (0-100) */
  porcentagem: number;
  /** Partida atual sendo analisada */
  atual?: string;
}

/**
 * Thresholds de probabilidade por estatística
 */
export interface StatThresholds {
  overMin: number;
  underMin: number;
  confiancaMin: number;
}

/**
 * Configuração padrão de thresholds para todas as estatísticas
 * Use DEFAULT_STAT_THRESHOLDS do settingsStore para valores atualizáveis
 */
export const DEFAULT_STAT_THRESHOLDS: Record<string, StatThresholds> = {
  gols: { overMin: 0.60, underMin: 0.65, confiancaMin: 0.70 },
  escanteios: { overMin: 0.65, underMin: 0.65, confiancaMin: 0.70 },
  finalizacoes: { overMin: 0.65, underMin: 0.65, confiancaMin: 0.70 },
  finalizacoes_gol: { overMin: 0.65, underMin: 0.65, confiancaMin: 0.70 },
  cartoes_amarelos: { overMin: 0.60, underMin: 0.65, confiancaMin: 0.70 },
  faltas: { overMin: 0.65, underMin: 0.65, confiancaMin: 0.70 },
};

/**
 * @deprecated Use DEFAULT_STAT_THRESHOLDS e o settingsStore para thresholds configuráveis
 */
export const STAT_THRESHOLDS = DEFAULT_STAT_THRESHOLDS;

/**
 * Labels legíveis para cada estatística
 */
export const STAT_LABELS: Record<string, string> = {
  gols: 'Gols',
  escanteios: 'Escanteios',
  finalizacoes: 'Chutes',
  finalizacoes_gol: 'Chutes ao Gol',
  cartoes_amarelos: 'Cartões',
  faltas: 'Faltas',
};
