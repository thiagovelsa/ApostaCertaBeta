import { Link } from 'react-router-dom';
import { TeamCard } from '@/components/molecules';
import { Icon } from '@/components/atoms';
import type { PartidaResumo } from '@/types';

interface MatchCardProps {
  match: PartidaResumo;
}

function formatTime(horario: string): string {
  // horario vem no formato HH:MM:SS
  const parts = horario.split(':');
  return `${parts[0]}:${parts[1]}`;
}

export function MatchCard({ match }: MatchCardProps) {
  return (
    <Link
      to={`/partida/${match.id}`}
      className="card-hover block group"
    >
      {/* Competition & Time Header */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs text-gray-500 uppercase tracking-wider truncate max-w-[60%]">
          {match.competicao}
        </span>
        <div className="flex items-center gap-1.5">
          <Icon name="clock" size="sm" className="text-gray-500" />
          <span className="text-sm text-gray-400">
            {formatTime(match.horario)}
          </span>
        </div>
      </div>

      {/* Teams */}
      <div className="flex items-center justify-between">
        <TeamCard team={match.mandante} isHome />

        {/* VS */}
        <div className="flex flex-col items-center px-4">
          <span className="text-gray-500 font-medium">VS</span>
        </div>

        <TeamCard team={match.visitante} isHome={false} />
      </div>

      {/* Stadium */}
      {match.estadio && (
        <div className="mt-3 text-center">
          <span className="text-xs text-gray-600">{match.estadio}</span>
        </div>
      )}

      {/* View Stats Hint */}
      <div className="mt-4 pt-3 border-t border-dark-tertiary flex items-center justify-center gap-2 text-gray-500 group-hover:text-primary-400 transition-colors">
        <Icon name="stats" size="sm" />
        <span className="text-sm">Ver estatísticas</span>
        <Icon name="chevron-right" size="sm" />
      </div>
    </Link>
  );
}
