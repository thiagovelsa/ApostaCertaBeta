import type { OverUnderPartida, OverUnderStat, OverUnderLine } from '@/types';
import { calcAdjustedChance } from '@/utils/chance';

export type MatchInsightType = 'opportunity' | 'avoid';

export interface MatchInsight {
  type: MatchInsightType;
  statKey: string;
  statLabel: string;
  marketLabel: string; // e.g. "Under 2.5"
  chanceAdj: number; // 0-1 (principal)
  chanceModel: number; // 0-1 (probabilidade do modelo)
  confidence: number; // 0-1
  uncertainty?: number | null;
  confidenceLabel: 'Baixa' | 'Média' | 'Alta';
  reason: string;
}

function pickBestLine(
  stat: OverUnderStat
): { line: OverUnderLine; side: 'over' | 'under'; pModel: number; pAdj: number } | null {
  if (!stat.lines?.length) return null;

  let best: { line: OverUnderLine; side: 'over' | 'under'; pModel: number; pAdj: number } | null = null;
  for (const l of stat.lines) {
    const unc = l.uncertainty ?? 0;
    const over = l.over ?? 0.5;
    const under = l.under ?? (1 - over);

    const overAdj = calcAdjustedChance(over, stat.confidence, unc);
    const underAdj = 1 - overAdj;

    const side = overAdj >= underAdj ? 'over' : 'under';
    const pAdj = Math.max(overAdj, underAdj);
    const pModel = Math.max(over, under);

    if (!best || pAdj > best.pAdj) best = { line: l, side, pModel, pAdj };
  }
  return best;
}

function reasonFor(stat: OverUnderStat, line: OverUnderLine): string {
  const unc = line.uncertainty ?? null;
  if (stat.confidenceLabel === 'Alta') return 'Alta confianca do modelo para esta estatistica.';
  if (stat.confidenceLabel === 'Média') {
    if (unc !== null && unc >= 0.35) return 'Confianca media, mas com incerteza elevada na linha.';
    return 'Confianca media, use gestao de risco.';
  }
  if (unc !== null && unc >= 0.35) return 'Baixa confianca e alta incerteza: evitar.';
  return 'Baixa confianca do modelo: evitar.';
}

export function buildMatchInsights(overUnder: OverUnderPartida): MatchInsight[] {
  const stats: Array<[string, OverUnderStat]> = [
    ['gols', overUnder.gols],
    ['escanteios', overUnder.escanteios],
    ['finalizacoes', overUnder.finalizacoes],
    ['finalizacoes_gol', overUnder.finalizacoes_gol],
    ['cartoes_amarelos', overUnder.cartoes_amarelos],
    ['faltas', overUnder.faltas],
  ];

  const out: MatchInsight[] = [];

  for (const [key, stat] of stats) {
    const best = pickBestLine(stat);
    if (!best) continue;
    const { line, side, pModel, pAdj } = best;

    const type: MatchInsightType =
      stat.confidenceLabel === 'Baixa' || (line.uncertainty ?? 0) >= 0.40 ? 'avoid' : 'opportunity';

    out.push({
      type,
      statKey: key,
      statLabel: stat.label,
      marketLabel: `${side === 'over' ? 'Over' : 'Under'} ${line.line}`,
      chanceAdj: pAdj,
      chanceModel: pModel,
      confidence: stat.confidence,
      uncertainty: line.uncertainty ?? null,
      confidenceLabel: stat.confidenceLabel,
      reason: reasonFor(stat, line),
    });
  }

  // Sort: opportunities first by probability; then avoids by highest uncertainty/prob
  out.sort((a, b) => {
    if (a.type !== b.type) return a.type === 'opportunity' ? -1 : 1;
    return b.chanceAdj - a.chanceAdj;
  });

  return out.slice(0, 6);
}
