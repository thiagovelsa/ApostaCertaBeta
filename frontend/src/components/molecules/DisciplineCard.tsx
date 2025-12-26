import { Icon, Badge } from '@/components/atoms';
import type { EstatisticaMetrica, CVClassificacao, ArbitroInfo } from '@/types';

interface DisciplineMetric {
  label: string;
  home: EstatisticaMetrica;
  away: EstatisticaMetrica;
}

interface DisciplineCardProps {
  metrics: DisciplineMetric[];
  homeTeamName: string;
  awayTeamName: string;
  arbitro?: ArbitroInfo | null;
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
 * Componente para uma linha de métrica simples (sem feitos/sofridos)
 */
function DisciplineMetricRow({
  label,
  home,
  away,
  homeTeamName,
  awayTeamName,
}: {
  label: string;
  home: EstatisticaMetrica;
  away: EstatisticaMetrica;
  homeTeamName: string;
  awayTeamName: string;
}) {
  // Determina a pior classificação para o badge
  const classificationOrder: CVClassificacao[] = [
    'Muito Instável',
    'Instável',
    'Moderado',
    'Estável',
    'Muito Estável',
  ];
  const worstClassification =
    classificationOrder.indexOf(home.classificacao) <
    classificationOrder.indexOf(away.classificacao)
      ? home.classificacao
      : away.classificacao;

  const total = home.media + away.media;
  const percentHome = total > 0 ? (home.media / total) * 100 : 50;

  return (
    <div className="py-3 first:pt-0 last:pb-0">
      {/* Header com label e badge */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-300">{label}</span>
        <Badge classificacao={worstClassification} size="sm" />
      </div>

      {/* Valores comparativos */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-lg font-bold text-white">{home.media.toFixed(1)}</span>
        <span className="text-lg font-bold text-white">{away.media.toFixed(1)}</span>
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

      {/* CV por time */}
      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 truncate min-w-0" style={{ maxWidth: '90px' }} title={homeTeamName}>
            {homeTeamName}
          </span>
          <div className="flex-1 h-1 bg-dark-quaternary rounded-full overflow-hidden">
            <div
              className={`h-full ${getCVBarColor(home.classificacao)} transition-all duration-500`}
              style={{ width: `${Math.min(home.cv * 100, 100)}%` }}
            />
          </div>
          <span className="text-xs text-gray-400">{(home.cv * 100).toFixed(0)}%</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 truncate min-w-0" style={{ maxWidth: '90px' }} title={awayTeamName}>
            {awayTeamName}
          </span>
          <div className="flex-1 h-1 bg-dark-quaternary rounded-full overflow-hidden">
            <div
              className={`h-full ${getCVBarColor(away.classificacao)} transition-all duration-500`}
              style={{ width: `${Math.min(away.cv * 100, 100)}%` }}
            />
          </div>
          <span className="text-xs text-gray-400">{(away.cv * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
}

/**
 * Componente para exibir informações do árbitro
 */
function RefereeInfo({ arbitro }: { arbitro: ArbitroInfo }) {
  return (
    <div className="flex items-center justify-between p-3 bg-dark-tertiary/50 rounded-lg">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-dark-quaternary flex items-center justify-center">
          <Icon name="whistle" size="sm" className="text-gray-400" />
        </div>
        <div>
          <p className="text-sm font-medium text-white">{arbitro.nome}</p>
          <p className="text-xs text-gray-500">
            {arbitro.partidas} {arbitro.partidas === 1 ? 'partida' : 'partidas'} na competição
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-lg font-bold text-warning">{arbitro.media_cartoes_amarelos.toFixed(1)}</p>
        <p className="text-xs text-gray-500">cartões/jogo</p>
      </div>
    </div>
  );
}

/**
 * Card de disciplina com múltiplas métricas simples
 * Layout full-width com cartões amarelos, vermelhos e faltas
 */
export function DisciplineCard({
  metrics,
  homeTeamName,
  awayTeamName,
  arbitro,
}: DisciplineCardProps) {
  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary hover:border-dark-quaternary transition-colors col-span-full">
      {/* Header do card */}
      <div className="flex items-center gap-2 mb-4">
        <Icon name="card" size="sm" className="text-primary-400" />
        <h3 className="text-sm font-medium text-white">Disciplina</h3>
      </div>

      {/* Árbitro (se disponível) */}
      {arbitro && (
        <>
          <RefereeInfo arbitro={arbitro} />
          <div className="h-px bg-dark-tertiary my-4" />
        </>
      )}

      {/* Divisor (se não tem árbitro) */}
      {!arbitro && <div className="h-px bg-dark-tertiary mb-4" />}

      {/* Grid de métricas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        {metrics.map((metric) => (
          <DisciplineMetricRow
            key={metric.label}
            label={metric.label}
            home={metric.home}
            away={metric.away}
            homeTeamName={homeTeamName}
            awayTeamName={awayTeamName}
          />
        ))}
      </div>
    </div>
  );
}
