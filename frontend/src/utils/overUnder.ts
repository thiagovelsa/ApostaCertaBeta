/**
 * Funções de cálculo de probabilidades Over/Under
 * Usa distribuições de Poisson (eventos discretos) e Normal (alta frequência)
 *
 * MELHORIAS IMPLEMENTADAS (v1.1):
 * - Sigma calculado corretamente via variância combinada independente
 * - Threshold dinâmico para seleção Poisson/Normal baseado em λ
 */

import jstat from 'jstat';
import type {
  PrevisaoPartida,
  EstatisticasTime,
  OverUnderLine,
  OverUnderStat,
  OverUnderPartida,
  DistributionType,
  ConfiancaLabel,
} from '@/types';
import type { IconName } from '@/components/atoms';

// ============================================================
// CONSTANTES DE CONFIGURAÇÃO
// ============================================================

/**
 * Linhas base para cada estatística
 * Estas são as linhas iniciais a partir das quais geramos as dinâmicas
 */
const BASE_LINES: Record<string, number[]> = {
  gols: [0.5, 1.5, 2.5, 3.5],
  escanteios: [7.5, 8.5, 9.5, 10.5],
  finalizacoes: [18.5, 20.5, 22.5, 24.5],
  finalizacoes_gol: [5.5, 6.5, 7.5, 8.5],
  cartoes_amarelos: [2.5, 3.5, 4.5, 5.5],
  faltas: [20.5, 22.5, 24.5, 26.5],
};

/**
 * Distribuição estatística PREFERIDA por tipo de estatística
 * - Poisson: eventos discretos de baixa/média frequência
 * - Normal: eventos de alta frequência (CLT)
 *
 * MELHORIA v1.1: Estas são preferências, mas a seleção final
 * é dinâmica baseada no λ (threshold = 7)
 */
const PREFERRED_DISTRIBUTIONS: Record<string, DistributionType> = {
  gols: 'poisson',
  escanteios: 'poisson',
  finalizacoes: 'normal',
  finalizacoes_gol: 'poisson',
  cartoes_amarelos: 'poisson',
  faltas: 'normal',
};

/**
 * Threshold de λ para usar Normal em vez de Poisson
 *
 * Quando λ > 7, a distribuição de Poisson converge para Normal
 * e usar Normal é mais preciso computacionalmente.
 */
const POISSON_NORMAL_THRESHOLD = 7;

/**
 * Seleciona a distribuição apropriada baseado no λ
 *
 * MELHORIA v1.1: Seleção dinâmica
 * - Se λ > 7: usa Normal (mesmo para stats que preferem Poisson)
 * - Senão: usa a distribuição preferida
 *
 * @param statKey - Chave da estatística
 * @param lambda - Valor esperado
 * @returns Tipo de distribuição a usar
 */
function selectDistribution(statKey: string, lambda: number): DistributionType {
  const preferred = PREFERRED_DISTRIBUTIONS[statKey] || 'poisson';

  // Se λ é alto, Poisson converge para Normal
  // Mais preciso usar Normal para λ > 7
  if (lambda > POISSON_NORMAL_THRESHOLD && preferred === 'poisson') {
    return 'normal';
  }

  return preferred;
}

/**
 * Ícones por estatística
 */
const ICONS: Record<string, IconName> = {
  gols: 'goal',
  escanteios: 'corner',
  finalizacoes: 'shot',
  finalizacoes_gol: 'target',
  cartoes_amarelos: 'card',
  faltas: 'foul',
};

/**
 * Labels por estatística
 */
const LABELS: Record<string, string> = {
  gols: 'Gols',
  escanteios: 'Escanteios',
  finalizacoes: 'Chutes',
  finalizacoes_gol: 'Chutes ao Gol',
  cartoes_amarelos: 'Cartões',
  faltas: 'Faltas',
};

/**
 * Limite de probabilidade para pular linha (≥98%)
 */
const PROBABILITY_CUTOFF = 0.98;

/**
 * Número máximo de linhas por estatística
 */
const MAX_LINES = 4;

// ============================================================
// FUNÇÕES DE CÁLCULO
// ============================================================

/**
 * Calcula P(X > n) usando Poisson ou Normal
 *
 * @param line - Linha (ex: 2.5)
 * @param lambda - Valor esperado (λ ou μ)
 * @param distribution - Tipo de distribuição
 * @param sigma - Desvio padrão (apenas para Normal)
 * @returns Probabilidade de Over (0-1)
 */
function calculateOverProbability(
  line: number,
  lambda: number,
  distribution: DistributionType,
  sigma: number | null
): number {
  // Proteção contra valores inválidos
  if (lambda <= 0) return 0.5;

  if (distribution === 'poisson') {
    // P(X > n) = 1 - P(X ≤ n) = 1 - CDF(floor(n))
    // Para linha 2.5, queremos P(X >= 3) = 1 - P(X <= 2)
    const n = Math.floor(line);
    const cdf = jstat.poisson.cdf(n, lambda);
    return 1 - cdf;
  } else {
    // Normal: P(X > n)
    if (sigma === null || sigma <= 0) {
      return 0.5; // Fallback
    }
    const cdf = jstat.normal.cdf(line, lambda, sigma);
    return 1 - cdf;
  }
}

/**
 * Parâmetros para cálculo de sigma combinado
 */
interface SigmaParams {
  mediaHome: number;
  mediaAway: number;
  cvHome: number;
  cvAway: number;
}

/**
 * Calcula sigma (desvio padrão) para distribuição Normal
 *
 * MELHORIA v1.1: Usa variância combinada correta (independente)
 *
 * Antes (incorreto):
 *   σ = CV_médio × λ_total
 *   Problema: assume correlação entre times
 *
 * Depois (correto):
 *   var_home = (CV_home × μ_home)²
 *   var_away = (CV_away × μ_away)²
 *   σ = √(var_home + var_away)
 *
 * @param params - Parâmetros com médias e CVs individuais
 * @returns Desvio padrão combinado
 */
function calculateSigmaCombined(params: SigmaParams): number {
  const { mediaHome, mediaAway, cvHome, cvAway } = params;

  // Limita CVs para evitar valores extremos
  const safeCvHome = Math.min(1.5, Math.max(0.1, cvHome));
  const safeCvAway = Math.min(1.5, Math.max(0.1, cvAway));

  // Calcula variância de cada time: var = (σ)² = (CV × μ)²
  const varHome = Math.pow(safeCvHome * mediaHome, 2);
  const varAway = Math.pow(safeCvAway * mediaAway, 2);

  // Variância combinada (eventos independentes): var_total = var_home + var_away
  const varTotal = varHome + varAway;

  // Sigma = raiz da variância
  const sigma = Math.sqrt(varTotal);

  // Sigma mínimo de 0.5 para evitar distribuições degeneradas
  return Math.max(0.5, sigma);
}


/**
 * Gera linhas dinâmicas com corte em ≥98%
 * Se uma linha tem probabilidade ≥98%, pula para a próxima
 *
 * @param lambda - Valor esperado
 * @param distribution - Tipo de distribuição
 * @param sigma - Desvio padrão (null para Poisson)
 * @param baseLines - Linhas base da estatística
 * @param maxLines - Número máximo de linhas
 * @returns Array de linhas Over/Under
 */
function generateDynamicLines(
  lambda: number,
  distribution: DistributionType,
  sigma: number | null,
  baseLines: number[],
  maxLines: number = MAX_LINES
): OverUnderLine[] {
  const lines: OverUnderLine[] = [];
  const increment = baseLines.length > 1 ? baseLines[1] - baseLines[0] : 1;
  const maxAttempts = baseLines.length * 6; // Limite de segurança

  let currentIndex = 0;

  while (lines.length < maxLines && currentIndex < maxAttempts) {
    // Calcula linha: base[i % len] + (floor(i / len) * len * increment)
    const baseIdx = currentIndex % baseLines.length;
    const multiplier = Math.floor(currentIndex / baseLines.length);
    const line = baseLines[baseIdx] + multiplier * baseLines.length * increment;

    const overProb = calculateOverProbability(line, lambda, distribution, sigma);
    const underProb = 1 - overProb;

    // Corte: se over ≥98% ou under ≥98%, pular linha
    if (overProb >= PROBABILITY_CUTOFF || underProb >= PROBABILITY_CUTOFF) {
      currentIndex++;
      continue;
    }

    lines.push({
      line,
      over: overProb,
      under: underProb,
    });

    currentIndex++;
  }

  // Se não conseguiu linhas suficientes, forçar pelo menos 1
  if (lines.length === 0 && baseLines.length > 0) {
    const midLine = baseLines[Math.floor(baseLines.length / 2)];
    const overProb = calculateOverProbability(midLine, lambda, distribution, sigma);
    lines.push({
      line: midLine,
      over: overProb,
      under: 1 - overProb,
    });
  }

  return lines;
}

/**
 * Calcula confiança baseada no CV médio e partidas analisadas
 *
 * @param cvMedio - CV médio dos times
 * @param partidasAnalisadas - Número de partidas analisadas
 * @returns Confiança (0-1)
 */
function calculateConfidence(cvMedio: number, partidasAnalisadas: number): number {
  let confianca = 1 - cvMedio;

  // Ajuste por tamanho da amostra
  if (partidasAnalisadas < 5) {
    confianca *= 0.8;
  } else if (partidasAnalisadas >= 15) {
    confianca *= 1.15;
  } else if (partidasAnalisadas >= 10) {
    confianca *= 1.1;
  }

  // Limita entre 30% e 95%
  return Math.max(0.30, Math.min(0.95, confianca));
}

/**
 * Retorna label de confiança
 */
function getConfiancaLabel(confianca: number): ConfiancaLabel {
  if (confianca >= 0.70) return 'Alta';
  if (confianca >= 0.50) return 'Média';
  return 'Baixa';
}

/**
 * Parâmetros para criar estatística Over/Under
 */
interface CreateOverUnderParams {
  statKey: string;
  lambdaTotal: number;
  mediaHome: number;
  mediaAway: number;
  cvHome: number;
  cvAway: number;
  partidasAnalisadas: number;
}

/**
 * Cria um OverUnderStat para uma estatística específica
 *
 * MELHORIA v1.1:
 * - Usa seleção dinâmica de distribuição baseada em λ
 * - Calcula sigma via variância combinada correta
 *
 * @param params - Parâmetros para cálculo
 * @returns OverUnderStat completo
 */
function createOverUnderStat(params: CreateOverUnderParams): OverUnderStat {
  const {
    statKey,
    lambdaTotal,
    mediaHome,
    mediaAway,
    cvHome,
    cvAway,
    partidasAnalisadas,
  } = params;

  const baseLines = BASE_LINES[statKey] || [0.5, 1.5, 2.5, 3.5];

  // Lambda seguro
  const safeLambda = Math.max(0.1, lambdaTotal);

  // MELHORIA v1.1: Seleção dinâmica de distribuição
  const distribution = selectDistribution(statKey, safeLambda);

  // CV médio dos times (para confiança)
  const cvMedio = (cvHome + cvAway) / 2;

  // MELHORIA v1.1: Calcula sigma via variância combinada correta
  let sigma: number | null = null;
  if (distribution === 'normal') {
    sigma = calculateSigmaCombined({
      mediaHome,
      mediaAway,
      cvHome,
      cvAway,
    });
  }

  // Gera linhas dinâmicas
  const lines = generateDynamicLines(
    safeLambda,
    distribution,
    sigma,
    baseLines,
    MAX_LINES
  );

  // Calcula confiança
  const confidence = calculateConfidence(cvMedio, partidasAnalisadas);
  const confidenceLabel = getConfiancaLabel(confidence);

  return {
    label: LABELS[statKey] || statKey,
    icon: ICONS[statKey] || 'stats',
    lambda: safeLambda,
    sigma,
    distribution,
    lines,
    confidence,
    confidenceLabel,
  };
}

// ============================================================
// FUNÇÃO PRINCIPAL EXPORTADA
// ============================================================

/**
 * Calcula todas as probabilidades Over/Under da partida
 *
 * MELHORIA v1.1:
 * - Passa médias individuais para cálculo correto de sigma
 * - Usa seleção dinâmica de distribuição
 *
 * @param previsoes - Previsões calculadas (de calcularPrevisoes)
 * @param mandanteStats - Estatísticas do mandante
 * @param visitanteStats - Estatísticas do visitante
 * @param partidasAnalisadas - Número de partidas analisadas
 * @returns OverUnderPartida com probabilidades para todas as estatísticas
 */
export function calcularOverUnder(
  previsoes: PrevisaoPartida,
  mandanteStats: EstatisticasTime,
  visitanteStats: EstatisticasTime,
  partidasAnalisadas: number
): OverUnderPartida {
  return {
    gols: createOverUnderStat({
      statKey: 'gols',
      lambdaTotal: previsoes.gols.total.valor,
      mediaHome: previsoes.gols.home.valor,
      mediaAway: previsoes.gols.away.valor,
      cvHome: mandanteStats.gols.feitos.cv,
      cvAway: visitanteStats.gols.feitos.cv,
      partidasAnalisadas,
    }),
    escanteios: createOverUnderStat({
      statKey: 'escanteios',
      lambdaTotal: previsoes.escanteios.total.valor,
      mediaHome: previsoes.escanteios.home.valor,
      mediaAway: previsoes.escanteios.away.valor,
      cvHome: mandanteStats.escanteios.feitos.cv,
      cvAway: visitanteStats.escanteios.feitos.cv,
      partidasAnalisadas,
    }),
    finalizacoes: createOverUnderStat({
      statKey: 'finalizacoes',
      lambdaTotal: previsoes.finalizacoes.total.valor,
      mediaHome: previsoes.finalizacoes.home.valor,
      mediaAway: previsoes.finalizacoes.away.valor,
      cvHome: mandanteStats.finalizacoes.feitos.cv,
      cvAway: visitanteStats.finalizacoes.feitos.cv,
      partidasAnalisadas,
    }),
    finalizacoes_gol: createOverUnderStat({
      statKey: 'finalizacoes_gol',
      lambdaTotal: previsoes.finalizacoes_gol.total.valor,
      mediaHome: previsoes.finalizacoes_gol.home.valor,
      mediaAway: previsoes.finalizacoes_gol.away.valor,
      cvHome: mandanteStats.finalizacoes_gol.feitos.cv,
      cvAway: visitanteStats.finalizacoes_gol.feitos.cv,
      partidasAnalisadas,
    }),
    cartoes_amarelos: createOverUnderStat({
      statKey: 'cartoes_amarelos',
      lambdaTotal: previsoes.cartoes_amarelos.total.valor,
      mediaHome: previsoes.cartoes_amarelos.home.valor,
      mediaAway: previsoes.cartoes_amarelos.away.valor,
      cvHome: mandanteStats.cartoes_amarelos.cv,
      cvAway: visitanteStats.cartoes_amarelos.cv,
      partidasAnalisadas,
    }),
    faltas: createOverUnderStat({
      statKey: 'faltas',
      lambdaTotal: previsoes.faltas.total.valor,
      mediaHome: previsoes.faltas.home.valor,
      mediaAway: previsoes.faltas.away.valor,
      cvHome: mandanteStats.faltas.cv,
      cvAway: visitanteStats.faltas.cv,
      partidasAnalisadas,
    }),
  };
}
