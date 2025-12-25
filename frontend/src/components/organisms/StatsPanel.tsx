import { useState } from 'react';
import { StatMetric } from '@/components/molecules';
import { LoadingSpinner, TeamBadge, Icon, Badge, type IconName } from '@/components/atoms';
import type { StatsResponse, EstatisticaFeitos, CVClassificacao } from '@/types';

interface StatsPanelProps {
  stats: StatsResponse | undefined;
  isLoading: boolean;
  error: Error | null;
}

interface StatsCategoryProps {
  title: string;
  icon: IconName;
  homeFeitos: EstatisticaFeitos;
  awayFeitos: EstatisticaFeitos;
}

function StatsCategory({ title, icon, homeFeitos, awayFeitos }: StatsCategoryProps) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Icon name={icon} size="sm" className="text-primary-400" />
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">{title}</h3>
      </div>
      <div className="space-y-1">
        <StatMetric
          label="Feitos"
          home={homeFeitos.feitos}
          away={awayFeitos.feitos}
        />
        <StatMetric
          label="Sofridos"
          home={homeFeitos.sofridos}
          away={awayFeitos.sofridos}
        />
      </div>
    </div>
  );
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
    <div className="mb-4">
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

  return (
    <div className="card">
      {/* Team Headers */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-dark-tertiary">
        <div className="flex items-center gap-3">
          <TeamBadge src={mandante.escudo ?? undefined} alt={mandante.nome} size="md" />
          <div>
            <p className="font-semibold text-white">{mandante.nome}</p>
            <p className="text-xs text-gray-500">Mandante</p>
          </div>
        </div>

        <div className="text-center">
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
      <CVLegend isOpen={showCVLegend} onToggle={() => setShowCVLegend(!showCVLegend)} />

      {/* Stats Categories */}
      <div className="divide-y divide-dark-tertiary">
        {/* Gols */}
        <StatsCategory
          title="Gols"
          icon="goal"
          homeFeitos={mandante.estatisticas.gols}
          awayFeitos={visitante.estatisticas.gols}
        />

        {/* Escanteios */}
        <StatsCategory
          title="Escanteios"
          icon="corner"
          homeFeitos={mandante.estatisticas.escanteios}
          awayFeitos={visitante.estatisticas.escanteios}
        />

        {/* Finalizações */}
        <StatsCategory
          title="Finalizações"
          icon="shot"
          homeFeitos={mandante.estatisticas.finalizacoes}
          awayFeitos={visitante.estatisticas.finalizacoes}
        />

        {/* Finalizações no Gol */}
        <StatsCategory
          title="Finalizações no Gol"
          icon="target"
          homeFeitos={mandante.estatisticas.finalizacoes_gol}
          awayFeitos={visitante.estatisticas.finalizacoes_gol}
        />

        {/* Cartões e Faltas - Simple Metrics */}
        <div className="pt-4">
          <div className="flex items-center gap-2 mb-3">
            <Icon name="card" size="sm" className="text-primary-400" />
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
              Disciplina
            </h3>
          </div>
          <div className="space-y-1">
            <StatMetric
              label="Cartões Amarelos"
              home={mandante.estatisticas.cartoes_amarelos}
              away={visitante.estatisticas.cartoes_amarelos}
            />
            <StatMetric
              label="Cartões Vermelhos"
              home={mandante.estatisticas.cartoes_vermelhos}
              away={visitante.estatisticas.cartoes_vermelhos}
            />
            <StatMetric
              label="Faltas"
              home={mandante.estatisticas.faltas}
              away={visitante.estatisticas.faltas}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
