import { type EstabilidadeLabel } from '@/types/stats';

interface BadgeProps {
  estabilidade: EstabilidadeLabel;
  size?: 'sm' | 'md';
  label?: string;
}

const badgeStyles: Record<EstabilidadeLabel, string> = {
  'Alta': 'bg-success/20 text-success',
  'Média': 'bg-warning/20 text-warning',
  'Baixa': 'bg-danger/20 text-danger',
  'N/A': 'bg-gray-500/20 text-gray-400',
};

export function Badge({ estabilidade, size = 'sm', label }: BadgeProps) {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClasses} ${badgeStyles[estabilidade]}`}
    >
      {label ? `${label} ${estabilidade}` : estabilidade}
    </span>
  );
}
