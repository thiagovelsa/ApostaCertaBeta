import { useState, useMemo } from 'react';
import { StatsCard, DisciplineCard, PredictionsCard, OverUnderCard } from '@/components/molecules';
import { LoadingSpinner, TeamBadge, Icon, Badge } from '@/components/atoms';
import { calcularPrevisoes } from '@/utils/predictions';
import { calcularOverUnder } from '@/utils/overUnder';
import type { StatsResponse, FormResult, MandoFilter } from '@/types';
import type { EstabilidadeLabel } from '@/types/stats';

/**
 * Badges de sequência de resultados (race)
 * V = Vitória (verde), E = Empate (amarelo), D = Derrota (vermelho)
 *
 * @param results - Array de resultados (W/D/L)
 * @param limit - Limite de badges a exibir (default: todos)
 */
function RaceBadges({ results, limit }: { results?: FormResult[]; limit?: number }) {
  if (!results?.length) return null;

  const colors: Record<FormResult, string> = {
    W: 'bg-success',
    D: 'bg-warning',
    L: 'bg-danger',
  };

  const labels: Record<FormResult, string> = {
    W: 'V',
    D: 'E',
    L: 'D',
  };

  // Aplica limite se especificado
  const displayResults = limit ? results.slice(0, limit) : results;

  return (
    <div className="flex gap-0.5 mt-1">
      {displayResults.map((r, i) => (
        <span
          key={i}
          className={`${colors[r]} text-[10px] font-bold text-white px-1.5 py-0.5 rounded`}
        >
          {labels[r]}
        </span>
      ))}
    </div>
  );
}

/**
 * Botões toggle para subfiltro Casa/Fora
 */
function MandoToggle({
  value,
  onToggle,
}: {
  value: MandoFilter;
  onToggle: (mando: 'casa' | 'fora') => void;
}) {
  return (
    <div className="inline-flex bg-dark-tertiary rounded-lg p-1 gap-1 mt-2">
      <button
        onClick={() => onToggle('casa')}
        className={`
          px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center gap-1.5
          ${
            value === 'casa'
              ? 'bg-primary-500 text-dark-primary shadow-glow'
              : 'text-gray-400 hover:text-white hover:bg-dark-quaternary'
          }
        `}
      >
        <Icon name="home" size="sm" />
        Casa
      </button>
      <button
        onClick={() => onToggle('fora')}
        className={`
          px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center gap-1.5
          ${
            value === 'fora'
              ? 'bg-info text-dark-primary shadow-glow'
              : 'text-gray-400 hover:text-white hover:bg-dark-quaternary'
          }
        `}
      >
        <Icon name="plane" size="sm" />
        Fora
      </button>
    </div>
  );
}

interface StatsPanelProps {
  stats: StatsResponse | undefined;
  isLoading: boolean;
  error: Error | null;
  homeMando?: MandoFilter;
  awayMando?: MandoFilter;
  onToggleHomeMando?: (mando: 'casa' | 'fora') => void;
  onToggleAwayMando?: (mando: 'casa' | 'fora') => void;
}

/**
 * Legenda explicativa da Estabilidade
 */
function EstabilidadeLegend({ isOpen, onToggle }: { isOpen: boolean; onToggle: () => void }) {
  const legendItems: { estabilidade: EstabilidadeLabel; range: string; desc: string }[] = [
    { estabilidade: 'Alta', range: '≥ 70%', desc: 'Time muito previsível e consistente' },
    { estabilidade: 'Média', range: '50-70%', desc: 'Comportamento com alguma variação' },
    { estabilidade: 'Baixa', range: '< 50%', desc: 'Resultados imprevisíveis' },
  ];

  return (
    <div className="mb-6">
      <button
        onClick={onToggle}
        className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
      >
        <Icon name="info" size="sm" />
        <span>O que significa Estabilidade?</span>
        <Icon
          name="chevron-right"
          size="sm"
          className={`transform transition-transform ${isOpen ? 'rotate-90' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="mt-3 p-4 bg-dark-tertiary/50 rounded-lg border border-dark-tertiary">
          <p className="text-sm text-gray-300 mb-3">
            A <strong className="text-white">Estabilidade</strong> mede a consistência do time.
            Quanto maior, mais previsível é o desempenho.
          </p>

          <div className="space-y-2">
            {legendItems.map(({ estabilidade, range, desc }) => (
              <div key={estabilidade} className="flex items-center gap-3">
                <Badge estabilidade={estabilidade} size="sm" />
                <span className="text-xs text-gray-500 w-16">{range}</span>
                <span className="text-xs text-gray-400">{desc}</span>
              </div>
            ))}
          </div>

          <p className="text-xs text-gray-500 mt-3 pt-3 border-t border-dark-tertiary">
            Times mais estáveis tendem a ter resultados mais consistentes.
            Barra cheia = alta estabilidade = bom para previsões.
          </p>
        </div>
      )}
    </div>
  );
}

export function StatsPanel({
  stats,
  isLoading,
  error,
  homeMando,
  awayMando,
  onToggleHomeMando,
  onToggleAwayMando,
}: StatsPanelProps) {
  const [showEstabilidadeLegend, setShowEstabilidadeLegend] = useState(false);

  // Hooks devem ser chamados ANTES de qualquer return condicional
  // para manter a ordem consistente entre renderizações
  const { mandante, visitante, filtro_aplicado, partidas_analisadas } = stats ?? {
    mandante: null,
    visitante: null,
    filtro_aplicado: 'geral',
    partidas_analisadas: 0,
  };

  // Calcula previsões para a partida (memoizado para evitar recálculos)
  const previsoes = useMemo(
    () => mandante && visitante
      ? calcularPrevisoes(
          mandante,
          visitante,
          partidas_analisadas,
          homeMando ?? null,
          awayMando ?? null
        )
      : null,
    [mandante, visitante, partidas_analisadas, homeMando, awayMando]
  );

  // Calcula probabilidades Over/Under (memoizado)
  const overUnderData = useMemo(
    () => previsoes && mandante && visitante
      ? calcularOverUnder(
          previsoes,
          mandante.estatisticas,
          visitante.estatisticas,
          partidas_analisadas
        )
      : null,
    [previsoes, mandante, visitante, partidas_analisadas]
  );

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

  if (!stats || !mandante || !visitante || !previsoes || !overUnderData) {
    return (
      <div className="card text-center py-8">
        <p className="text-gray-500">Nenhuma estatística disponível</p>
      </div>
    );
  }

  // Limite de badges a exibir baseado no filtro
  // Temporada (geral) → 5, Últimos 5 → 5, Últimos 10 → 10
  const raceBadgesLimit = filtro_aplicado === '10' ? 10 : 5;

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
              <RaceBadges results={mandante.recent_form} limit={raceBadgesLimit} />
              {onToggleHomeMando && (
                <MandoToggle value={homeMando ?? null} onToggle={onToggleHomeMando} />
              )}
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
              <div className="flex justify-end">
                <RaceBadges results={visitante.recent_form} limit={raceBadgesLimit} />
              </div>
              {onToggleAwayMando && (
                <div className="flex justify-end">
                  <MandoToggle value={awayMando ?? null} onToggle={onToggleAwayMando} />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Estabilidade Legend */}
        <div className="mt-4 pt-4 border-t border-dark-tertiary">
          <EstabilidadeLegend isOpen={showEstabilidadeLegend} onToggle={() => setShowEstabilidadeLegend(!showEstabilidadeLegend)} />
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

        {/* Chutes */}
        <StatsCard
          title="Chutes"
          icon="shot"
          homeFeitos={mandante.estatisticas.finalizacoes}
          awayFeitos={visitante.estatisticas.finalizacoes}
          homeTeamName={mandante.nome}
          awayTeamName={visitante.nome}
        />

        {/* Chutes ao Gol */}
        <StatsCard
          title="Chutes ao Gol"
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

        {/* Probabilidades Over/Under - Full Width */}
        <OverUnderCard overUnder={overUnderData} />
      </div>
    </div>
  );
}
