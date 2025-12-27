import { useParams } from 'react-router-dom';
import { useFilterStore } from '@/stores';
import { useStats } from '@/hooks';
import { PageLayout, Container } from '@/components/layout';
import { StatsPanel } from '@/components/organisms';
import { FilterToggle, PeriodoToggle } from '@/components/molecules';

export function EstatisticasPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const {
    filtro, setFiltro,
    periodo, setPeriodo,
    homeMando, awayMando,
    toggleHomeMando, toggleAwayMando
  } = useFilterStore();
  const { data: stats, isLoading, error } = useStats(matchId, filtro, periodo, homeMando, awayMando);

  return (
    <PageLayout
      title="Estatísticas"
      showBackButton
      backTo="/"
    >
      <Container size="md">
        {/* Filter Controls */}
        <div className="flex flex-col items-center gap-3 mb-6">
          <FilterToggle value={filtro} onChange={setFiltro} />
          <PeriodoToggle value={periodo} onChange={setPeriodo} />
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
