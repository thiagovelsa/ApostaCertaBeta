import { useParams } from 'react-router-dom';
import { useFilterStore } from '@/stores';
import { useStats } from '@/hooks';
import { PageLayout, Container } from '@/components/layout';
import { StatsPanel } from '@/components/organisms';
import { FilterToggle } from '@/components/molecules';

export function EstatisticasPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const { filtro, setFiltro, homeMando, awayMando, toggleHomeMando, toggleAwayMando } = useFilterStore();
  const { data: stats, isLoading, error } = useStats(matchId, filtro, homeMando, awayMando);

  return (
    <PageLayout
      title="Estatísticas"
      showBackButton
      backTo="/"
    >
      <Container size="md">
        {/* Filter Controls */}
        <div className="flex justify-center mb-6">
          <FilterToggle value={filtro} onChange={setFiltro} />
        </div>

        {/* Stats Panel */}
        <StatsPanel
          stats={stats}
          isLoading={isLoading}
          error={error}
          homeMando={homeMando}
          awayMando={awayMando}
          onToggleHomeMando={toggleHomeMando}
          onToggleAwayMando={toggleAwayMando}
        />
      </Container>
    </PageLayout>
  );
}
