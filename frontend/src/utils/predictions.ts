/**
 * Funções de cálculo de previsões para estatísticas de partida
 * Usa abordagem Poisson-like combinando força ofensiva + fraqueza defensiva
 */

import type {
  EstatisticaMetrica,
  EstatisticaFeitos,
  EstatisticasTime,
  PrevisaoEstatistica,
  PrevisaoValor,
  PrevisaoPartida,
  ConfiancaLabel,
} from '@/types';

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
 */
export function calcularPrevisaoFeitos(
  homeStats: EstatisticaFeitos,
  awayStats: EstatisticaFeitos,
  partidasAnalisadas: number
): PrevisaoEstatistica {
  // PREVISÃO MANDANTE
  // Fatores: mandante.feitos + visitante.sofridos
  const lambdaHome = (homeStats.feitos.media + awayStats.sofridos.media) / 2;
  const cvHome = (homeStats.feitos.cv + awayStats.sofridos.cv) / 2;
  const confiancaHome = calcularConfianca(cvHome, partidasAnalisadas);

  // PREVISÃO VISITANTE
  // Fatores: visitante.feitos + mandante.sofridos
  const lambdaAway = (awayStats.feitos.media + homeStats.sofridos.media) / 2;
  const cvAway = (awayStats.feitos.cv + homeStats.sofridos.cv) / 2;
  const confiancaAway = calcularConfianca(cvAway, partidasAnalisadas);

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
 */
export function calcularPrevisaoSimples(
  home: EstatisticaMetrica,
  away: EstatisticaMetrica,
  partidasAnalisadas: number
): PrevisaoEstatistica {
  const confiancaHome = calcularConfianca(home.cv, partidasAnalisadas);
  const confiancaAway = calcularConfianca(away.cv, partidasAnalisadas);

  const cvTotal = (home.cv + away.cv) / 2;
  const confiancaTotal = calcularConfianca(cvTotal, partidasAnalisadas);

  return {
    home: criarPrevisaoValor(home.media, confiancaHome),
    away: criarPrevisaoValor(away.media, confiancaAway),
    total: criarPrevisaoValor(home.media + away.media, confiancaTotal),
  };
}

/**
 * Calcula todas as previsões da partida
 */
export function calcularPrevisoes(
  mandante: { estatisticas: EstatisticasTime },
  visitante: { estatisticas: EstatisticasTime },
  partidasAnalisadas: number
): PrevisaoPartida {
  const { estatisticas: homeStats } = mandante;
  const { estatisticas: awayStats } = visitante;

  return {
    gols: calcularPrevisaoFeitos(
      homeStats.gols,
      awayStats.gols,
      partidasAnalisadas
    ),
    escanteios: calcularPrevisaoFeitos(
      homeStats.escanteios,
      awayStats.escanteios,
      partidasAnalisadas
    ),
    finalizacoes: calcularPrevisaoFeitos(
      homeStats.finalizacoes,
      awayStats.finalizacoes,
      partidasAnalisadas
    ),
    finalizacoes_gol: calcularPrevisaoFeitos(
      homeStats.finalizacoes_gol,
      awayStats.finalizacoes_gol,
      partidasAnalisadas
    ),
    cartoes_amarelos: calcularPrevisaoSimples(
      homeStats.cartoes_amarelos,
      awayStats.cartoes_amarelos,
      partidasAnalisadas
    ),
    faltas: calcularPrevisaoSimples(
      homeStats.faltas,
      awayStats.faltas,
      partidasAnalisadas
    ),
  };
}
