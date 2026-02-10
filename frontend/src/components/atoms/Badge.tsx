import { memo } from 'react';
import { type EstabilidadeLabel } from '@/types/stats';

interface BadgeProps {
  estabilidade: EstabilidadeLabel;
  size?: 'sm' | 'md';
  label?: string;
}

const badgeStyles: Record<EstabilidadeLabel, string> = {
  'Alta': 'bg-success/15 text-success border border-success/30',
  'Média': 'bg-warning/15 text-warning border border-warning/30',
  'Baixa': 'bg-danger/15 text-danger border border-danger/30',
  'N/A': 'bg-gray-500/15 text-gray-400 border border-gray-500/30',
};

export const Badge = memo(function Badge({ estabilidade, size = 'sm', label }: BadgeProps) {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClasses} ${badgeStyles[estabilidade]}`}
    >
      {label ? `${label} ${estabilidade}` : estabilidade}
    </span>
  );
});
