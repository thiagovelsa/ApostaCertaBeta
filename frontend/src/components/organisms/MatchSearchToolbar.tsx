import { Button, Icon } from '@/components/atoms';

export type MatchesSort = 'time' | 'competition';
export type MatchesView = 'list' | 'insights';

interface MatchSearchToolbarProps {
  query: string;
  onQueryChange: (value: string) => void;
  sort: MatchesSort;
  onSortChange: (value: MatchesSort) => void;
  view: MatchesView;
  onViewChange: (value: MatchesView) => void;
  onlyUpcoming?: boolean;
  onOnlyUpcomingChange?: (value: boolean) => void;
  onRefresh?: () => void;
  onClearCache?: () => void;
  onSmartSearch?: () => void;
  smartSearchBusy?: boolean;
}

export function MatchSearchToolbar({
  query,
  onQueryChange,
  sort,
  onSortChange,
  view,
  onViewChange,
  onlyUpcoming,
  onOnlyUpcomingChange,
  onRefresh,
  onClearCache,
  onSmartSearch,
  smartSearchBusy,
}: MatchSearchToolbarProps) {
  return (
    <div className="bg-dark-secondary/80 backdrop-blur-lg rounded-xl border border-dark-tertiary p-3">
      <div className="flex flex-col gap-3">
        <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => onViewChange('list')}
              className={`focus-ring px-3 py-2 min-h-[44px] sm:min-h-0 rounded-lg text-sm font-medium transition-colors ${view === 'list'
                  ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                  : 'bg-dark-tertiary/40 text-gray-400 border border-dark-quaternary hover:text-white hover:bg-dark-tertiary'
                }`}
              aria-pressed={view === 'list'}
              type="button"
            >
              Partidas
            </button>
            <button
              onClick={() => onViewChange('insights')}
              className={`focus-ring px-3 py-2 min-h-[44px] sm:min-h-0 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${view === 'insights'
                  ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                  : 'bg-dark-tertiary/40 text-gray-400 border border-dark-quaternary hover:text-white hover:bg-dark-tertiary'
                }`}
              aria-pressed={view === 'insights'}
              type="button"
            >
              <Icon name="target" size="sm" />
              Análise Automática
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-2 justify-between sm:justify-end">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-gray-400">Ordenar</span>
              <select
                value={sort}
                onChange={(e) => onSortChange(e.target.value as MatchesSort)}
                className="bg-dark-tertiary/60 border border-dark-quaternary rounded-lg px-3 py-2 text-sm text-white focus-ring focus-visible:border-primary-500"
              >
                <option value="time">Horário</option>
                <option value="competition">Competição</option>
              </select>

              {onOnlyUpcomingChange && (
                <button
                  type="button"
                  onClick={() => onOnlyUpcomingChange(!onlyUpcoming)}
                  aria-pressed={!!onlyUpcoming}
                  className={`focus-ring px-3 py-2 min-h-[44px] sm:min-h-0 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
                    onlyUpcoming
                      ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                      : 'bg-dark-tertiary/40 text-gray-400 border border-dark-quaternary hover:text-white hover:bg-dark-tertiary'
                  }`}
                  title="Oculta partidas que já começaram ou já terminaram."
                >
                  <Icon name="clock" size="sm" />
                  Só futuras
                </button>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {onSmartSearch && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={onSmartSearch}
                  disabled={smartSearchBusy}
                  className="relative"
                >
                  <span className="relative flex h-2 w-2 mr-2">
                    <span className="animate-ping motion-reduce:animate-none absolute inline-flex h-full w-full rounded-full bg-dark-primary opacity-40" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-dark-primary" />
                  </span>
                  Análise Automática
                </Button>
              )}
              {onClearCache && (
                <Button variant="ghost" size="sm" onClick={onClearCache}>
                  <Icon name="refresh" size="sm" className="mr-1" />
                  Reiniciar
                </Button>
              )}
              {onRefresh && (
                <Button variant="ghost" size="sm" onClick={onRefresh}>
                  <Icon name="refresh" size="sm" className="mr-1" />
                  Atualizar
                </Button>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Icon name="search" size="sm" className="text-gray-400" />
          <input
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            className="input-field w-full"
            placeholder="Buscar por time, competição ou estádio…"
          />
        </div>
      </div>
    </div>
  );
}
