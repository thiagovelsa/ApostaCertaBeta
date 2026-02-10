interface ComparisonBarProps {
  home: number;
  away: number;
  label?: string;
  showValues?: boolean;
  height?: 'sm' | 'md';
}

export function ComparisonBar({
  home,
  away,
  label,
  showValues = true,
  height = 'sm',
}: ComparisonBarProps) {
  const total = home + away;
  const percentHome = total > 0 ? (home / total) * 100 : 50;
  const percentAway = total > 0 ? (away / total) * 100 : 50;

  const heightClass = height === 'sm' ? 'h-1.5' : 'h-2.5';

  return (
    <div className="w-full">
      {label && (
        <div className="mb-1">
          <div className="flex justify-between items-center">
            {showValues && (
              <span className="text-white font-medium text-sm">{home}</span>
            )}
            <span className="text-gray-400 text-xs uppercase tracking-wider flex-1 text-center">
              {label}
            </span>
            {showValues && (
              <span className="text-white font-medium text-sm">{away}</span>
            )}
          </div>
          <div className="text-[10px] text-gray-400 text-center">
            Relativo (não é probabilidade).
          </div>
        </div>
      )}
      <div
        className={`${heightClass} bg-dark-quaternary rounded-full overflow-hidden flex`}
        title="Comparação relativa entre as médias. Não representa probabilidade."
      >
        <div
          className="bg-primary-500 rounded-l-full transition-all duration-500"
          style={{ width: `${percentHome}%` }}
        />
        <div
          className="bg-gray-500 rounded-r-full transition-all duration-500"
          style={{ width: `${percentAway}%` }}
        />
      </div>
    </div>
  );
}
