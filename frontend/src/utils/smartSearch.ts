/**
 * Funções de análise para Busca Inteligente
 * Identifica e ranqueia oportunidades de aposta
 */

import type {
  Oportunidade,
  SmartSearchResult,
  TimeResumo,
} from '@/types/smartSearch';
import { STAT_THRESHOLDS, STAT_LABELS } from '@/types/smartSearch';
import type { StatsResponse, OverUnderPartida, OverUnderStat } from '@/types';
import type { PartidaResumo } from '@/types/partida';

/**
 * Limite de probabilidade para descartar linhas óbvias
 */
const PROBABILITY_CUTOFF = 0.98;

/**
 * Edge mínimo (diferença entre over e under)
 */
const MIN_EDGE = 0.30;

/**
 * Número máximo de oportunidades a exibir
 */
export const MAX_OPPORTUNITIES = 999;

/**
 * Analisa uma estatística específica e retorna oportunidades válidas
 */
function analisarEstatistica(
  statKey: string,
  stat: OverUnderStat,
  matchId: string,
  mandante: TimeResumo,
  visitante: TimeResumo,
  competicao: string,
  horario: string
): Oportunidade[] {
  const oportunidades: Oportunidade[] = [];
  const thresholds = STAT_THRESHOLDS[statKey];

  if (!thresholds) return oportunidades;

  // Verifica se a confiança é suficiente (Alta = ≥70%)
  if (stat.confidence < thresholds.confiancaMin) {
    return oportunidades;
  }

  // Analisa cada linha
  for (const line of stat.lines) {
    // Pula linhas muito óbvias
    if (line.over >= PROBABILITY_CUTOFF || line.under >= PROBABILITY_CUTOFF) {
      continue;
    }

    // Verifica edge mínimo
    const edge = Math.abs(line.over - line.under);
    if (edge < MIN_EDGE) {
      continue;
    }

    // Verifica Over
    if (line.over >= thresholds.overMin) {
      const score = stat.confidence * line.over;
      oportunidades.push({
        matchId,
        mandante,
        visitante,
        competicao,
        horario,
        estatistica: statKey,
        estatisticaLabel: STAT_LABELS[statKey] || statKey,
        tipo: 'over',
        linha: line.line,
        probabilidade: line.over,
        confianca: stat.confidence,
        confiancaLabel: stat.confidenceLabel,
        score,
      });
    }

    // Verifica Under
    if (line.under >= thresholds.underMin) {
      const score = stat.confidence * line.under;
      oportunidades.push({
        matchId,
        mandante,
        visitante,
        competicao,
        horario,
        estatistica: statKey,
        estatisticaLabel: STAT_LABELS[statKey] || statKey,
        tipo: 'under',
        linha: line.line,
        probabilidade: line.under,
        confianca: stat.confidence,
        confiancaLabel: stat.confidenceLabel,
        score,
      });
    }
  }

  return oportunidades;
}

/**
 * Formata horário da partida
 * Recebe formato HH:MM:SS e retorna HH:MM
 */
function formatarHorario(horario: string | undefined): string {
  if (!horario) return '--:--';

  // Se já está no formato HH:MM ou HH:MM:SS, extrai apenas HH:MM
  const match = horario.match(/^(\d{2}):(\d{2})/);
  if (match) {
    return `${match[1]}:${match[2]}`;
  }

  return '--:--';
}

/**
 * Analisa uma partida completa e retorna todas as oportunidades
 */
export function analisarPartida(
  partida: PartidaResumo,
  stats: StatsResponse,
  overUnder: OverUnderPartida
): Oportunidade[] {
  const oportunidades: Oportunidade[] = [];

  const mandante: TimeResumo = {
    id: stats.mandante.id,
    nome: stats.mandante.nome,
    escudo: stats.mandante.escudo,
  };

  const visitante: TimeResumo = {
    id: stats.visitante.id,
    nome: stats.visitante.nome,
    escudo: stats.visitante.escudo,
  };

  const competicao = partida.competicao;
  const horario = formatarHorario(partida.horario);

  // Analisa cada estatística
  const statsToAnalyze: [string, OverUnderStat][] = [
    ['gols', overUnder.gols],
    ['escanteios', overUnder.escanteios],
    ['finalizacoes', overUnder.finalizacoes],
    ['finalizacoes_gol', overUnder.finalizacoes_gol],
    ['cartoes_amarelos', overUnder.cartoes_amarelos],
    ['faltas', overUnder.faltas],
  ];

  for (const [statKey, stat] of statsToAnalyze) {
    const novasOportunidades = analisarEstatistica(
      statKey,
      stat,
      partida.id,
      mandante,
      visitante,
      competicao,
      horario
    );
    oportunidades.push(...novasOportunidades);
  }

  return oportunidades;
}

/**
 * Ranqueia oportunidades por score (confiança × probabilidade)
 * e limita ao máximo configurado
 */
export function ranquearOportunidades(
  oportunidades: Oportunidade[],
  limite: number = MAX_OPPORTUNITIES
): Oportunidade[] {
  return oportunidades
    .sort((a, b) => b.score - a.score)
    .slice(0, limite);
}

/**
 * Agrupa oportunidades por partida
 */
export function agruparPorPartida(
  oportunidades: Oportunidade[]
): Map<string, Oportunidade[]> {
  const grupos = new Map<string, Oportunidade[]>();

  for (const op of oportunidades) {
    const key = op.matchId;
    if (!grupos.has(key)) {
      grupos.set(key, []);
    }
    grupos.get(key)!.push(op);
  }

  return grupos;
}

/**
 * Cria resultado final da busca inteligente
 */
export function criarResultado(
  todasOportunidades: Oportunidade[],
  partidasAnalisadas: number
): SmartSearchResult {
  const ranqueadas = ranquearOportunidades(todasOportunidades);
  const grupos = agruparPorPartida(todasOportunidades);

  return {
    partidas_analisadas: partidasAnalisadas,
    partidas_com_oportunidades: grupos.size,
    total_oportunidades: todasOportunidades.length,
    oportunidades: ranqueadas,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Formata probabilidade para exibição (ex: 72%)
 */
export function formatarProbabilidade(prob: number): string {
  return `${Math.round(prob * 100)}%`;
}

/**
 * Retorna cor baseada no score
 */
export function getScoreColor(score: number): string {
  if (score >= 0.6) return 'text-success';
  if (score >= 0.5) return 'text-primary-400';
  return 'text-warning';
}

/**
 * Retorna cor de fundo baseada no tipo
 */
export function getTipoBgColor(tipo: 'over' | 'under'): string {
  return tipo === 'over'
    ? 'bg-success/20 text-success'
    : 'bg-info/20 text-info';
}
