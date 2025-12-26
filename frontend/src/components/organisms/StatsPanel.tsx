import { useState } from 'react';
import { StatsCard, DisciplineCard, PredictionsCard } from '@/components/molecules';
import { LoadingSpinner, TeamBadge, Icon, Badge } from '@/components/atoms';
import { calcularPrevisoes } from '@/utils/predictions';
import type { StatsResponse, CVClassificacao } from '@/types';

interface StatsPanelProps {
  stats: StatsResponse | undefined;
  isLoading: boolean;
  error: Error | null;
}

/**
 * Legenda explicativa do Coeficiente de Variação (CV)
 */
function CVLegend({ isOpen, onToggle }: { isOpen: boolean; onToggle: () => void }) {
  const legendItems: { classificacao: CVClassificacao; range: string; desc: string }[] = [
    { classificacao: 'Muito Estável', range: '< 15%', desc: 'Time muito previsível' },
    { classificacao: 'Estável', range: '15-30%', desc: 'Comportamento consistente' },
    { classificacao: 'Moderado', range: '30-50%', desc: 'Alguma variação' },
    { classificacao: 'Instável', range: '50-75%', desc: 'Resultados imprevisíveis' },
    { classificacao: 'Muito Instável', range: '> 75%', desc: 'Alta imprevisibilidade' },
  ];

  return (
    <div className="mb-6">
      <button
        onClick={onToggle}
        className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
      >
        <Icon name="info" size="sm" />
        <span>O que significa o CV?</span>
        <Icon
          name="chevron-right"
          size="sm"
          className={`transform transition-transform ${isOpen ? 'rotate-90' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="mt-3 p-4 bg-dark-tertiary/50 rounded-lg border border-dark-tertiary">
          <p className="text-sm text-gray-300 mb-3">
            O <strong className="text-white">CV (Coeficiente de Variação)</strong> mede a
            estabilidade do time. Quanto menor, mais previsível é o desempenho.
          </p>

          <div className="space-y-2">
            {legendItems.map(({ classificacao, range, desc }) => (
              <div key={classificacao} className="flex items-center gap-3">
                <Badge classificacao={classificacao} size="sm" />
                <span className="text-xs text-gray-500 w-16">{range}</span>
                <span className="text-xs text-gray-400">{desc}</span>
              </div>
            ))}
          </div>

          <p className="text-xs text-gray-500 mt-3 pt-3 border-t border-dark-tertiary">
            Times mais estáveis tendem a ter resultados mais consistentes.
          </p>
        </div>
      )}
    </div>
  );
}

export function StatsPanel({ stats, isLoading, error }: StatsPanelProps) {
  const [showCVLegend, setShowCVLegend] = useState(false);

  if (isLoading) {
    return (
      <div className="card flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card text-center py-8">
        <p className="text-danger mb-2">Erro ao carregar estatísticas</p>
        <p className="text-gray-500 text-sm">{error.message}</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="card text-center py-8">
        <p className="text-gray-500">Nenhuma estatística disponível</p>
      </div>
    );
  }

  const { mandante, visitante, filtro_aplicado, partidas_analisadas } = stats;

  // Calcula previsões para a partida
  const previsoes = calcularPrevisoes(mandante, visitante, partidas_analisadas);

  return (
    <div className="space-y-4">
      {/* Team Headers Card */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <TeamBadge src={mandante.escudo ?? undefined} alt={mandante.nome} size="md" />
            <div>
              <p className="font-semibold text-white">{mandante.nome}</p>
              <p className="text-xs text-gray-500">Mandante</p>
            </div>
          </div>

          <div className="text-center px-4">
            <span className="text-xs text-gray-500 uppercase tracking-wider">
              {filtro_aplicado === 'geral'
                ? 'Temporada'
                : `Últimos ${filtro_aplicado}`}
            </span>
            <p className="text-xs text-gray-600 mt-1">
              {partidas_analisadas} jogos analisados
            </p>
          </div>

          <div className="flex items-center gap-3 flex-row-reverse">
            <TeamBadge src={visitante.escudo ?? undefined} alt={visitante.nome} size="md" />
            <div className="text-right">
              <p className="font-semibold text-white">{visitante.nome}</p>
              <p className="text-xs text-gray-500">Visitante</p>
            </div>
          </div>
        </div>

        {/* CV Legend */}
        <div className="mt-4 pt-4 border-t border-dark-tertiary">
          <CVLegend isOpen={showCVLegend} onToggle={() => setShowCVLegend(!showCVLegend)} />
        </div>
      </div>

      {/* Predictions Card */}
      <PredictionsCard
        previsoes={previsoes}
        homeTeamName={mandante.nome}
        awayTeamName={visitante.nome}
      />

      {/* Stats Grid - 2 columns on desktop, 1 on mobile */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Gols */}
        <StatsCard
          title="Gols"
          icon="goal"
          homeFeitos={mandante.estatisticas.gols}
          awayFeitos={visitante.estatisticas.gols}
          homeTeamName={mandante.nome}
          awayTeamName={visitante.nome}
        />

        {/* Escanteios */}
        <StatsCard
          title="Escanteios"
          icon="corner"
          homeFeitos={mandante.estatisticas.escanteios}
          awayFeitos={visitante.estatisticas.escanteios}
          homeTeamName={mandante.nome}
          awayTeamName={visitante.nome}
        />

        {/* Finalizações */}
        <StatsCard
          title="Finalizações"
          icon="shot"
          homeFeitos={mandante.estatisticas.finalizacoes}
          awayFeitos={visitante.estatisticas.finalizacoes}
          homeTeamName={mandante.nome}
          awayTeamName={visitante.nome}
        />

        {/* Finalizações no Gol */}
        <StatsCard
          title="Finalizações no Gol"
          icon="target"
          homeFeitos={mandante.estatisticas.finalizacoes_gol}
          awayFeitos={visitante.estatisticas.finalizacoes_gol}
          homeTeamName={mandante.nome}
          awayTeamName={visitante.nome}
        />

        {/* Disciplina - Full Width */}
        <DisciplineCard
          metrics={[
            {
              label: 'Cartões Amarelos',
              home: mandante.estatisticas.cartoes_amarelos,
              away: visitante.estatisticas.cartoes_amarelos,
            },
            {
              label: 'Faltas',
              home: mandante.estatisticas.faltas,
              away: visitante.estatisticas.faltas,
            },
          ]}
          homeTeamName={mandante.nome}
          awayTeamName={visitante.nome}
          arbitro={stats.arbitro}
        />
      </div>
    </div>
  );
}
