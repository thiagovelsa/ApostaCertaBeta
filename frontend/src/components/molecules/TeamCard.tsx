import { TeamBadge, RaceDot } from '@/components/atoms';
import type { TimeInfo } from '@/types';

interface TeamCardProps {
  team: TimeInfo;
  isHome?: boolean;
  recentForm?: ('W' | 'D' | 'L')[];
}

export function TeamCard({ team, isHome = false, recentForm }: TeamCardProps) {
  return (
    <div className={`flex items-center gap-3 ${isHome ? '' : 'flex-row-reverse'}`}>
      <TeamBadge src={team.escudo ?? undefined} alt={team.nome} size="lg" />
      <div className={`flex flex-col ${isHome ? 'items-start' : 'items-end'}`}>
        <span className="font-semibold text-white truncate max-w-[140px]">
          {team.nome}
        </span>
        {team.codigo && (
          <span className="text-xs text-gray-500 uppercase tracking-wider">
            {team.codigo}
          </span>
        )}
        {recentForm && recentForm.length > 0 && (
          <div className={`flex gap-1 mt-1 ${isHome ? '' : 'flex-row-reverse'}`}>
            {recentForm.slice(0, 5).map((result, index) => (
              <RaceDot key={index} result={result} size="sm" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
