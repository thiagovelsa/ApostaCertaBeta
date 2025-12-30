import { memo } from 'react';
import { Icon, Badge, type IconName } from '@/components/atoms';
import type { EstatisticaFeitos } from '@/types';
import type { EstabilidadeLabel } from '@/types/stats';

interface StatsCardProps {
  title: string;
  icon: IconName;
  homeFeitos: EstatisticaFeitos;
  awayFeitos: EstatisticaFeitos;
  homeTeamName: string;
  awayTeamName: string;
}

/**
 * Retorna a cor da barra de estabilidade baseada no valor
 * Barra cheia = verde (estável), barra vazia = vermelho (instável)
 */
function getEstabilidadeBarColor(estabilidade: number): string {
  if (estabilidade >= 70) return 'bg-cv-muitoEstavel';
  if (estabilidade >= 50) return 'bg-cv-moderado';
  return 'bg-danger';
}

/**
 * Componente para exibir a estabilidade de um time com barra de progresso colorida
 * Barra cheia = 100% estável = bom (verde)
 */
function EstabilidadeTeamBar({
  teamName,
  estabilidade,
}: {
  teamName: string;
  estabilidade: number;
}) {
  const barColor = getEstabilidadeBarColor(estabilidade);

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-400 truncate min-w-0 flex-shrink" style={{ maxWidth: '100px' }} title={teamName}>
        {teamName}
      </span>
      <div className="flex-1 h-1.5 bg-dark-quaternary rounded-full overflow-hidden">
        <div
          className={`h-full ${barColor} transition-all duration-500`}
          style={{ width: `${estabilidade}%` }}
        />
      </div>
      <span className="text-xs text-gray-300 font-medium w-10 text-right">
        {estabilidade}%
      </span>
    </div>
  );
}

/**
 * Componente para uma métrica individual (Feitos ou Sofridos)
 */
function MetricColumn({
  label,
  homeValue,
  awayValue,
  homeTeamName,
  awayTeamName,
  homeEstabilidade,
  awayEstabilidade,
}: {
  label: string;
  homeValue: number;
  awayValue: number;
  homeTeamName: string;
  awayTeamName: string;
  homeEstabilidade: number;
  awayEstabilidade: number;
}) {
  const total = homeValue + awayValue;
  const percentHome = total > 0 ? (homeValue / total) * 100 : 50;

  return (
    <div className="flex-1">
      <p className="text-xs text-gray-500 uppercase tracking-wider mb-2 text-center">
        {label}
      </p>

      {/* Valores comparativos */}
      <div className="flex items-center justify-center gap-3 mb-3">
        <span className="text-lg font-bold text-white">{homeValue.toFixed(1)}</span>
        <span className="text-gray-600 text-sm">vs</span>
        <span className="text-lg font-bold text-white">{awayValue.toFixed(1)}</span>
      </div>

      {/* Barra de comparação */}
      <div className="h-1.5 bg-dark-quaternary rounded-full overflow-hidden flex mb-3">
        <div
          className="bg-primary-500 transition-all duration-500"
          style={{ width: `${percentHome}%` }}
        />
        <div
          className="bg-info transition-all duration-500"
          style={{ width: `${100 - percentHome}%` }}
        />
      </div>

      {/* Estabilidade por time */}
      <div className="space-y-1.5">
        <EstabilidadeTeamBar
          teamName={homeTeamName}
          estabilidade={homeEstabilidade}
        />
        <EstabilidadeTeamBar
          teamName={awayTeamName}
          estabilidade={awayEstabilidade}
        />
      </div>
    </div>
  );
}

/**
 * Card de estatísticas com layout compacto
 * Mostra Feitos e Sofridos lado a lado com Estabilidade por time
 */
export const StatsCard = memo(function StatsCard({
  title,
  icon,
  homeFeitos,
  awayFeitos,
  homeTeamName,
  awayTeamName,
}: StatsCardProps) {
  // Calcula estabilidade média para determinar o badge do card
  const estabilidades = [
    homeFeitos.feitos.estabilidade,
    homeFeitos.sofridos.estabilidade,
    awayFeitos.feitos.estabilidade,
    awayFeitos.sofridos.estabilidade,
  ];
  const avgEstabilidade = estabilidades.reduce((a, b) => a + b, 0) / estabilidades.length;

  // Determina o label simplificado baseado na estabilidade média
  const cardLabel: EstabilidadeLabel =
    avgEstabilidade >= 70 ? 'Alta' :
    avgEstabilidade >= 50 ? 'Média' : 'Baixa';

  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary hover:border-dark-quaternary transition-colors">
      {/* Header do card */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Icon name={icon} size="sm" className="text-primary-400" />
          <h3 className="text-sm font-medium text-white">{title}</h3>
        </div>
        <Badge estabilidade={cardLabel} label="Estabilidade" size="sm" />
      </div>

      {/* Divisor */}
      <div className="h-px bg-dark-tertiary mb-4" />

      {/* Grid Feitos | Sofridos */}
      <div className="flex gap-4">
        <MetricColumn
          label="Feitos"
          homeValue={homeFeitos.feitos.media}
          awayValue={awayFeitos.feitos.media}
          homeTeamName={homeTeamName}
          awayTeamName={awayTeamName}
          homeEstabilidade={homeFeitos.feitos.estabilidade}
          awayEstabilidade={awayFeitos.feitos.estabilidade}
        />

        {/* Separador vertical */}
        <div className="w-px bg-dark-tertiary" />

        <MetricColumn
          label="Sofridos"
          homeValue={homeFeitos.sofridos.media}
          awayValue={awayFeitos.sofridos.media}
          homeTeamName={homeTeamName}
          awayTeamName={awayTeamName}
          homeEstabilidade={homeFeitos.sofridos.estabilidade}
          awayEstabilidade={awayFeitos.sofridos.estabilidade}
        />
      </div>
    </div>
  );
});
