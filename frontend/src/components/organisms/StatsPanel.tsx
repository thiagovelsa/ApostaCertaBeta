import { useState, useMemo } from 'react';
import { StatsCard, DisciplineCard, PredictionsCard, OverUnderCard, QuickInsightsCard } from '@/components/molecules';
import { LoadingSpinner, TeamBadge, Icon, Badge } from '@/components/atoms';
import type { StatsResponse, FormResult, MandoFilter } from '@/types';
import type { EstabilidadeLabel } from '@/types/stats';
import { MotionSection } from '@/components/motion/MotionSection';
import { buildMatchInsights } from '@/utils/insights';

/**
 * Badges de sequência de resultados (race)
 * V = Vitória (verde), E = Empate (amarelo), D = Derrota (vermelho)
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

  const displayResults = limit ? results.slice(0, limit) : results;

  // When showing 10, render in a 2x5 grid to avoid overflow in the header card.
  const isGrid = displayResults.length > 5;

  return (
    <div
      className={`mt-1 max-w-full ${isGrid ? 'grid grid-cols-5 gap-0.5' : 'flex flex-wrap gap-0.5'} overflow-hidden`}
      aria-label="Sequência recente (Vitória/Empate/Derrota)"
    >
      {displayResults.map((r, i) => (
        <span
          key={i}
          className={`${colors[r]} text-[10px] font-bold text-white px-1.5 py-0.5 rounded ${isGrid ? 'justify-self-start' : ''}`}
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
    <div className="inline-flex bg-dark-tertiary rounded-full p-1 gap-1 mt-2">
      <button
        onClick={() => onToggle('casa')}
        type="button"
        className={`
          focus-ring px-4 py-2 sm:py-1.5 min-h-[44px] sm:min-h-0 rounded-full text-sm font-medium transition-all duration-200 flex items-center gap-1.5
          ${value === 'casa'
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
        type="button"
        className={`
          focus-ring px-4 py-2 sm:py-1.5 min-h-[44px] sm:min-h-0 rounded-full text-sm font-medium transition-all duration-200 flex items-center gap-1.5
          ${value === 'fora'
            ? 'bg-primary-500 text-dark-primary shadow-glow'
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

/**
 * Legenda explicativa da Consistência (anteriormente Estabilidade)
 */
function EstabilidadeLegend({ isOpen, onToggle }: { isOpen: boolean; onToggle: () => void }) {
  const legendItems: { estabilidade: EstabilidadeLabel; range: string; desc: string }[] = [
    { estabilidade: 'Alta', range: '≥ 70%', desc: 'Time muito previsível e consistente' },
    { estabilidade: 'Média', range: '50-70%', desc: 'Comportamento com alguma variação' },
    { estabilidade: 'Baixa', range: '< 50%', desc: 'Resultados imprevisíveis/Inconstantes' },
  ];

  return (
    <div>
      {!isOpen && (
        <p className="text-xs text-gray-400">
          Dica: use <strong>Consistência</strong> para saber se o time mantém um padrão de jogo.
        </p>
      )}

      {isOpen && (
        <div className="p-4 bg-dark-tertiary/50 rounded-lg border border-dark-tertiary">
          <p className="text-sm text-gray-300 mb-3">
            A <strong className="text-white">Consistência</strong> indica o quão confiável é o histórico do time.
            Quanto maior, menos surpresas ele costuma entregar.
          </p>

          <div className="space-y-2">
            {legendItems.map(({ estabilidade, range, desc }) => (
              <div key={estabilidade} className="flex items-center gap-3">
                <Badge estabilidade={estabilidade} size="sm" />
                <span className="text-xs text-gray-400 w-16">{range}</span>
                <span className="text-xs text-gray-400">{desc}</span>
              </div>
            ))}
          </div>

          <p className="text-xs text-gray-400 mt-3 pt-3 border-t border-dark-tertiary">
            Times mais consistentes tendem a ter resultados mais previsíveis.
            Barra cheia = alta consistência = bom para fazer entradas.
          </p>

          <button
            onClick={onToggle}
            className="focus-ring mt-3 inline-flex items-center justify-center px-3 py-2 text-xs text-gray-400 hover:text-white transition-colors min-h-[44px] sm:min-h-0 sm:py-1"
            type="button"
          >
            Fechar legenda
          </button>
        </div>
      )}
    </div>
  );
}

function QuickCompareTable({
  homeName,
  awayName,
  rows,
}: {
  homeName: string;
  awayName: string;
  rows: Array<{
    key: string;
    label: string;
    homeFeitos: number;
    awayFeitos: number;
    homeSofridos: number;
    awaySofridos: number;
  }>;
}) {
  const icons: Record<string, 'goal' | 'corner' | 'shot' | 'target'> = {
    gols: 'goal',
    escanteios: 'corner',
    finalizacoes: 'shot',
    finalizacoes_gol: 'target',
  };

  return (
    <div className="bg-dark-secondary rounded-xl p-4 lg:p-6 border border-dark-tertiary">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Icon name="stats" size="sm" className="text-primary-400" />
          <h3 className="text-base font-medium text-white">Comparativo Rápido</h3>
          <span className="text-xs text-gray-400 bg-dark-tertiary/50 px-2 py-0.5 rounded-full">Médias</span>
        </div>
      </div>

      <p className="text-[11px] text-gray-400 mb-4">
        Vantagem usa expectativa (feitos + sofridos) e é relativa ao total estimado.
      </p>

      {/* Team names header */}
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4 mb-4 px-2">
        <div className="text-right">
          <span className="text-sm font-medium text-primary-400">{homeName}</span>
        </div>
        <div className="text-center">
          <span className="text-[10px] text-gray-400 uppercase tracking-wider">vs</span>
        </div>
        <div className="text-left">
          <span className="text-sm font-medium text-gray-400">{awayName}</span>
        </div>
      </div>

      {/* Metrics */}
      <div className="space-y-2">
        {rows.map((r) => {
          // "Total" estimado: considera ataque (feitos) + defesa do adversário (sofridos).
          // expHome = (homeFeitos + awaySofridos) / 2
          // expAway = (awayFeitos + homeSofridos) / 2
          const expHome = (r.homeFeitos + r.awaySofridos) / 2;
          const expAway = (r.awayFeitos + r.homeSofridos) / 2;
          const totalEstimado = expHome + expAway;
          const edgeExpected = expHome - expAway;
          const edgeRel = edgeExpected / Math.max(1, totalEstimado);
          const homeBetter = edgeRel >= 0.06;
          const awayBetter = edgeRel <= -0.06;
          const totalFeitos = r.homeFeitos + r.awayFeitos;
          const totalSofridos = r.homeSofridos + r.awaySofridos;

          return (
            <div
              key={r.key}
              className="group relative grid grid-cols-[1fr_auto_1fr] items-center gap-4 p-4 rounded-lg bg-dark-tertiary/20 hover:bg-dark-tertiary/40 transition-all duration-200"
            >
              {/* Home Stats */}
              <div className={`flex items-center justify-end gap-3 ${homeBetter ? 'text-white' : 'text-gray-400'}`}>
                <div className="flex flex-col items-end">
                  <span className={`text-lg font-semibold tabular-nums ${homeBetter ? 'text-primary-400' : ''}`}>
                    {r.homeFeitos.toFixed(1)}
                  </span>
                  <span className="text-[11px] text-gray-400 tabular-nums">
                    {r.homeSofridos.toFixed(1)} sof.
                  </span>
                </div>
                {homeBetter && (
                  <div className="w-1.5 h-8 rounded-full bg-gradient-to-b from-primary-400 to-primary-600" />
                )}
              </div>

              {/* Center - Metric Label */}
              <div className="flex flex-col items-center justify-center min-w-[100px]">
                <div className="flex items-center gap-2 mb-0.5">
                  <Icon name={icons[r.key] ?? 'stats'} size="sm" className="text-gray-400" />
                  <span className="text-sm font-medium text-white">{r.label}</span>
                </div>
                <span
                  className="text-[10px] text-gray-400 tabular-nums"
                  title="Estimativa: média de (feitos do time + sofridos do adversário) para cada lado."
                >
                  Total (estimado): {totalEstimado.toFixed(1)}
                </span>
                <span className="text-[10px] text-gray-400 tabular-nums">
                  Feitos: {totalFeitos.toFixed(1)} · Sofridos: {totalSofridos.toFixed(1)}
                </span>
                <span className="text-[10px] text-gray-400">Feitos / Sofridos</span>
              </div>

              {/* Away Stats */}
              <div className={`flex items-center justify-start gap-3 ${awayBetter ? 'text-white' : 'text-gray-400'}`}>
                {awayBetter && (
                  <div className="w-1.5 h-8 rounded-full bg-gradient-to-b from-info to-info/60" />
                )}
                <div className="flex flex-col items-start">
                  <span className={`text-lg font-semibold tabular-nums ${awayBetter ? 'text-info' : ''}`}>
                    {r.awayFeitos.toFixed(1)}
                  </span>
                  <span className="text-[11px] text-gray-400 tabular-nums">
                    {r.awaySofridos.toFixed(1)} sof.
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 pt-4 border-t border-dark-tertiary/30">
        <div className="flex items-center gap-2">
          <div className="w-1 h-4 rounded-full bg-primary-400" />
          <span className="text-[10px] text-gray-400">Vantagem estimada (mandante)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-1 h-4 rounded-full bg-info" />
          <span className="text-[10px] text-gray-400">Vantagem estimada (visitante)</span>
        </div>
      </div>
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

  const {
    mandante,
    visitante,
    filtro_aplicado,
    partidas_analisadas,
    partidas_analisadas_mandante,
    partidas_analisadas_visitante,
  } = stats ?? {
    mandante: null,
    visitante: null,
    filtro_aplicado: 'geral',
    partidas_analisadas: 0,
    partidas_analisadas_mandante: null,
    partidas_analisadas_visitante: null,
  };

  const sampleHome = (partidas_analisadas_mandante ?? partidas_analisadas) || 0;
  const sampleAway = (partidas_analisadas_visitante ?? partidas_analisadas) || 0;
  const minSideSample = Math.min(sampleHome, sampleAway);
  const MIN_SAMPLE_FOR_SUBFILTER = 5;
  const targetSample = filtro_aplicado === 'geral' ? 50 : Number(filtro_aplicado);
  const shortSample = minSideSample > 0 && minSideSample < targetSample;
  const hasPeriodFallback = Boolean(stats?.contexto?.ajustes_aplicados?.includes('periodo_fallback_integral'));
  const hasSeasonFallback = Boolean(stats?.contexto?.ajustes_aplicados?.includes('seasonstats_fallback'));
  const showBelowFilterBadge = shortSample && filtro_aplicado !== 'geral' && !hasSeasonFallback;
  const showPartialSeasonBadge = shortSample && filtro_aplicado === 'geral' && !hasSeasonFallback;

  const previsoes = useMemo(() => stats?.previsoes ?? null, [stats]);
  const overUnderData = useMemo(() => stats?.over_under ?? null, [stats]);
  const insights = useMemo(() => (overUnderData ? buildMatchInsights(overUnderData) : []), [overUnderData]);

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
        <p className="text-gray-400 text-sm">{error.message}</p>
      </div>
    );
  }

  if (!stats || !mandante || !visitante || !previsoes || !overUnderData) {
    return (
      <div className="card text-center py-8">
        <p className="text-gray-400">Nenhuma estatística disponível</p>
      </div>
    );
  }

  const raceBadgesLimit = filtro_aplicado === '10' ? 10 : 5;

  const opportunities = insights.filter((i) => i.type === 'opportunity');
  const avoids = insights.filter((i) => i.type === 'avoid');

  const quickRows = [
    {
      key: 'gols',
      label: 'Gols',
      homeFeitos: mandante.estatisticas.gols.feitos.media,
      awayFeitos: visitante.estatisticas.gols.feitos.media,
      homeSofridos: mandante.estatisticas.gols.sofridos.media,
      awaySofridos: visitante.estatisticas.gols.sofridos.media,
    },
    {
      key: 'escanteios',
      label: 'Escanteios',
      homeFeitos: mandante.estatisticas.escanteios.feitos.media,
      awayFeitos: visitante.estatisticas.escanteios.feitos.media,
      homeSofridos: mandante.estatisticas.escanteios.sofridos.media,
      awaySofridos: visitante.estatisticas.escanteios.sofridos.media,
    },
    {
      key: 'finalizacoes',
      label: 'Chutes',
      homeFeitos: mandante.estatisticas.finalizacoes.feitos.media,
      awayFeitos: visitante.estatisticas.finalizacoes.feitos.media,
      homeSofridos: mandante.estatisticas.finalizacoes.sofridos.media,
      awaySofridos: visitante.estatisticas.finalizacoes.sofridos.media,
    },
    {
      key: 'finalizacoes_gol',
      label: 'Chutes ao Gol',
      homeFeitos: mandante.estatisticas.finalizacoes_gol.feitos.media,
      awayFeitos: visitante.estatisticas.finalizacoes_gol.feitos.media,
      homeSofridos: mandante.estatisticas.finalizacoes_gol.sofridos.media,
      awaySofridos: visitante.estatisticas.finalizacoes_gol.sofridos.media,
    },
  ];

  return (
    <div className="space-y-4">
      <MotionSection id="sec-hero" className="scroll-mt-36">
        {/* Team Headers Card — Responsive Grid */}
        <div className="card overflow-hidden">
          {/* Desktop: 3-column grid | Mobile: stacked */}
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto_1fr] gap-4 lg:gap-6 items-start">

            {/* ===== Mobile: Teams side-by-side (hidden on lg+) ===== */}
            <div className="flex items-start justify-between gap-3 lg:hidden col-span-full">
              {/* Home compact */}
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <TeamBadge src={mandante.escudo ?? undefined} alt={mandante.nome} size="lg" />
                <div className="min-w-0">
                  <h2 className="text-base font-bold text-white leading-tight truncate">{mandante.nome}</h2>
                  <span className="inline-block mt-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-primary-500/15 text-primary-400 border border-primary-500/25">
                    Mandante
                  </span>
                  <RaceBadges results={mandante.recent_form} limit={raceBadgesLimit} />
                  {onToggleHomeMando && (
                    <>
                      <MandoToggle value={homeMando ?? null} onToggle={onToggleHomeMando} />
                      <p className={`mt-1 text-[11px] ${homeMando && sampleHome < MIN_SAMPLE_FOR_SUBFILTER ? 'text-warning' : 'text-gray-400'}`}>
                        Amostra ({homeMando ?? 'todos'}): <span className="text-gray-300 font-medium">{sampleHome}</span> jogo{sampleHome === 1 ? '' : 's'}
                      </p>
                      {homeMando && hasSeasonFallback && (
                        <p className="text-[10px] text-gray-400/70 mt-0.5">Contagem total da temporada (agregado não separa por mando)</p>
                      )}
                    </>
                  )}
                </div>
              </div>

              {/* Away compact */}
              <div className="flex items-center gap-3 min-w-0 flex-1 flex-row-reverse text-right">
                <TeamBadge src={visitante.escudo ?? undefined} alt={visitante.nome} size="lg" />
                <div className="min-w-0">
                  <h2 className="text-base font-bold text-white leading-tight truncate">{visitante.nome}</h2>
                  <span className="inline-block mt-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-info/15 text-info border border-info/25">
                    Visitante
                  </span>
                  <RaceBadges results={visitante.recent_form} limit={raceBadgesLimit} />
                  {onToggleAwayMando && (
                    <>
                      <div className="flex justify-end">
                        <MandoToggle value={awayMando ?? null} onToggle={onToggleAwayMando} />
                      </div>
                      <p className={`mt-1 text-[11px] ${awayMando && sampleAway < MIN_SAMPLE_FOR_SUBFILTER ? 'text-warning' : 'text-gray-400'}`}>
                        Amostra ({awayMando ?? 'todos'}): <span className="text-gray-300 font-medium">{sampleAway}</span> jogo{sampleAway === 1 ? '' : 's'}
                      </p>
                      {awayMando && hasSeasonFallback && (
                        <p className="text-[10px] text-gray-400/70 mt-0.5">Contagem total da temporada (agregado não separa por mando)</p>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* ===== Desktop: Home (col 1, hidden on mobile) ===== */}
            <div className="hidden lg:flex items-center gap-4 min-w-0">
              <TeamBadge src={mandante.escudo ?? undefined} alt={mandante.nome} size="lg" />
              <div className="min-w-0">
                <h2 className="text-lg font-bold text-white leading-tight">{mandante.nome}</h2>
                <div className="flex items-center flex-wrap gap-2 mt-1 min-w-0">
                  <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-primary-500/15 text-primary-400 border border-primary-500/25">
                    Mandante
                  </span>
                  <div className="h-4 w-px bg-dark-tertiary" />
                  <RaceBadges results={mandante.recent_form} limit={raceBadgesLimit} />
                </div>
                {onToggleHomeMando && (
                  <>
                    <div className="mt-2">
                      <MandoToggle value={homeMando ?? null} onToggle={onToggleHomeMando} />
                    </div>
                    <p className={`mt-1 text-[11px] ${homeMando && sampleHome < MIN_SAMPLE_FOR_SUBFILTER ? 'text-warning' : 'text-gray-400'}`}>
                      Amostra ({homeMando ?? 'todos'}): <span className="text-gray-300 font-medium">{sampleHome}</span> jogo{sampleHome === 1 ? '' : 's'}
                      {homeMando && sampleHome < MIN_SAMPLE_FOR_SUBFILTER ? ' · Pouca amostra' : null}
                    </p>
                    {homeMando && hasSeasonFallback && (
                      <p className="text-[10px] text-gray-400/70 mt-0.5">Contagem total (temporada)</p>
                    )}
                  </>
                )}
              </div>
            </div>

            {/* ===== Center: Base da Análise (both mobile and desktop) ===== */}
            <div className="text-center px-4 py-3 bg-dark-tertiary/30 rounded-xl border border-dark-tertiary/50 lg:max-w-[280px]">
              <div className="flex items-center justify-center gap-2 mb-1">
                <span className="text-[10px] text-primary-400 font-bold uppercase tracking-widest">
                  Base da análise
                </span>
                {showBelowFilterBadge && (
                  <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full bg-warning/15 text-warning border border-warning/30">
                    Abaixo do filtro
                  </span>
                )}
                {showPartialSeasonBadge && (
                  <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full bg-white/5 text-gray-300 border border-white/10">
                    Base parcial
                  </span>
                )}
              </div>

              <span className="text-xs text-gray-300 uppercase tracking-wider font-medium block">
                {hasSeasonFallback
                  ? 'Temporada (agregado)'
                  : filtro_aplicado === 'geral'
                    ? 'Até 50 jogos (por time)'
                    : `Últimos ${filtro_aplicado} jogos`}
              </span>

              <p className="text-[11px] text-gray-400 mt-1.5 tabular-nums">
                <span className="text-gray-300 font-medium">{sampleHome}</span> mandante · <span className="text-gray-300 font-medium">{sampleAway}</span> visitante
              </p>

              <p className="text-[11px] text-gray-400 mt-0.5 tabular-nums">
                Amostra efetiva: <span className="text-gray-300 font-medium">{Math.max(0, minSideSample)}</span>
              </p>

              {/* Notas detalhadas — colapsáveis */}
              {(hasSeasonFallback || hasPeriodFallback || showBelowFilterBadge || showPartialSeasonBadge) && (
                <details className="mt-2 text-left">
                  <summary className="text-[10px] text-gray-400 cursor-pointer hover:text-gray-300 transition-colors select-none">
                    Ver detalhes da amostra
                  </summary>
                  <div className="mt-1.5 space-y-1 text-[11px] text-gray-400">
                    {hasSeasonFallback && (
                      <p>
                        Sem partidas individuais suficientes para este recorte; usando agregado da temporada
                        {filtro_aplicado !== 'geral' ? ` (filtro solicitado: Últimos ${filtro_aplicado}).` : '.'}
                      </p>
                    )}
                    {hasPeriodFallback && (
                      <p>Período: dados por tempo incompletos em algumas partidas; usamos integral como fallback.</p>
                    )}
                    {showBelowFilterBadge && (
                      <p>Nem todos os times têm {targetSample} jogos disponíveis neste recorte.</p>
                    )}
                    {showPartialSeasonBadge && (
                      <p>Base parcial da temporada: a consistência melhora conforme os times acumulam jogos.</p>
                    )}
                  </div>
                </details>
              )}
            </div>

            {/* ===== Desktop: Away (col 3, hidden on mobile) ===== */}
            <div className="hidden lg:flex items-center gap-4 min-w-0 justify-end flex-row-reverse text-right">
              <TeamBadge src={visitante.escudo ?? undefined} alt={visitante.nome} size="lg" />
              <div className="min-w-0">
                <h2 className="text-lg font-bold text-white leading-tight">{visitante.nome}</h2>
                <div className="flex items-center flex-wrap gap-2 mt-1 justify-end min-w-0">
                  <RaceBadges results={visitante.recent_form} limit={raceBadgesLimit} />
                  <div className="h-4 w-px bg-dark-tertiary" />
                  <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-info/15 text-info border border-info/25">
                    Visitante
                  </span>
                </div>
                {onToggleAwayMando && (
                  <>
                    <div className="mt-2 flex justify-end">
                      <MandoToggle value={awayMando ?? null} onToggle={onToggleAwayMando} />
                    </div>
                    <p className={`mt-1 text-[11px] text-right ${awayMando && sampleAway < MIN_SAMPLE_FOR_SUBFILTER ? 'text-warning' : 'text-gray-400'}`}>
                      Amostra ({awayMando ?? 'todos'}): <span className="text-gray-300 font-medium">{sampleAway}</span> jogo{sampleAway === 1 ? '' : 's'}
                      {awayMando && sampleAway < MIN_SAMPLE_FOR_SUBFILTER ? ' · Pouca amostra' : null}
                    </p>
                    {awayMando && hasSeasonFallback && (
                      <p className="text-[10px] text-gray-400/70 mt-0.5">Contagem total (temporada)</p>
                    )}
                  </>
                )}
              </div>
            </div>

          </div>
        </div>
      </MotionSection>

      <MotionSection id="sec-como-usar" className="scroll-mt-36" delay={0.01}>
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Icon name="info" size="sm" className="text-primary-400" />
            <h3 className="text-sm font-medium text-white">Como usar esta página</h3>
          </div>
          <ul className="text-sm text-gray-400 space-y-1">
            <li>
              1) Comece por <strong className="text-gray-200">O que considerar</strong> e{' '}
              <strong className="text-gray-200">O que evitar</strong>.
            </li>
            <li>
              2) Confira <strong className="text-gray-200">Previsões</strong> e a{' '}
              <strong className="text-gray-200">Confiança do modelo</strong>.
            </li>
            <li>
              3) Valide <strong className="text-gray-200">Amostra</strong> e{' '}
              <strong className="text-gray-200">Consistência</strong> antes de decidir.
            </li>
          </ul>
          <p className="text-xs text-gray-400 mt-3 pt-3 border-t border-dark-tertiary">
            Estimativas ajudam a decidir, mas não garantem resultado.
          </p>
        </div>
      </MotionSection>

      <MotionSection id="sec-previsoes" className="scroll-mt-36" delay={0.02}>
        <PredictionsCard
          previsoes={previsoes}
          homeTeamName={mandante.nome}
          awayTeamName={visitante.nome}
          overUnder={overUnderData}
        />
      </MotionSection>

      <MotionSection id="sec-resumo" className="scroll-mt-36" delay={0.04}>
        {/* Renderiza oportunidades apenas se houver itens */}
        {opportunities.length > 0 && (
          <div className="mb-4">
            <QuickInsightsCard title="O que considerar" insights={opportunities} />
          </div>
        )}

        {/* Renderiza riscos sempre */}
        {avoids.length > 0 && (
          <div className="mt-4">
            <QuickInsightsCard title="O que evitar" insights={avoids} />
          </div>
        )}
      </MotionSection>

      <MotionSection id="sec-comparacoes" className="scroll-mt-36" delay={0.06}>
        <div className="space-y-4">
          <QuickCompareTable homeName={mandante.nome} awayName={visitante.nome} rows={quickRows} />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <StatsCard
              title="Gols"
              icon="goal"
              homeFeitos={mandante.estatisticas.gols}
              awayFeitos={visitante.estatisticas.gols}
              homeTeamName={mandante.nome}
              awayTeamName={visitante.nome}
            />

            <StatsCard
              title="Escanteios"
              icon="corner"
              homeFeitos={mandante.estatisticas.escanteios}
              awayFeitos={visitante.estatisticas.escanteios}
              homeTeamName={mandante.nome}
              awayTeamName={visitante.nome}
            />

            <StatsCard
              title="Chutes"
              icon="shot"
              homeFeitos={mandante.estatisticas.finalizacoes}
              awayFeitos={visitante.estatisticas.finalizacoes}
              homeTeamName={mandante.nome}
              awayTeamName={visitante.nome}
            />

            <StatsCard
              title="Chutes ao Gol"
              icon="target"
              homeFeitos={mandante.estatisticas.finalizacoes_gol}
              awayFeitos={visitante.estatisticas.finalizacoes_gol}
              homeTeamName={mandante.nome}
              awayTeamName={visitante.nome}
            />
          </div>
        </div>
      </MotionSection>

      <MotionSection id="sec-disciplina" className="scroll-mt-36" delay={0.08}>
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
      </MotionSection>

      <MotionSection id="sec-mercados" className="scroll-mt-36" delay={0.1}>
        <OverUnderCard overUnder={overUnderData} />
      </MotionSection>

      <MotionSection id="sec-legenda" className="scroll-mt-36" delay={0.12}>
        <div className="card">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icon name="info" size="sm" className="text-primary-400" />
              <h3 className="text-sm font-medium text-white">Legenda</h3>
            </div>
            <button
              onClick={() => setShowEstabilidadeLegend(!showEstabilidadeLegend)}
              className="text-xs text-gray-400 hover:text-white transition-colors flex items-center gap-2"
              type="button"
            >
              O que significa Consistência?
              <Icon
                name="chevron-right"
                size="sm"
                className={`transform transition-transform ${showEstabilidadeLegend ? 'rotate-90' : ''}`}
              />
            </button>
          </div>

          <div className="mt-4 pt-4 border-t border-dark-tertiary">
            <EstabilidadeLegend
              isOpen={showEstabilidadeLegend}
              onToggle={() => setShowEstabilidadeLegend(!showEstabilidadeLegend)}
            />
          </div>
        </div>
      </MotionSection>
    </div>
  );
}
