import { useState } from 'react';
import { useDateStore } from '@/stores';
import { usePartidas, useSmartSearch } from '@/hooks';
import { PageLayout, Container, Grid } from '@/components/layout';
import { MatchCard, SmartSearchResults } from '@/components/organisms';
import { Button, Icon, LoadingSpinner } from '@/components/atoms';
import { useQueryClient } from '@tanstack/react-query';

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
  const [searchEnabled, setSearchEnabled] = useState(false);
  const queryClient = useQueryClient();
  const { data, isLoading, error, refetch } = usePartidas(selectedDate, { enabled: searchEnabled });

  // Smart Search hook
  const smartSearch = useSmartSearch();

  const handleSearch = () => {
    if (searchEnabled) {
      refetch();
    } else {
      setSearchEnabled(true);
    }
    // Reset smart search when doing normal search
    smartSearch.reset();
  };

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
    // Reset search state when date changes
    setSearchEnabled(false);
    smartSearch.reset();
  };

  const handleClearCache = () => {
    queryClient.clear();
    setSearchEnabled(false);
    smartSearch.reset();
  };

  // Check if smart search is active (loading or has results)
  const isSmartSearchActive = smartSearch.isLoading || smartSearch.isAnalyzing || smartSearch.result !== null;

  return (
    <PageLayout>
      <Container>
        {/* Date Navigation */}
        <div className="flex items-center justify-between mb-6">
          <Button variant="ghost" onClick={() => handleDateChange('prev')}>
            <Icon name="chevron-left" size="md" />
          </Button>

          <div className="text-center">
            <button
              onClick={() => handleDateChange('today')}
              className="text-lg font-semibold text-white hover:text-primary-400 transition-colors capitalize"
            >
              {formatDisplayDate(selectedDate)}
            </button>
            <p className="text-sm text-gray-500">
              {formatShortDate(selectedDate)}
            </p>
          </div>

          <Button variant="ghost" onClick={() => handleDateChange('next')}>
            <Icon name="chevron-right" size="md" />
          </Button>
        </div>

        {/* Search Buttons - shown when no search has been made */}
        {!searchEnabled && !isLoading && !isSmartSearchActive && (
          <div className="card text-center py-12">
            <Icon name="calendar" size="lg" className="text-primary-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">
              Buscar Partidas
            </h2>
            <p className="text-gray-400 mb-6">
              Selecione uma data e clique no botão para buscar as partidas
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Button variant="primary" size="lg" onClick={handleSearch}>
                <Icon name="search" size="sm" className="mr-2" />
                Buscar Partidas
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={handleSmartSearch}
                disabled={smartSearch.isLoading || smartSearch.isAnalyzing}
              >
                <Icon name="target" size="sm" className="mr-2" />
                Busca Inteligente
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-4 max-w-md mx-auto">
              A Busca Inteligente analisa todas as partidas e identifica as melhores oportunidades de aposta
            </p>
          </div>
        )}

        {/* Smart Search Loading State */}
        {smartSearch.isLoading && (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {/* Smart Search Results */}
        {isSmartSearchActive && !smartSearch.isLoading && (
          <SmartSearchResults
            result={smartSearch.result}
            progress={smartSearch.progress}
            isAnalyzing={smartSearch.isAnalyzing}
            onClose={smartSearch.reset}
          />
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {/* Error State */}
        {error && searchEnabled && (
          <div className="card text-center py-8">
            <p className="text-danger mb-4">Erro ao carregar partidas</p>
            <p className="text-gray-500 text-sm mb-4">{error.message}</p>
            <Button variant="secondary" onClick={() => refetch()}>
              Tentar novamente
            </Button>
          </div>
        )}

        {/* Results */}
        {!isLoading && !error && data && searchEnabled && (
          <>
            {data.partidas.length === 0 ? (
              <div className="card text-center py-12">
                <Icon name="calendar" size="lg" className="text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 mb-2">Nenhuma partida encontrada</p>
                <p className="text-gray-600 text-sm mb-4">
                  Não há jogos agendados para esta data
                </p>
                <Button variant="secondary" onClick={() => handleDateChange('today')}>
                  Voltar para hoje
                </Button>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-gray-400">
                    <span className="text-white font-semibold">{data.total_partidas}</span> partidas
                  </h2>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={handleSmartSearch}
                      disabled={smartSearch.isLoading || smartSearch.isAnalyzing}
                    >
                      <Icon name="target" size="sm" className="mr-1" />
                      Busca Inteligente
                    </Button>
                    <Button variant="ghost" size="sm" onClick={handleClearCache}>
                      <Icon name="refresh" size="sm" className="mr-1" />
                      Limpar cache
                    </Button>
                    <Button variant="ghost" size="sm" onClick={handleSearch}>
                      <Icon name="refresh" size="sm" className="mr-1" />
                      Atualizar
                    </Button>
                  </div>
                </div>

                <Grid cols={2} gap="md">
                  {data.partidas.map((match) => (
                    <MatchCard key={match.id} match={match} />
                  ))}
                </Grid>
              </>
            )}
          </>
        )}
      </Container>
    </PageLayout>
  );
}
