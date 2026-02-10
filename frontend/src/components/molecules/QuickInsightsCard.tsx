import { memo } from 'react';
import { Icon } from '@/components/atoms';
import type { MatchInsight } from '@/utils/insights';
import { formatPercent } from '@/utils/chance';

function pillColor(type: 'opportunity' | 'avoid') {
  return type === 'opportunity'
    ? 'bg-success/15 text-success border border-success/20'
    : 'bg-danger/15 text-danger border border-danger/20';
}

export const QuickInsightsCard = memo(function QuickInsightsCard({
  title,
  insights,
}: {
  title: string;
  insights: MatchInsight[];
}) {
  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary">
      <div className="flex items-center gap-2 mb-3">
        <Icon name="target" size="sm" className="text-primary-400" />
        <h3 className="text-sm font-medium text-white">{title}</h3>
      </div>

      {insights.length === 0 ? (
        <p className="text-sm text-gray-400">Sem destaques para os filtros atuais.</p>
      ) : (
        <div className="space-y-3">
          {insights.map((i, idx) => (
            <div key={`${i.statKey}-${idx}`} className="bg-dark-tertiary/20 rounded-lg p-3">
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-white truncate">
                    {i.statLabel}: <span className="text-gray-300 font-medium">{i.marketLabel}</span>
                  </p>
                  <p className="text-xs text-gray-400 mt-1">{i.reason}</p>
                  <div className="text-[11px] text-gray-400 mt-2 flex flex-wrap gap-x-3 gap-y-1 tabular-nums">
                    <span>Modelo {formatPercent(i.chanceModel)}</span>
                    <span>Confiança do modelo: {i.confidenceLabel}</span>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-2 flex-shrink-0">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${pillColor(i.type)}`}>
                    {i.type === 'opportunity' ? 'Oportunidade' : 'Evitar'}
                  </span>
                  <div className="text-right">
                    <div className="text-lg font-bold text-white tabular-nums">
                      {formatPercent(i.chanceAdj)}
                    </div>
                    <div className="text-[11px] text-gray-400">Probabilidade ajustada</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
});
