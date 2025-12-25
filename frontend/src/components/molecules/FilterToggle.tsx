import type { FiltroEstatisticas } from '@/types';

interface FilterToggleProps {
  value: FiltroEstatisticas;
  onChange: (value: FiltroEstatisticas) => void;
}

const options: { value: FiltroEstatisticas; label: string }[] = [
  { value: 'geral', label: 'Temporada' },
  { value: '10', label: 'Últimos 10' },
  { value: '5', label: 'Últimos 5' },
];

export function FilterToggle({ value, onChange }: FilterToggleProps) {
  return (
    <div className="inline-flex bg-dark-tertiary rounded-lg p-1 gap-1">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`
            px-4 py-2 rounded-md text-sm font-medium transition-all duration-200
            ${
              value === option.value
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
