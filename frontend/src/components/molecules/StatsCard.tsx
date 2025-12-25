import { Icon, Badge, type IconName } from '@/components/atoms';
import type { EstatisticaFeitos, CVClassificacao } from '@/types';

interface StatsCardProps {
  title: string;
  icon: IconName;
  homeFeitos: EstatisticaFeitos;
  awayFeitos: EstatisticaFeitos;
  homeTeamName: string;
  awayTeamName: string;
}

/**
 * Retorna a cor da barra de progresso baseada na classificação CV
 */
function getCVBarColor(classificacao: CVClassificacao): string {
  switch (classificacao) {
    case 'Muito Estável':
      return 'bg-cv-muitoEstavel';
    case 'Estável':
      return 'bg-cv-estavel';
    case 'Moderado':
      return 'bg-cv-moderado';
    case 'Instável':
      return 'bg-cv-instavel';
    case 'Muito Instável':
      return 'bg-cv-muitoInstavel';
    default:
      return 'bg-gray-500';
  }
}

/**
 * Componente para exibir o CV de um time com barra de progresso colorida
 */
function CVTeamBar({
  teamName,
  cv,
  classificacao,
}: {
  teamName: string;
  cv: number;
  classificacao: CVClassificacao;
}) {
  const cvPercent = Math.min(cv * 100, 100);
  const barColor = getCVBarColor(classificacao);

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-400 truncate w-20" title={teamName}>
        {teamName.length > 12 ? `${teamName.substring(0, 10)}...` : teamName}
      </span>
      <div className="flex-1 h-1.5 bg-dark-quaternary rounded-full overflow-hidden">
        <div
          className={`h-full ${barColor} transition-all duration-500`}
          style={{ width: `${cvPercent}%` }}
        />
      </div>
      <span className="text-xs text-gray-300 font-medium w-10 text-right">
        {cvPercent.toFixed(0)}%
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
  homeCv,
  awayCv,
  homeClassificacao,
  awayClassificacao,
}: {
  label: string;
  homeValue: number;
  awayValue: number;
  homeTeamName: string;
  awayTeamName: string;
  homeCv: number;
  awayCv: number;
  homeClassificacao: CVClassificacao;
  awayClassificacao: CVClassificacao;
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
          className="bg-gray-600 transition-all duration-500"
          style={{ width: `${100 - percentHome}%` }}
        />
      </div>

      {/* CV por time */}
      <div className="space-y-1.5">
        <CVTeamBar
          teamName={homeTeamName}
          cv={homeCv}
          classificacao={homeClassificacao}
        />
        <CVTeamBar
          teamName={awayTeamName}
          cv={awayCv}
          classificacao={awayClassificacao}
        />
      </div>
    </div>
  );
}

/**
 * Card de estatísticas com layout compacto
 * Mostra Feitos e Sofridos lado a lado com CV por time
 */
export function StatsCard({
  title,
  icon,
  homeFeitos,
  awayFeitos,
  homeTeamName,
  awayTeamName,
}: StatsCardProps) {
  // Determina a classificação geral do card (usa a mais instável)
  const classifications = [
    homeFeitos.feitos.classificacao,
    homeFeitos.sofridos.classificacao,
    awayFeitos.feitos.classificacao,
    awayFeitos.sofridos.classificacao,
  ];

  const classificationOrder: CVClassificacao[] = [
    'Muito Instável',
    'Instável',
    'Moderado',
    'Estável',
    'Muito Estável',
  ];

  const worstClassification = classifications.reduce((worst, current) => {
    const worstIndex = classificationOrder.indexOf(worst);
    const currentIndex = classificationOrder.indexOf(current);
    return currentIndex < worstIndex ? current : worst;
  }, 'Muito Estável' as CVClassificacao);

  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary hover:border-dark-quaternary transition-colors">
      {/* Header do card */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Icon name={icon} size="sm" className="text-primary-400" />
          <h3 className="text-sm font-medium text-white">{title}</h3>
        </div>
        <Badge classificacao={worstClassification} size="sm" />
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
          homeCv={homeFeitos.feitos.cv}
          awayCv={awayFeitos.feitos.cv}
          homeClassificacao={homeFeitos.feitos.classificacao}
          awayClassificacao={awayFeitos.feitos.classificacao}
        />

        {/* Separador vertical */}
        <div className="w-px bg-dark-tertiary" />

        <MetricColumn
          label="Sofridos"
          homeValue={homeFeitos.sofridos.media}
          awayValue={awayFeitos.sofridos.media}
          homeTeamName={homeTeamName}
          awayTeamName={awayTeamName}
          homeCv={homeFeitos.sofridos.cv}
          awayCv={awayFeitos.sofridos.cv}
          homeClassificacao={homeFeitos.sofridos.classificacao}
          awayClassificacao={awayFeitos.sofridos.classificacao}
        />
      </div>
    </div>
  );
}
