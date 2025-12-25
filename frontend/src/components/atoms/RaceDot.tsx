type Result = 'W' | 'D' | 'L';

interface RaceDotProps {
  result: Result;
  size?: 'sm' | 'md';
}

const resultStyles: Record<Result, string> = {
  W: 'bg-success',
  D: 'bg-warning',
  L: 'bg-danger',
};

const resultTitles: Record<Result, string> = {
  W: 'Vitória',
  D: 'Empate',
  L: 'Derrota',
};

export function RaceDot({ result, size = 'sm' }: RaceDotProps) {
  const sizeClass = size === 'sm' ? 'h-2 w-2' : 'h-3 w-3';

  return (
    <span
      className={`inline-block rounded-full ${sizeClass} ${resultStyles[result]}`}
      title={resultTitles[result]}
    />
  );
}
