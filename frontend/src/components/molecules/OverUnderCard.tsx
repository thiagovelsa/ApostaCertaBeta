/**
 * Card de Probabilidades Over/Under
 * Exibe probabilidades estatísticas para mercados de apostas
 */

import { Icon, Badge } from '@/components/atoms';
import type { OverUnderPartida, OverUnderStat, OverUnderLine as OverUnderLineType, ConfiancaLabel } from '@/types';

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
function formatPercent(prob: number): string {
  return `${Math.round(prob * 100)}%`;
}

/**
 * Linha individual Over/Under
 */
function OverUnderLineRow({ line, over, under }: OverUnderLineType) {
  return (
    <div className="flex items-center justify-between py-1.5 px-3 hover:bg-dark-tertiary/30 rounded transition-colors">
      <div className="flex items-center gap-2 flex-1">
        <span className="text-xs text-gray-500 w-16">Over {line}</span>
        <span className={`text-sm w-10 ${getProbabilityColor(over)}`}>
          {formatPercent(over)}
        </span>
      </div>

      <div className="h-px flex-1 bg-dark-quaternary/50 mx-2" />

      <div className="flex items-center gap-2 flex-1 justify-end">
        <span className={`text-sm w-10 text-right ${getProbabilityColor(under)}`}>
          {formatPercent(under)}
        </span>
        <span className="text-xs text-gray-500 w-16 text-right">Under {line}</span>
      </div>
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

  return (
    <div className="mb-4 last:mb-0">
      {/* Header da estatística */}
      <div className="flex items-center justify-between mb-2 px-1">
        <div className="flex items-center gap-2">
          <Icon name={stat.icon} size="sm" className="text-primary-400" />
          <span className="text-sm font-medium text-white">{stat.label}</span>
          <span className="text-xs text-gray-500">
            (Prev: {stat.lambda.toFixed(1)})
          </span>
        </div>
        <Badge estabilidade={estabilidadeLabel} size="sm" />
      </div>

      {/* Linhas Over/Under */}
      <div className="bg-dark-tertiary/20 rounded-lg overflow-hidden">
        {stat.lines.map((line, idx) => (
          <OverUnderLineRow
            key={idx}
            line={line.line}
            over={line.over}
            under={line.under}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * Card principal de Probabilidades Over/Under
 * Posicionado abaixo do DisciplineCard no StatsPanel
 */
export function OverUnderCard({ overUnder }: OverUnderCardProps) {
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
          <h3 className="text-sm font-medium text-white">Probabilidades Over/Under</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Confiança</span>
          <Badge estabilidade={estabilidadeLabel} size="sm" />
        </div>
      </div>

      {/* Divisor */}
      <div className="h-px bg-dark-tertiary mb-4" />

      {/* Grid 2 colunas em desktop, 1 em mobile */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
        <StatSection stat={overUnder.gols} />
        <StatSection stat={overUnder.escanteios} />
        <StatSection stat={overUnder.finalizacoes} />
        <StatSection stat={overUnder.finalizacoes_gol} />
        <StatSection stat={overUnder.cartoes_amarelos} />
        <StatSection stat={overUnder.faltas} />
      </div>
    </div>
  );
}
