import { Icon, Badge } from '@/components/atoms';
import type { EstatisticaMetrica, ArbitroInfo } from '@/types';
import type { EstabilidadeLabel } from '@/types/stats';

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
 * Retorna a cor da barra de estabilidade baseada no valor
 */
function getEstabilidadeBarColor(estabilidade: number): string {
  if (estabilidade >= 70) return 'bg-cv-muitoEstavel';
  if (estabilidade >= 50) return 'bg-cv-moderado';
  return 'bg-danger';
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
  // Calcula estabilidade média para o badge
  const avgEstabilidade = (home.estabilidade + away.estabilidade) / 2;
  const badgeLabel: EstabilidadeLabel =
    avgEstabilidade >= 70 ? 'Alta' :
    avgEstabilidade >= 50 ? 'Média' : 'Baixa';

  const total = home.media + away.media;
  const percentHome = total > 0 ? (home.media / total) * 100 : 50;

  return (
    <div className="flex flex-col">
      {/* Header com label e badge - altura fixa */}
      <div className="flex items-center justify-between mb-2 h-6">
        <span className="text-sm text-gray-300">{label}</span>
        <Badge estabilidade={badgeLabel} label="Estabilidade" size="sm" />
      </div>

      {/* Valores comparativos - altura fixa */}
      <div className="flex items-center justify-between mb-2 h-7">
        <span className="text-lg font-bold text-white">{home.media.toFixed(1)}</span>
        <span className="text-lg font-bold text-white">{away.media.toFixed(1)}</span>
      </div>

      {/* Barra de comparação - altura fixa */}
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

      {/* Estabilidade por time - layout vertical para consistência */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 truncate w-24" title={homeTeamName}>
            {homeTeamName}
          </span>
          <div className="flex-1 h-1 bg-dark-quaternary rounded-full overflow-hidden">
            <div
              className={`h-full ${getEstabilidadeBarColor(home.estabilidade)} transition-all duration-500`}
              style={{ width: `${home.estabilidade}%` }}
            />
          </div>
          <span className="text-xs text-gray-400 w-8 text-right">{home.estabilidade}%</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 truncate w-24" title={awayTeamName}>
            {awayTeamName}
          </span>
          <div className="flex-1 h-1 bg-dark-quaternary rounded-full overflow-hidden">
            <div
              className={`h-full ${getEstabilidadeBarColor(away.estabilidade)} transition-all duration-500`}
              style={{ width: `${away.estabilidade}%` }}
            />
          </div>
          <span className="text-xs text-gray-400 w-8 text-right">{away.estabilidade}%</span>
        </div>
      </div>
    </div>
  );
}

/**
 * Componente para exibir informações do árbitro
 * Mostra dados da competição e da temporada (todas competições)
 */
function RefereeInfo({ arbitro }: { arbitro: ArbitroInfo }) {
  // Fallback para compatibilidade com API antiga
  const partidasTemp = arbitro.partidas_temporada ?? arbitro.partidas;
  const mediaTemp = arbitro.media_cartoes_temporada ?? arbitro.media_cartoes_amarelos;

  return (
    <div className="flex flex-col items-center justify-center p-3 bg-dark-tertiary/50 rounded-lg">
      <div className="w-10 h-10 rounded-full bg-dark-quaternary flex items-center justify-center mb-2">
        <Icon name="whistle" size="md" className="text-warning" />
      </div>
      <p className="text-sm font-medium text-white">{arbitro.nome}</p>
      <p className="text-xs text-gray-500">
        {arbitro.partidas} jogos · {arbitro.media_cartoes_amarelos.toFixed(1)} cartões/jogo (competição)
      </p>
      <p className="text-xs text-gray-400">
        {partidasTemp} jogos · {mediaTemp.toFixed(1)} cartões/jogo (temporada)
      </p>
    </div>
  );
}

/**
 * Card de disciplina com múltiplas métricas simples
 * Layout full-width com cartões amarelos e faltas
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
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
