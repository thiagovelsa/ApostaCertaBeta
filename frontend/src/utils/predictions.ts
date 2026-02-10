/**
 * Funções de cálculo de previsões para estatísticas de partida
 * Usa abordagem Poisson-like combinando força ofensiva + fraqueza defensiva
 *
 * MELHORIAS IMPLEMENTADAS (v1.1):
 * - Ajuste de vantagem de mando (home-field advantage)
 * - Fatores baseados em estudos estatísticos de futebol
 */

import type {
  EstatisticaMetrica,
  EstatisticaFeitos,
  EstatisticasTime,
  PrevisaoEstatistica,
  PrevisaoValor,
  PrevisaoPartida,
  ConfiancaLabel,
  MandoFilter,
} from '@/types';

// ============================================================
// CONSTANTES DE AJUSTE DE MANDO
// ============================================================

/**
 * Fator de vantagem de jogar em casa (home-field advantage)
 *
 * Baseado em estudos estatísticos:
 * - Times marcam em média 35-40% mais gols em casa
 * - Dividido: 15-20% pelo efeito de jogar em casa, 15-20% pelo efeito visitante
 *
 * Usamos fatores conservadores de 8% para evitar over-adjustment:
 * - HOME_BOOST: multiplicador para o mandante (1.08 = +8%)
 * - AWAY_PENALTY: multiplicador para o visitante (0.92 = -8%)
 *
 * NOTA: Estes fatores só são aplicados quando os filtros de mando
 * NÃO estão definidos. Se o usuário usar home_mando="casa" e
 * away_mando="fora", os dados já refletem o contexto correto.
 */
const HOME_BOOST = 1.08;
const AWAY_PENALTY = 0.92;

/**
 * Fatores de ajuste por tipo de estatística
 * Algumas estatísticas são mais influenciadas pelo mando que outras
 */
const STAT_HOME_FACTORS: Record<string, { home: number; away: number }> = {
  gols: { home: 1.08, away: 0.92 },           // Gols: efeito significativo
  escanteios: { home: 1.05, away: 0.97 },     // Escanteios: efeito moderado
  finalizacoes: { home: 1.06, away: 0.95 },   // Chutes: efeito moderado
  finalizacoes_gol: { home: 1.06, away: 0.95 },
  cartoes_amarelos: { home: 0.95, away: 1.08 }, // Cartões: visitantes levam mais
  faltas: { home: 0.96, away: 1.05 },         // Faltas: visitantes cometem mais
};

/**
 * Arredonda para 1 casa decimal
 */
function round(value: number): number {
  return Math.round(value * 10) / 10;
}

/**
 * Retorna o label de confiança baseado no valor
 */
function getConfiancaLabel(confianca: number): ConfiancaLabel {
  if (confianca >= 0.70) return 'Alta';
  if (confianca >= 0.50) return 'Média';
  return 'Baixa';
}

/**
 * Calcula a confiança baseada no CV e tamanho da amostra
 * Quanto menor o CV, maior a confiança
 */
function calcularConfianca(cv: number, partidasAnalisadas: number): number {
  let confianca = 1 - cv;

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
 * Cria um objeto PrevisaoValor
 */
function criarPrevisaoValor(valor: number, confianca: number): PrevisaoValor {
  return {
    valor: round(valor),
    confianca,
    confiancaLabel: getConfiancaLabel(confianca),
  };
}

/**
 * Contexto de mando para ajuste de previsões
 */
interface MandoContext {
  homeMando: MandoFilter;
  awayMando: MandoFilter;
}

/**
 * Verifica se deve aplicar ajuste de mando
 *
 * NÃO aplica ajuste quando:
 * - homeMando="casa" E awayMando="fora" (dados já refletem contexto)
 * - Ambos filtros estão definidos explicitamente
 *
 * APLICA ajuste quando:
 * - Filtros de mando não estão definidos (null)
 * - Usando dados gerais que precisam de correção estatística
 */
function shouldApplyMandoAdjustment(context?: MandoContext): boolean {
  if (!context) return true; // Sem contexto = usar ajuste

  const { homeMando, awayMando } = context;

  // Se ambos estão com mando "ideal", não ajusta
  if (homeMando === 'casa' && awayMando === 'fora') {
    return false;
  }

  // Se nenhum está definido, aplica ajuste
  if (homeMando === null && awayMando === null) {
    return true;
  }

  // Casos mistos: aplica ajuste parcial (retorna true para simplificar)
  return true;
}

/**
 * Calcula 3 previsões para estatísticas com feitos/sofridos
 *
 * PREVISÃO MANDANTE:
 *   λ_home = (mandante.feitos.media + visitante.sofridos.media) / 2
 *   cv_home = (mandante.feitos.cv + visitante.sofridos.cv) / 2
 *
 * PREVISÃO VISITANTE:
 *   λ_away = (visitante.feitos.media + mandante.sofridos.media) / 2
 *   cv_away = (visitante.feitos.cv + mandante.sofridos.cv) / 2
 *
 * PREVISÃO TOTAL:
 *   λ_total = λ_home + λ_away
 *
 * MELHORIA v1.1: Ajuste de mando
 *   Quando filtros de mando não estão definidos, aplica correção
 *   estatística baseada em home-field advantage.
 *
 * @param homeStats - Estatísticas do mandante
 * @param awayStats - Estatísticas do visitante
 * @param partidasAnalisadas - Número de partidas na amostra
 * @param statKey - Chave da estatística (para fator de ajuste específico)
 * @param mandoContext - Contexto de filtros de mando (opcional)
 */
export function calcularPrevisaoFeitos(
  homeStats: EstatisticaFeitos,
  awayStats: EstatisticaFeitos,
  partidasAnalisadas: number,
  statKey?: string,
  mandoContext?: MandoContext
): PrevisaoEstatistica {
  // Determina se deve aplicar ajuste de mando
  const applyMandoAdjustment = shouldApplyMandoAdjustment(mandoContext);

  // Obtém fatores de ajuste para esta estatística
  const factors = statKey && STAT_HOME_FACTORS[statKey]
    ? STAT_HOME_FACTORS[statKey]
    : { home: HOME_BOOST, away: AWAY_PENALTY };

  // PREVISÃO MANDANTE
  // Fatores: mandante.feitos + visitante.sofridos
  let lambdaHome = (homeStats.feitos.media + awayStats.sofridos.media) / 2;
  const cvHome = (homeStats.feitos.cv + awayStats.sofridos.cv) / 2;
  const confiancaHome = calcularConfianca(cvHome, partidasAnalisadas);

  // PREVISÃO VISITANTE
  // Fatores: visitante.feitos + mandante.sofridos
  let lambdaAway = (awayStats.feitos.media + homeStats.sofridos.media) / 2;
  const cvAway = (awayStats.feitos.cv + homeStats.sofridos.cv) / 2;
  const confiancaAway = calcularConfianca(cvAway, partidasAnalisadas);

  // Aplica ajuste de mando se necessário
  if (applyMandoAdjustment) {
    lambdaHome *= factors.home;
    lambdaAway *= factors.away;
  }

  // PREVISÃO TOTAL
  const lambdaTotal = lambdaHome + lambdaAway;
  const cvTotal = (cvHome + cvAway) / 2;
  const confiancaTotal = calcularConfianca(cvTotal, partidasAnalisadas);

  return {
    home: criarPrevisaoValor(lambdaHome, confiancaHome),
    away: criarPrevisaoValor(lambdaAway, confiancaAway),
    total: criarPrevisaoValor(lambdaTotal, confiancaTotal),
  };
}

/**
 * Calcula 3 previsões para métricas simples (cartões, faltas)
 * Usa a média diretamente de cada time
 *
 * MELHORIA v1.1: Ajuste de mando para cartões e faltas
 *   Visitantes historicamente cometem mais faltas e recebem mais cartões.
 *
 * @param home - Estatística do mandante
 * @param away - Estatística do visitante
 * @param partidasAnalisadas - Número de partidas na amostra
 * @param statKey - Chave da estatística (para fator de ajuste específico)
 * @param mandoContext - Contexto de filtros de mando (opcional)
 */
export function calcularPrevisaoSimples(
  home: EstatisticaMetrica,
  away: EstatisticaMetrica,
  partidasAnalisadas: number,
  statKey?: string,
  mandoContext?: MandoContext
): PrevisaoEstatistica {
  // Determina se deve aplicar ajuste de mando
  const applyMandoAdjustment = shouldApplyMandoAdjustment(mandoContext);

  // Obtém fatores de ajuste para esta estatística
  const factors = statKey && STAT_HOME_FACTORS[statKey]
    ? STAT_HOME_FACTORS[statKey]
    : { home: 1.0, away: 1.0 }; // Default: sem ajuste

  const confiancaHome = calcularConfianca(home.cv, partidasAnalisadas);
  const confiancaAway = calcularConfianca(away.cv, partidasAnalisadas);

  let mediaHome = home.media;
  let mediaAway = away.media;

  // Aplica ajuste de mando se necessário
  if (applyMandoAdjustment) {
    mediaHome *= factors.home;
    mediaAway *= factors.away;
  }

  const cvTotal = (home.cv + away.cv) / 2;
  const confiancaTotal = calcularConfianca(cvTotal, partidasAnalisadas);

  return {
    home: criarPrevisaoValor(mediaHome, confiancaHome),
    away: criarPrevisaoValor(mediaAway, confiancaAway),
    total: criarPrevisaoValor(mediaHome + mediaAway, confiancaTotal),
  };
}

/**
 * Calcula todas as previsões da partida
 *
 * MELHORIA v1.1: Aceita contexto de mando para ajuste automático
 *
 * @param mandante - Time mandante com estatísticas
 * @param visitante - Time visitante com estatísticas
 * @param partidasAnalisadas - Número de partidas na amostra
 * @param homeMando - Filtro de mando do mandante (null = sem filtro)
 * @param awayMando - Filtro de mando do visitante (null = sem filtro)
 */
export function calcularPrevisoes(
  mandante: { estatisticas: EstatisticasTime },
  visitante: { estatisticas: EstatisticasTime },
  partidasAnalisadas: number,
  homeMando: MandoFilter = null,
  awayMando: MandoFilter = null
): PrevisaoPartida {
  const { estatisticas: homeStats } = mandante;
  const { estatisticas: awayStats } = visitante;

  // Contexto de mando para ajuste de previsões
  const mandoContext: MandoContext = { homeMando, awayMando };

  return {
    gols: calcularPrevisaoFeitos(
      homeStats.gols,
      awayStats.gols,
      partidasAnalisadas,
      'gols',
      mandoContext
    ),
    escanteios: calcularPrevisaoFeitos(
      homeStats.escanteios,
      awayStats.escanteios,
      partidasAnalisadas,
      'escanteios',
      mandoContext
    ),
    finalizacoes: calcularPrevisaoFeitos(
      homeStats.finalizacoes,
      awayStats.finalizacoes,
      partidasAnalisadas,
      'finalizacoes',
      mandoContext
    ),
    finalizacoes_gol: calcularPrevisaoFeitos(
      homeStats.finalizacoes_gol,
      awayStats.finalizacoes_gol,
      partidasAnalisadas,
      'finalizacoes_gol',
      mandoContext
    ),
    cartoes_amarelos: calcularPrevisaoSimples(
      homeStats.cartoes_amarelos,
      awayStats.cartoes_amarelos,
      partidasAnalisadas,
      'cartoes_amarelos',
      mandoContext
    ),
    faltas: calcularPrevisaoSimples(
      homeStats.faltas,
      awayStats.faltas,
      partidasAnalisadas,
      'faltas',
      mandoContext
    ),
  };
}
