import { type CVClassificacao } from '@/types';

interface BadgeProps {
  classificacao: CVClassificacao;
  size?: 'sm' | 'md';
}

const badgeStyles: Record<CVClassificacao, string> = {
  'Muito Estável': 'bg-success/20 text-success',
  'Estável': 'bg-primary-500/20 text-primary-400',
  'Moderado': 'bg-warning/20 text-warning',
  'Instável': 'bg-orange-500/20 text-orange-400',
  'Muito Instável': 'bg-danger/20 text-danger',
};

export function Badge({ classificacao, size = 'sm' }: BadgeProps) {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClasses} ${badgeStyles[classificacao]}`}
    >
      {classificacao}
    </span>
  );
}
