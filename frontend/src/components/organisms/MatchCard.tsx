import { memo } from 'react';
import { Link } from 'react-router-dom';
import { TeamCard } from '@/components/molecules';
import { Icon, StatusBadge, getMatchStatus } from '@/components/atoms';
import type { PartidaResumo } from '@/types';

interface MatchCardProps {
  match: PartidaResumo;
}

function formatTime(horario: string): string {
  // horario vem no formato HH:MM:SS
  const parts = horario.split(':');
  return `${parts[0]}:${parts[1]}`;
}

function MatchCardInner({ match }: MatchCardProps) {
  const { status, minutesUntil } = getMatchStatus(match.data, match.horario);

  // Gradient color based on status
  const gradientClass = status === 'live'
    ? 'from-accent-live/30 via-accent-live/10 to-transparent'
    : status === 'soon'
      ? 'from-accent-soon/20 via-accent-soon/5 to-transparent'
      : 'from-primary-500/20 via-primary-500/5 to-transparent';

  return (
    <Link
      to={`/partida/${match.id}`}
      className="card-hover block group relative overflow-hidden"
    >
      {/* Gradient Accent Top */}
      <div
        className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${gradientClass} opacity-50 group-hover:opacity-100 transition-opacity duration-300`}
      />

      {/* Competition & Time Header */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs text-gray-400 uppercase tracking-wider truncate max-w-[50%] font-medium">
          {match.competicao}
        </span>
        <div className="flex items-center gap-2">
          <StatusBadge status={status} minutesUntil={minutesUntil} />
        <div className="flex items-center gap-1.5">
          <Icon name="clock" size="sm" className="text-gray-400" />
            <span className="text-sm text-gray-400 font-medium font-mono tabular-nums">
              {formatTime(match.horario)}
            </span>
          </div>
        </div>
      </div>

      {/* Teams */}
      <div className="flex items-center justify-between">
        <TeamCard team={match.mandante} isHome />

        {/* VS Badge */}
        <div className="flex flex-col items-center px-4">
          <span className="text-gray-400 font-bold text-sm group-hover:text-primary-500/50 transition-colors">
            VS
          </span>
        </div>

        <TeamCard team={match.visitante} isHome={false} />
      </div>

      {/* Stadium */}
      {match.estadio && (
        <div className="mt-3 text-center">
          <span className="text-xs text-gray-400">{match.estadio}</span>
        </div>
      )}

      {/* CTA Footer */}
      <div className="mt-4 pt-3 border-t border-dark-tertiary flex items-center justify-center gap-2 text-gray-400 group-hover:text-primary-400 transition-colors">
        <Icon name="stats" size="sm" />
        <span className="text-sm font-medium">Abrir análise</span>
        <Icon name="chevron-right" size="sm" className="group-hover:translate-x-0.5 transition-transform" />
      </div>
    </Link>
  );
}

export const MatchCard = memo(MatchCardInner, (prev, next) => {
  // Avoid re-rendering when the match identity and display-critical fields are the same.
  // This helps when filtering/sorting changes cause parent re-renders.
  return (
    prev.match.id === next.match.id &&
    prev.match.horario === next.match.horario &&
    prev.match.data === next.match.data &&
    prev.match.competicao === next.match.competicao &&
    prev.match.estadio === next.match.estadio &&
    prev.match.mandante?.id === next.match.mandante?.id &&
    prev.match.visitante?.id === next.match.visitante?.id
  );
});
