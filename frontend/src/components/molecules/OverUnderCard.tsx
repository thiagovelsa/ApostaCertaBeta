/**
 * Card de Probabilidades Over/Under
 * Exibe probabilidades estatísticas para mercados de apostas
 */

import { memo } from 'react';
import { Icon, Badge } from '@/components/atoms';
import type { OverUnderPartida, OverUnderStat, OverUnderLine as OverUnderLineType, ConfiancaLabel } from '@/types';
import { calcAdjustedChance, formatPercent } from '@/utils/chance';

interface OverUnderCardProps {
  overUnder: OverUnderPartida;
}

/**
 * Retorna a cor do texto baseada na probabilidade
 * - Verde (≥70%): Alta probabilidade
 * - Amarelo (50-70%): Moderada
 * - Cinza (<50%): Baixa
 */
function getProbabilityColor(prob: number): string {
  if (prob >= 0.70) return 'text-success font-bold';
  if (prob >= 0.50) return 'text-warning font-medium';
  return 'text-gray-400';
}

/**
 * Formata probabilidade como porcentagem
 */
/**
 * Linha individual Over/Under
 */
function OverUnderLineRow({
  line,
  over,
  under,
  overAdj,
  underAdj,
  highlight,
  bestLabel,
}: OverUnderLineType & { overAdj: number; underAdj: number; highlight?: boolean; bestLabel?: string }) {
  return (
    <div
      className={`grid grid-cols-[80px_1fr_80px_auto] items-center gap-3 py-2 px-3 rounded transition-colors ${highlight ? 'bg-primary-500/10 border border-primary-500/20' : 'hover:bg-dark-tertiary/30'
        }`}
    >
      {/* Over side - Alinhado à esquerda */}
      <div className="flex flex-col">
        <span className="text-xs text-gray-400">Over {line}</span>
        <div className="flex items-baseline gap-2">
          <span className={`text-sm font-medium tabular-nums ${getProbabilityColor(overAdj)}`}>
            {formatPercent(overAdj)}
          </span>
        </div>
        <span className="text-[10px] text-gray-400 tabular-nums">Modelo {formatPercent(over)}</span>
      </div>

      {/* Divider central */}
      <div className="h-px bg-dark-quaternary/30 mx-2" />

      {/* Under side - Alinhado à direita */}
      <div className="flex flex-col items-end text-right">
        <span className="text-xs text-gray-400">Under {line}</span>
        <div className="flex items-baseline gap-2 justify-end">
          <span className={`text-sm font-medium tabular-nums ${getProbabilityColor(underAdj)}`}>
            {formatPercent(underAdj)}
          </span>
        </div>
        <span className="text-[10px] text-gray-400 tabular-nums">Modelo {formatPercent(under)}</span>
      </div>

      {/* Highlight badge */}
      {highlight ? (
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-primary-500/15 text-primary-300 border border-primary-500/20 whitespace-nowrap">
          {bestLabel ?? 'Destaque'}
        </span>
      ) : <span className="w-[100px]" />}
    </div>
  );
}

/**
 * Seção de uma estatística com suas linhas Over/Under
 */
function StatSection({ stat }: { stat: OverUnderStat }) {
  // Converte confiança para EstabilidadeLabel compatível com Badge
  const estabilidadeLabel = stat.confidenceLabel === 'Alta' ? 'Alta' :
    stat.confidenceLabel === 'Média' ? 'Média' : 'Baixa';

  // Melhor linha por chance ajustada (nao pelo p bruto do modelo).
  const bestIdx = (() => {
    let best = -1;
    let bestP = -1;
    stat.lines.forEach((l, idx) => {
      const unc = l.uncertainty ?? 0;
      const overAdj = calcAdjustedChance(l.over ?? 0.5, stat.confidence, unc);
      const underAdj = 1 - overAdj;
      const p = Math.max(overAdj, underAdj);
      if (p > bestP) {
        bestP = p;
        best = idx;
      }
    });
    return best;
  })();

  return (
    <div className="flex flex-col h-full">
      {/* Header da estatística */}
      <div className="flex items-center justify-between mb-2 px-1 gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <Icon name={stat.icon} size="sm" className="text-primary-400 flex-shrink-0" />
          <span className="text-sm font-medium text-white">{stat.label}</span>
          <span className="text-[11px] text-gray-400 tabular-nums truncate">
            Prev {stat.lambda.toFixed(1)} · Min {stat.predMin.toFixed(1)} · Max {stat.predMax.toFixed(1)}
          </span>
        </div>
        <Badge estabilidade={estabilidadeLabel} size="sm" />
      </div>

      {/* Linhas Over/Under */}
      <div className="bg-dark-tertiary/20 rounded-lg overflow-hidden flex-1 flex flex-col justify-start">
        {stat.lines.map((line, idx) => {
          const unc = line.uncertainty ?? 0;
          const overAdj = calcAdjustedChance(line.over ?? 0.5, stat.confidence, unc);
          const underAdj = 1 - overAdj;
          const bestSide = overAdj >= underAdj ? 'Over' : 'Under';
          const bestP = Math.max(overAdj, underAdj);
          const deltaPP = (bestP - 0.5) * 100;
          const deltaLabel = `${deltaPP >= 0 ? '+' : ''}${deltaPP.toFixed(0)} p.p.`;
          return (
            <OverUnderLineRow
              key={idx}
              line={line.line}
              over={line.over}
              under={line.under}
              overAdj={overAdj}
              underAdj={underAdj}
              highlight={idx === bestIdx}
              bestLabel={idx === bestIdx ? `Recomendado: ${bestSide} (${deltaLabel})` : undefined}
            />
          )
        })}
      </div>
    </div>
  );
}

/**
 * Card principal de Probabilidades Over/Under
 * Posicionado abaixo do DisciplineCard no StatsPanel
 */
export const OverUnderCard = memo(function OverUnderCard({ overUnder }: OverUnderCardProps) {
  // Calcula confiança média geral
  const allConfidences = [
    overUnder.gols.confidence,
    overUnder.escanteios.confidence,
    overUnder.finalizacoes.confidence,
    overUnder.finalizacoes_gol.confidence,
    overUnder.cartoes_amarelos.confidence,
    overUnder.faltas.confidence,
  ];
  const avgConfidence = allConfidences.reduce((a, b) => a + b, 0) / allConfidences.length;

  const generalConfidenceLabel: ConfiancaLabel =
    avgConfidence >= 0.70 ? 'Alta' :
      avgConfidence >= 0.50 ? 'Média' : 'Baixa';

  const estabilidadeLabel = generalConfidenceLabel === 'Alta' ? 'Alta' :
    generalConfidenceLabel === 'Média' ? 'Média' : 'Baixa';

  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary hover:border-dark-quaternary transition-colors col-span-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Icon name="stats" size="sm" className="text-primary-400" />
          <h3 className="text-sm font-medium text-white">Chances Over/Under (ajustadas)</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">Confiança do modelo</span>
          <Badge estabilidade={estabilidadeLabel} size="sm" />
        </div>
      </div>

      {/* Divisor */}
      <div className="h-px bg-dark-tertiary mb-4" />

      {/* Grid 2 colunas em desktop, 1 em mobile */}
      {/* Ordem: pareamos seções de tamanho similar (muitas linhas | muitas linhas) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-stretch">
        <StatSection stat={overUnder.gols} />
        <StatSection stat={overUnder.finalizacoes} />
        <StatSection stat={overUnder.escanteios} />
        <StatSection stat={overUnder.finalizacoes_gol} />
        <StatSection stat={overUnder.cartoes_amarelos} />
        <StatSection stat={overUnder.faltas} />
      </div>
    </div>
  );
});
