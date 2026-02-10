import type { PeriodoFilter } from '@/types';

interface PeriodoToggleProps {
  value: PeriodoFilter;
  onChange: (value: PeriodoFilter) => void;
}

const options: { value: PeriodoFilter; label: string }[] = [
  { value: 'integral', label: 'Integral' },
  { value: '1T', label: '1T' },
  { value: '2T', label: '2T' },
];

export function PeriodoToggle({ value, onChange }: PeriodoToggleProps) {
  return (
    <div className="inline-flex bg-dark-tertiary rounded-full p-1 gap-1">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          type="button"
          className={`
            focus-ring px-5 py-2 rounded-full text-sm font-medium transition-all duration-200
            ${value === option.value
              ? 'bg-primary-500 text-dark-primary shadow-glow'
              : 'text-gray-400 hover:text-white hover:bg-dark-quaternary'
            }
          `}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
