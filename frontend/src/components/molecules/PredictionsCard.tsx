import { memo } from 'react';
import { Icon, Badge } from '@/components/atoms';
import type { PrevisaoPartida, PrevisaoEstatistica, ConfiancaLabel, OverUnderPartida, OverUnderStat } from '@/types';

interface PredictionCellProps {
  label: string;
  icon: 'goal' | 'corner' | 'shot' | 'target' | 'card' | 'foul';
  previsao: PrevisaoEstatistica;
}

interface PredictionsCardProps {
  previsoes: PrevisaoPartida;
  homeTeamName: string;
  awayTeamName: string;
  overUnder: OverUnderPartida;
}

/**
 * Retorna a cor do texto baseada na confiança
 */
function getTextColor(label: ConfiancaLabel): string {
  switch (label) {
    case 'Alta':
      return 'text-cv-muitoEstavel';
    case 'Média':
      return 'text-cv-moderado';
    case 'Baixa':
      return 'text-danger';
    default:
      return 'text-gray-400';
  }
}

/**
 * Card de previsões da partida - Design Grid 2x3 Compacto
 * Com barra cabo de guerra e nomes dos times apenas no header
 */
export const PredictionsCard = memo(function PredictionsCard({
  previsoes,
  homeTeamName,
  awayTeamName,
  overUnder,
}: PredictionsCardProps) {
  // Calcula confiança média geral
  const allConfiancas = [
    previsoes.gols.total.confianca,
    previsoes.escanteios.total.confianca,
    previsoes.finalizacoes.total.confianca,
    previsoes.finalizacoes_gol.total.confianca,
    previsoes.cartoes_amarelos.total.confianca,
    previsoes.faltas.total.confianca,
  ];
  const confiancaMedia = allConfiancas.reduce((a, b) => a + b, 0) / allConfiancas.length;
  const confiancaLabel: ConfiancaLabel =
    confiancaMedia >= 0.70 ? 'Alta' : confiancaMedia >= 0.50 ? 'Média' : 'Baixa';

  const ranges: Record<string, OverUnderStat> = {
    gols: overUnder.gols,
    escanteios: overUnder.escanteios,
    finalizacoes: overUnder.finalizacoes,
    finalizacoes_gol: overUnder.finalizacoes_gol,
    cartoes_amarelos: overUnder.cartoes_amarelos,
    faltas: overUnder.faltas,
  };

  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary hover:border-dark-quaternary transition-colors col-span-full">
      {/* Header do card */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon name="stats" size="sm" className="text-primary-400" />
          <h3 className="text-base sm:text-lg font-semibold text-white">Previsões da Partida</h3>
        </div>
        <Badge estabilidade={confiancaLabel} label="Confiança do modelo" size="sm" />
      </div>

      {/* Intervalo do modelo */}
      <div className="flex items-center justify-between mb-4 px-1">
        <p className="text-xs text-gray-400">
          Min (Under) e Max (Over) sao um intervalo de previsao ({Math.round((ranges.gols.intervalLevel ?? 0.9) * 100)}%).
        </p>
        <span className="text-[11px] text-gray-400">Min | Exata | Max</span>
      </div>

      {/* Header dos Times - UMA ÚNICA VEZ */}
      <div className="flex items-center justify-between mb-4 px-3">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-primary-500" />
          <span className="text-sm font-medium text-white truncate max-w-[120px]" title={homeTeamName}>
            {homeTeamName}
          </span>
        </div>
        <span className="text-xs text-gray-400">vs</span>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-white truncate max-w-[120px]" title={awayTeamName}>
            {awayTeamName}
          </span>
          <div className="w-2 h-2 rounded-full bg-info" />
        </div>
      </div>

      {/* Grid 2x3 de métricas */}
      <div className="grid grid-cols-2 gap-3">
        <PredictionWithRange label="Gols" icon="goal" previsao={previsoes.gols} range={ranges.gols} />
        <PredictionWithRange label="Escanteios" icon="corner" previsao={previsoes.escanteios} range={ranges.escanteios} />
        <PredictionWithRange label="Chutes" icon="shot" previsao={previsoes.finalizacoes} range={ranges.finalizacoes} />
        <PredictionWithRange label="Chutes ao Gol" icon="target" previsao={previsoes.finalizacoes_gol} range={ranges.finalizacoes_gol} />
        <PredictionWithRange label="Cartões" icon="card" previsao={previsoes.cartoes_amarelos} range={ranges.cartoes_amarelos} />
        <PredictionWithRange label="Faltas" icon="foul" previsao={previsoes.faltas} range={ranges.faltas} />
      </div>
    </div>
  );
});

function PredictionWithRange({
  label,
  icon,
  previsao,
  range,
}: PredictionCellProps & { range: OverUnderStat }) {
  const { home, away, total } = previsao;

  const min = Number.isFinite(range.predMin) ? range.predMin : range.lambda;
  const max = Number.isFinite(range.predMax) ? range.predMax : range.lambda;
  const denom = Math.max(0.0001, max - min);
  const marker = Math.max(0, Math.min(1, (total.valor - min) / denom));

  // Calcula proporção para a barra cabo de guerra
  const sum = home.valor + away.valor;
  const homePercent = sum > 0 ? (home.valor / sum) * 100 : 50;

  const textColor = getTextColor(total.confiancaLabel);

  return (
    <div className="bg-dark-tertiary/30 rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <Icon name={icon} size="sm" className="text-primary-400" />
          <span className="text-xs font-medium text-gray-300">{label}</span>
        </div>
        <div className="flex items-center gap-1 tabular-nums">
          <span className="text-xs text-gray-400">Exata:</span>
          <span className="text-sm font-bold text-primary-400">{total.valor.toFixed(1)}</span>
        </div>
      </div>

      {/* Range: Min | Exata | Max */}
      <div className="flex items-center justify-between text-[11px] text-gray-400 tabular-nums mb-2">
        <span>Min {min.toFixed(1)}</span>
        <span className="text-gray-400">|</span>
        <span className="text-gray-300 font-medium">Prev {total.valor.toFixed(1)}</span>
        <span className="text-gray-400">|</span>
        <span>Max {max.toFixed(1)}</span>
      </div>

      <div className="relative h-2 bg-dark-quaternary rounded-full overflow-hidden mb-3">
        <div className="absolute inset-0 bg-gradient-to-r from-primary-500/35 via-primary-500/10 to-info/35" />
        <div
          className="absolute top-0 h-full w-1 bg-white/70"
          style={{ left: `calc(${marker * 100}% - 2px)` }}
          aria-hidden
        />
      </div>

      {/* Home + Tug of war + Away */}
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-sm font-bold text-white w-8 text-right tabular-nums">
          {home.valor.toFixed(1)}
        </span>

        <div
          className="flex-1 h-2 bg-dark-quaternary rounded-full overflow-hidden flex"
          title="Divide o total previsto entre os times (home vs away). Não indica chance de vitória."
        >
          <div className="bg-primary-500 transition-all duration-500" style={{ width: `${homePercent}%` }} />
          <div className="bg-info transition-all duration-500" style={{ width: `${100 - homePercent}%` }} />
        </div>

        <span className="text-sm font-bold text-white w-8 text-left tabular-nums">
          {away.valor.toFixed(1)}
        </span>
      </div>

      <div className="text-[11px] text-gray-400 text-center mb-1">
        Distribuição do total previsto (não é probabilidade).
      </div>

      <div className="flex items-center justify-center gap-1">
        <span className="text-xs text-gray-400">Confiança do modelo:</span>
        <span className={`text-xs font-medium ${textColor}`}>
          {Math.round(total.confianca * 100)}%
        </span>
      </div>
    </div>
  );
}
