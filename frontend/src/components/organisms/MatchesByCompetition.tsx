import type { PartidaResumo } from '@/types';
import { MatchCard } from '@/components/organisms/MatchCard';
import { Grid } from '@/components/layout';
import { StaggerList } from '@/components/motion/StaggerList';

function formatTime(horario: string): string {
  const parts = horario.split(':');
  return `${parts[0]}:${parts[1]}`;
}

export function MatchesByCompetition({
  matches,
  cols = 2,
}: {
  matches: PartidaResumo[];
  cols?: 1 | 2 | 3 | 4;
}) {
  const groups = new Map<string, PartidaResumo[]>();

  for (const m of matches) {
    const key = m.competicao || 'Outros';
    const arr = groups.get(key) ?? [];
    arr.push(m);
    groups.set(key, arr);
  }

  const entries = Array.from(groups.entries()).map(([competicao, ms]) => {
    const sorted = [...ms].sort((a, b) => (a.horario || '').localeCompare(b.horario || ''));
    return [competicao, sorted] as const;
  });

  // Sort groups by first match time so the day reads naturally.
  entries.sort((a, b) => {
    const at = a[1][0]?.horario ?? '';
    const bt = b[1][0]?.horario ?? '';
    return at.localeCompare(bt);
  });

  return (
    <div className="space-y-6">
      {entries.map(([competicao, ms]) => (
        <div key={competicao} className="space-y-3">
          <div className="sticky top-36 z-10 bg-dark-primary/80 backdrop-blur-lg py-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white truncate">{competicao}</h3>
              <span className="text-xs text-gray-400">
                {ms.length} jogo{ms.length === 1 ? '' : 's'} · {formatTime(ms[0].horario)}
              </span>
            </div>
          </div>

          <Grid cols={cols} gap="md">
            <StaggerList className="contents">
              {ms.map((m) => (
                <MatchCard key={m.id} match={m} />
              ))}
            </StaggerList>
          </Grid>
        </div>
      ))}
    </div>
  );
}
