import { Badge } from '@/components/atoms';
import { toEstabilidadeLabel } from '@/types/stats';
import type { EstatisticaMetrica } from '@/types';

interface StatMetricProps {
  label: string;
  home: EstatisticaMetrica;
  away: EstatisticaMetrica;
  showCV?: boolean;
}

export function StatMetric({ label, home, away, showCV = true }: StatMetricProps) {
  const total = home.media + away.media;
  const percentHome = total > 0 ? (home.media / total) * 100 : 50;
  const percentAway = total > 0 ? (away.media / total) * 100 : 50;

  return (
    <div className="py-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-white font-semibold text-lg">{home.media.toFixed(1)}</span>
          {showCV && (
            <Badge estabilidade={toEstabilidadeLabel(home.classificacao)} size="sm" />
          )}
        </div>

        <span className="text-gray-400 text-sm font-medium uppercase tracking-wider">
          {label}
        </span>

        <div className="flex items-center gap-2">
          {showCV && (
            <Badge estabilidade={toEstabilidadeLabel(away.classificacao)} size="sm" />
          )}
          <span className="text-white font-semibold text-lg">{away.media.toFixed(1)}</span>
        </div>
      </div>

      {/* Comparison Bar */}
      <div
        className="h-2 bg-dark-tertiary rounded-full overflow-hidden flex"
        title="Comparação relativa entre as médias. Não representa probabilidade."
      >
        <div
          className="bg-primary-500 transition-all duration-500"
          style={{ width: `${percentHome}%` }}
        />
        <div
          className="bg-gray-600 transition-all duration-500"
          style={{ width: `${percentAway}%` }}
        />
      </div>

      <div className="mt-1 text-[10px] text-gray-400 text-center">
        Comparação relativa (não é probabilidade).
      </div>

      {/* CV Values */}
      {showCV && (
        <div className="flex justify-between mt-1 text-xs text-gray-400">
          <span>CV: {(home.cv * 100).toFixed(0)}%</span>
          <span>CV: {(away.cv * 100).toFixed(0)}%</span>
        </div>
      )}
    </div>
  );
}
