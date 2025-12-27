/**
 * Funções de cálculo de probabilidades Over/Under
 * Usa distribuições de Poisson (eventos discretos) e Normal (alta frequência)
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
 * Distribuição estatística por tipo de estatística
 * - Poisson: eventos discretos de baixa/média frequência
 * - Normal: eventos de alta frequência (CLT)
 */
const DISTRIBUTIONS: Record<string, DistributionType> = {
  gols: 'poisson',
  escanteios: 'poisson',
  finalizacoes: 'normal',
  finalizacoes_gol: 'poisson',
  cartoes_amarelos: 'poisson',
  faltas: 'normal',
};

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
  finalizacoes: 'Finalizações',
  finalizacoes_gol: 'Fin. no Gol',
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
 * Calcula sigma (desvio padrão) para distribuição Normal
 * Baseado no CV médio dos times
 *
 * @param lambda - Valor esperado
 * @param cv - Coeficiente de Variação médio
 * @returns Desvio padrão
 */
function calculateSigma(lambda: number, cv: number): number {
  // σ = CV * μ
  // Com limites de segurança
  const safeCv = Math.min(1.5, Math.max(0.1, cv));
  const sigma = safeCv * lambda;
  return Math.max(0.5, sigma); // Sigma mínimo de 0.5
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
 * Cria um OverUnderStat para uma estatística específica
 *
 * @param statKey - Chave da estatística (gols, escanteios, etc.)
 * @param lambda - Valor esperado (do PrevisaoPartida.total.valor)
 * @param cvHome - CV do mandante
 * @param cvAway - CV do visitante
 * @param partidasAnalisadas - Número de partidas
 * @returns OverUnderStat completo
 */
function createOverUnderStat(
  statKey: string,
  lambda: number,
  cvHome: number,
  cvAway: number,
  partidasAnalisadas: number
): OverUnderStat {
  const distribution = DISTRIBUTIONS[statKey] || 'poisson';
  const baseLines = BASE_LINES[statKey] || [0.5, 1.5, 2.5, 3.5];

  // CV médio dos times
  const cvMedio = (cvHome + cvAway) / 2;

  // Lambda seguro
  const safeLambda = Math.max(0.1, lambda);

  // Calcula sigma para distribuições normais
  const sigma = distribution === 'normal' ? calculateSigma(safeLambda, cvMedio) : null;

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
    gols: createOverUnderStat(
      'gols',
      previsoes.gols.total.valor,
      mandanteStats.gols.feitos.cv,
      visitanteStats.gols.feitos.cv,
      partidasAnalisadas
    ),
    escanteios: createOverUnderStat(
      'escanteios',
      previsoes.escanteios.total.valor,
      mandanteStats.escanteios.feitos.cv,
      visitanteStats.escanteios.feitos.cv,
      partidasAnalisadas
    ),
    finalizacoes: createOverUnderStat(
      'finalizacoes',
      previsoes.finalizacoes.total.valor,
      mandanteStats.finalizacoes.feitos.cv,
      visitanteStats.finalizacoes.feitos.cv,
      partidasAnalisadas
    ),
    finalizacoes_gol: createOverUnderStat(
      'finalizacoes_gol',
      previsoes.finalizacoes_gol.total.valor,
      mandanteStats.finalizacoes_gol.feitos.cv,
      visitanteStats.finalizacoes_gol.feitos.cv,
      partidasAnalisadas
    ),
    cartoes_amarelos: createOverUnderStat(
      'cartoes_amarelos',
      previsoes.cartoes_amarelos.total.valor,
      mandanteStats.cartoes_amarelos.cv,
      visitanteStats.cartoes_amarelos.cv,
      partidasAnalisadas
    ),
    faltas: createOverUnderStat(
      'faltas',
      previsoes.faltas.total.valor,
      mandanteStats.faltas.cv,
      visitanteStats.faltas.cv,
      partidasAnalisadas
    ),
  };
}
