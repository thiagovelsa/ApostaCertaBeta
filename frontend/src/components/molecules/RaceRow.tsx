import { RaceDot } from '@/components/atoms';

interface RaceRowProps {
  results: ('W' | 'D' | 'L')[];
  maxItems?: number;
  label?: string;
  reverse?: boolean;
}

export function RaceRow({ results, maxItems = 5, label, reverse = false }: RaceRowProps) {
  const displayResults = results.slice(0, maxItems);

  return (
    <div className={`flex items-center gap-2 ${reverse ? 'flex-row-reverse' : ''}`}>
      {label && (
        <span className="text-xs text-gray-500 uppercase tracking-wider">{label}</span>
      )}
      <div className={`flex gap-1 ${reverse ? 'flex-row-reverse' : ''}`}>
        {displayResults.map((result, index) => (
          <RaceDot key={index} result={result} size="md" />
        ))}
      </div>
    </div>
  );
}
