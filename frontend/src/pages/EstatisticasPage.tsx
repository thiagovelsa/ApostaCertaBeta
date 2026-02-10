import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useFilterStore } from '@/stores';
import { useStats } from '@/hooks';
import { buildMatchExportBundle } from '@/services';
import { downloadJson, toSafeFilenameSegment } from '@/utils/downloadJson';
import { Button, Icon } from '@/components/atoms';
import { PageLayout, Container } from '@/components/layout';
import { StatsPanel } from '@/components/organisms';
import { FilterToggle, PeriodoToggle, JumpToSectionChips } from '@/components/molecules';

export function EstatisticasPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const {
    filtro, setFiltro,
    periodo, setPeriodo,
    homeMando, awayMando,
    toggleHomeMando, toggleAwayMando
  } = useFilterStore();
  const { data: stats, isLoading, error } = useStats(matchId, filtro, periodo, homeMando, awayMando);

  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  async function handleExport() {
    if (!matchId || isExporting) return;

    setIsExporting(true);
    setExportError(null);

    try {
      const bundle = await buildMatchExportBundle(matchId, { filtro, periodo, homeMando, awayMando });

      const preferred =
        bundle.contexts.find((c) => c.key === 'selected' && c.analysis) ??
        bundle.contexts.find((c) => Boolean(c.analysis));

      const partida = preferred?.analysis?.partida;
      const homeCode = partida?.mandante?.codigo ?? 'HOME';
      const awayCode = partida?.visitante?.codigo ?? 'AWAY';
      const date = partida?.data ?? 'sem-data';
      const ts = bundle.generated_at.replace(/[:.]/g, '-');

      const segments = [
        'partida',
        date,
        homeCode,
        'vs',
        awayCode,
        matchId.slice(0, 8),
        ts,
      ]
        .map(toSafeFilenameSegment)
        .filter(Boolean);

      const filename = `${segments.join('_')}.json`;

      downloadJson(filename, bundle);

      const failedCount = bundle.contexts.filter((c) => c.error).length;
      if (failedCount > 0) {
        setExportError(`Exportado com avisos: ${failedCount} recorte(s) falhou(aram).`);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setExportError(`Falha ao exportar: ${message}`);
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <PageLayout
      title="Análise da Partida"
      showBackButton
      backTo="/"
    >
      <Container size="md">
        {/* Sticky Controls + Jump */}
        <div className="sticky top-16 z-40 mb-6">
          <div className="bg-dark-primary/80 backdrop-blur-lg rounded-xl border border-dark-tertiary p-3">
            <div className="flex flex-col items-center gap-3">
              <FilterToggle value={filtro} onChange={setFiltro} />
              <PeriodoToggle value={periodo} onChange={setPeriodo} />
              <div className="w-full flex flex-col items-center gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  isLoading={isExporting}
                  onClick={handleExport}
                  disabled={!matchId}
                  className="w-full sm:w-auto"
                >
                  <Icon name="stats" size="sm" className="mr-2" />
                  Exportar JSON
                </Button>
                {exportError && (
                  <p className="text-[11px] text-warning text-center">{exportError}</p>
                )}
              </div>
              <div className="w-full">
                <JumpToSectionChips
                  sections={[
                    { id: 'sec-resumo', label: 'Resumo', icon: 'target' },
                    { id: 'sec-previsoes', label: 'Previsões', icon: 'stats' },
                    { id: 'sec-comparacoes', label: 'Comparações', icon: 'stats' },
                    { id: 'sec-disciplina', label: 'Disciplina', icon: 'card' },
                    { id: 'sec-mercados', label: 'Mercados', icon: 'stats' },
                    { id: 'sec-legenda', label: 'Legenda', icon: 'info' },
                  ]}
                />
              </div>
            </div>
          </div>
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
