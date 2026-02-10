import { Icon, type IconName } from '@/components/atoms';
import { ComparisonBar } from '@/components/molecules';
import type { EstatisticaFeitos } from '@/types';

interface StatsCategoryProps {
  title: string;
  icon: IconName;
  homeStats: EstatisticaFeitos;
  awayStats: EstatisticaFeitos;
}

export function StatsCategory({ title, icon, homeStats, awayStats }: StatsCategoryProps) {
  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-dark-tertiary">
        <Icon name={icon} size="md" className="text-primary-400" />
        <h3 className="font-semibold text-white">{title}</h3>
      </div>

      {/* Stats List */}
      <div className="space-y-4">
        <ComparisonBar
          home={homeStats.feitos.media}
          away={awayStats.feitos.media}
          label="Feitos"
          height="md"
        />
        <ComparisonBar
          home={homeStats.sofridos.media}
          away={awayStats.sofridos.media}
          label="Sofridos"
          height="md"
        />
      </div>
    </div>
  );
}
