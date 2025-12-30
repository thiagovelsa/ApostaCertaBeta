import { memo } from 'react';
import { Icon, Badge } from '@/components/atoms';
import type { PrevisaoPartida, PrevisaoEstatistica, ConfiancaLabel } from '@/types';

interface PredictionCellProps {
  label: string;
  icon: 'goal' | 'corner' | 'shot' | 'target' | 'card' | 'foul';
  previsao: PrevisaoEstatistica;
}

interface PredictionsCardProps {
  previsoes: PrevisaoPartida;
  homeTeamName: string;
  awayTeamName: string;
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
 * Célula de previsão individual com barra cabo de guerra
 */
function PredictionCell({ label, icon, previsao }: PredictionCellProps) {
  const { home, away, total } = previsao;

  // Calcula proporção para a barra cabo de guerra
  const sum = home.valor + away.valor;
  const homePercent = sum > 0 ? (home.valor / sum) * 100 : 50;

  const textColor = getTextColor(total.confiancaLabel);

  return (
    <div className="bg-dark-tertiary/30 rounded-lg p-3">
      {/* Linha 1: Label + Total */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <Icon name={icon} size="sm" className="text-primary-400" />
          <span className="text-xs font-medium text-gray-300">{label}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-xs text-gray-500">Previsão:</span>
          <span className="text-sm font-bold text-primary-400">{total.valor.toFixed(1)}</span>
        </div>
      </div>

      {/* Linha 2: Home + Barra Cabo de Guerra + Away */}
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-sm font-bold text-white w-8 text-right">
          {home.valor.toFixed(1)}
        </span>

        <div className="flex-1 h-2 bg-dark-quaternary rounded-full overflow-hidden flex">
          {/* Lado Home - verde primário */}
          <div
            className="bg-primary-500 transition-all duration-500"
            style={{ width: `${homePercent}%` }}
          />
          {/* Lado Away - azul info */}
          <div
            className="bg-info transition-all duration-500"
            style={{ width: `${100 - homePercent}%` }}
          />
        </div>

        <span className="text-sm font-bold text-white w-8 text-left">
          {away.valor.toFixed(1)}
        </span>
      </div>

      {/* Linha 3: % confiança individual */}
      <div className="flex items-center justify-center gap-1">
        <span className="text-xs text-gray-500">Confiança:</span>
        <span className={`text-xs font-medium ${textColor}`}>
          {Math.round(total.confianca * 100)}%
        </span>
      </div>
    </div>
  );
}

/**
 * Card de previsões da partida - Design Grid 2x3 Compacto
 * Com barra cabo de guerra e nomes dos times apenas no header
 */
export const PredictionsCard = memo(function PredictionsCard({
  previsoes,
  homeTeamName,
  awayTeamName,
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

  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary hover:border-dark-quaternary transition-colors col-span-full">
      {/* Header do card */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon name="stats" size="sm" className="text-primary-400" />
          <h3 className="text-sm font-medium text-white">Previsões da Partida</h3>
        </div>
        <Badge estabilidade={confiancaLabel} label="Probabilidade" size="sm" />
      </div>

      {/* Header dos Times - UMA ÚNICA VEZ */}
      <div className="flex items-center justify-between mb-4 px-3">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-primary-500" />
          <span className="text-sm font-medium text-white truncate max-w-[120px]" title={homeTeamName}>
            {homeTeamName}
          </span>
        </div>
        <span className="text-xs text-gray-500">vs</span>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-white truncate max-w-[120px]" title={awayTeamName}>
            {awayTeamName}
          </span>
          <div className="w-2 h-2 rounded-full bg-info" />
        </div>
      </div>

      {/* Grid 2x3 de métricas */}
      <div className="grid grid-cols-2 gap-3">
        <PredictionCell
          label="Gols"
          icon="goal"
          previsao={previsoes.gols}
        />
        <PredictionCell
          label="Escanteios"
          icon="corner"
          previsao={previsoes.escanteios}
        />
        <PredictionCell
          label="Chutes"
          icon="shot"
          previsao={previsoes.finalizacoes}
        />
        <PredictionCell
          label="Chutes ao Gol"
          icon="target"
          previsao={previsoes.finalizacoes_gol}
        />
        <PredictionCell
          label="Cartões"
          icon="card"
          previsao={previsoes.cartoes_amarelos}
        />
        <PredictionCell
          label="Faltas"
          icon="foul"
          previsao={previsoes.faltas}
        />
      </div>
    </div>
  );
});
