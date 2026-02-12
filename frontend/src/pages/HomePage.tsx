import { useMemo, useState } from 'react';
import { useDateStore } from '@/stores';
import { usePartidas, useSmartSearch } from '@/hooks';
import { PageLayout, Container, Grid } from '@/components/layout';
import { MatchSearchToolbar, MatchesByCompetition, SmartSearchResults, VirtualizedMatchesGrid } from '@/components/organisms';
import { Button, Icon, LoadingSpinner } from '@/components/atoms';
import { useQueryClient } from '@tanstack/react-query';
import type { PartidaResumo } from '@/types';
import type { MatchesSort, MatchesView } from '@/components/organisms/MatchSearchToolbar';
import { isMatchUpcoming } from '@/utils/matchStatus';

function formatDisplayDate(dateString: string): string {
  const [year, month, day] = dateString.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const dateOnly = new Date(date);
  dateOnly.setHours(0, 0, 0, 0);

  if (dateOnly.getTime() === today.getTime()) {
    return 'Hoje';
  } else if (dateOnly.getTime() === tomorrow.getTime()) {
    return 'Amanhã';
  } else if (dateOnly.getTime() === yesterday.getTime()) {
    return 'Ontem';
  }

  return date.toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  });
}

function formatShortDate(dateString: string): string {
  const [year, month, day] = dateString.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  return date.toLocaleDateString('pt-BR');
}

export function HomePage() {
  const { selectedDate, goToPreviousDay, goToNextDay, goToToday } = useDateStore();
  const [view, setView] = useState<MatchesView>('list');
  const [sort, setSort] = useState<MatchesSort>('time');
  const [query, setQuery] = useState('');
  const [onlyUpcoming, setOnlyUpcoming] = useState(false);
  const queryClient = useQueryClient();
  const { data, isLoading, error, refetch } = usePartidas(selectedDate);

  // Smart Search hook
  const smartSearch = useSmartSearch();

  const handleSmartSearch = () => {
    smartSearch.search(selectedDate);
  };

  const handleDateChange = (direction: 'prev' | 'next' | 'today') => {
    if (direction === 'prev') {
      goToPreviousDay();
    } else if (direction === 'next') {
      goToNextDay();
    } else {
      goToToday();
    }
    smartSearch.reset();
  };

  const handleClearCache = () => {
    queryClient.clear();
    smartSearch.reset();
  };

  // Check if smart search is active (loading or has results)
  const isSmartSearchActive = smartSearch.isLoading || smartSearch.isAnalyzing || smartSearch.result !== null || smartSearch.error !== null;

  const matchesFiltered = useMemo(() => {
    const partidas = data?.partidas ?? [];
    let filtered = partidas;

    if (onlyUpcoming) {
      const now = new Date();
      filtered = filtered.filter((m: PartidaResumo) => isMatchUpcoming(m.data, m.horario, now));
    }

    if (!query.trim()) return filtered;
    const q = query.trim().toLowerCase();
    return filtered.filter((m: PartidaResumo) => {
      return (
        (m.competicao || '').toLowerCase().includes(q) ||
        (m.mandante?.nome || '').toLowerCase().includes(q) ||
        (m.visitante?.nome || '').toLowerCase().includes(q) ||
        (m.estadio || '').toLowerCase().includes(q)
      );
    });
  }, [data, query, onlyUpcoming]);

  const hiddenCount = useMemo(() => {
    if (!onlyUpcoming) return 0;
    const total = data?.partidas?.length ?? 0;
    return Math.max(0, total - matchesFiltered.length);
  }, [data, matchesFiltered.length, onlyUpcoming]);

  const matchesSorted = useMemo(() => {
    const ms = [...matchesFiltered];
    if (sort === 'competition') {
      ms.sort((a, b) => (a.competicao || '').localeCompare(b.competicao || ''));
      return ms;
    }
    ms.sort((a, b) => (a.horario || '').localeCompare(b.horario || ''));
    return ms;
  }, [matchesFiltered, sort]);

  function MatchCardSkeleton() {
    return (
      <div className="card relative overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <div className="h-3 w-40 skeleton-shimmer rounded" />
          <div className="h-3 w-12 skeleton-shimmer rounded" />
        </div>
        <div className="flex items-center justify-between">
          <div className="h-10 w-10 skeleton-shimmer rounded-full" />
          <div className="h-6 w-10 skeleton-shimmer rounded" />
          <div className="h-10 w-10 skeleton-shimmer rounded-full" />
        </div>
        <div className="mt-4 pt-3 border-t border-dark-tertiary">
          <div className="h-3 w-28 skeleton-shimmer rounded mx-auto" />
        </div>
      </div>
    );
  }

  return (
    <PageLayout>
      <Container>
        {/* Date Navigation */}
        <div className="flex items-center justify-between mb-6">
          <Button
            variant="ghost"
            onClick={() => handleDateChange('prev')}
            className="min-w-[44px] sm:min-w-[36px]"
          >
            <Icon name="chevron-left" size="md" />
          </Button>

          <div className="text-center">
            <button
              onClick={() => handleDateChange('today')}
              className="focus-ring text-lg font-semibold text-white hover:text-primary-400 transition-colors capitalize rounded-lg px-2 py-1"
            >
              {formatDisplayDate(selectedDate)}
            </button>
            <p className="text-sm text-gray-400">
              {formatShortDate(selectedDate)}
            </p>
            {!isLoading && data && matchesSorted.length > 0 && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-primary-500/20 text-primary-400 mt-1 font-medium">
                {matchesSorted.length} partida{matchesSorted.length === 1 ? '' : 's'}
              </span>
            )}
            {!isLoading && onlyUpcoming && hiddenCount > 0 && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-dark-tertiary/60 text-gray-300 mt-1 font-medium">
                Filtro ativo · {hiddenCount} ocultada{hiddenCount === 1 ? '' : 's'}
              </span>
            )}
          </div>

          <Button
            variant="ghost"
            onClick={() => handleDateChange('next')}
            className="min-w-[44px] sm:min-w-[36px]"
          >
            <Icon name="chevron-right" size="md" />
          </Button>
        </div>

        {/* Sticky Toolbar */}
        <div className="sticky top-16 z-40 mb-5">
          <MatchSearchToolbar
            query={query}
            onQueryChange={setQuery}
            sort={sort}
            onSortChange={setSort}
            view={view}
            onViewChange={setView}
            onlyUpcoming={onlyUpcoming}
            onOnlyUpcomingChange={setOnlyUpcoming}
            onRefresh={() => refetch()}
            onClearCache={handleClearCache}
            onSmartSearch={handleSmartSearch}
            smartSearchBusy={smartSearch.isLoading || smartSearch.isAnalyzing}
          />
        </div>

        {/* Smart Search Loading State */}
        {smartSearch.isLoading && view === 'insights' && (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {/* Smart Search Results */}
        {view === 'insights' && isSmartSearchActive && !smartSearch.isLoading && (
          <SmartSearchResults
            result={smartSearch.result}
            progress={smartSearch.progress}
            isAnalyzing={smartSearch.isAnalyzing}
            error={smartSearch.error}
            onClose={smartSearch.reset}
            onRetry={handleSmartSearch}
          />
        )}

        {/* Smart Search Empty */}
        {view === 'insights' && !isSmartSearchActive && !smartSearch.isLoading && (
          <div className="card text-center py-10">
            <Icon name="target" size="lg" className="text-primary-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">
              Análise Automática do Dia
            </h2>
            <p className="text-gray-400 mb-6 max-w-xl mx-auto">
              A Análise Automática varre as partidas da data selecionada e destaca o que considerar e o que evitar com base em estatísticas. Use como triagem, não como garantia.
            </p>
            <Button
              variant="primary"
              size="lg"
              onClick={handleSmartSearch}
              disabled={smartSearch.isLoading || smartSearch.isAnalyzing}
            >
              <Icon name="target" size="sm" className="mr-2" />
              Rodar Análise Automática
            </Button>
          </div>
        )}

        {/* Error State */}
        {error && view === 'list' && (
          <div className="card text-center py-8" role="alert" aria-live="polite">
            <p className="text-danger mb-4">Não foi possível carregar as partidas.</p>
            <p className="text-gray-400 text-sm mb-4">{error.message}</p>
            <Button variant="secondary" onClick={() => refetch()}>
              Tentar novamente
            </Button>
          </div>
        )}

        {/* Results */}
        {view === 'list' && (
          <>
            {/* Loading State */}
            {isLoading && (
              <Grid cols={2} gap="md">
                {Array.from({ length: 6 }).map((_, i) => (
                  <MatchCardSkeleton key={i} />
                ))}
              </Grid>
            )}

            {/* Empty State */}
            {!isLoading && !error && data && matchesSorted.length === 0 && (
              <div className="card text-center py-12">
                <Icon name="calendar" size="lg" className="text-gray-400 mx-auto mb-4" />
                <p className="text-gray-400 mb-2">Sem partidas para esta data.</p>
                <p className="text-gray-400 text-sm mb-4">
                  Pode não haver jogos agendados (ou o filtro atual ocultou os jogos já encerrados).
                </p>
                <Button variant="secondary" onClick={() => handleDateChange('today')}>
                  Voltar para hoje
                </Button>
              </div>
            )}

            {/* List */}
            {!isLoading && !error && data && matchesSorted.length > 0 && (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-gray-400">
                    <span className="text-white font-semibold">{matchesSorted.length}</span>{' '}
                    {onlyUpcoming ? 'futuras' : 'partidas'}
                  </h2>
                  <p className="text-xs text-gray-400">
                    Abra uma partida para ver previsões, consistência, amostra e mercados.
                  </p>
                </div>

                {sort === 'competition' ? (
                  <MatchesByCompetition matches={matchesSorted} cols={2} />
                ) : (
                  <VirtualizedMatchesGrid matches={matchesSorted} cols={2} gap="md" />
                )}
              </>
            )}
          </>
        )}
      </Container>
    </PageLayout>
  );
}
