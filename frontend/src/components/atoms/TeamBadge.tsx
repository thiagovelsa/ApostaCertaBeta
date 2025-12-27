import { getTeamLogoPath } from '@/utils/teamLogos';

interface TeamBadgeProps {
  /** URL externa da logo (fallback se não houver logo local) */
  src?: string;
  /** Nome do time - usado para buscar logo local */
  alt: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeStyles = {
  sm: 'h-6 w-6',
  md: 'h-10 w-10',
  lg: 'h-14 w-14',
  xl: 'h-20 w-20',
};

/**
 * Componente de badge/escudo de time
 *
 * Prioridade de fontes:
 * 1. Logo local (baseado no nome do time via `alt`)
 * 2. URL externa (`src`)
 * 3. Placeholder padrão
 */
export function TeamBadge({ src, alt, size = 'md', className = '' }: TeamBadgeProps) {
  const fallbackSrc = '/placeholder-badge.svg';

  // Tenta buscar logo local pelo nome do time
  const localLogo = getTeamLogoPath(alt);

  // Prioridade: local > externo > placeholder
  const primarySrc = localLogo || src || fallbackSrc;

  // Sem fundo quando tem logo local (já tem design próprio)
  const bgClass = localLogo ? '' : 'bg-dark-tertiary';

  return (
    <div
      className={`
        rounded-full flex items-center justify-center overflow-hidden
        ${bgClass} ${sizeStyles[size]} ${className}
      `}
    >
      <img
        src={primarySrc}
        alt={alt}
        className="h-full w-full object-contain"
        onError={(e) => {
          const target = e.target as HTMLImageElement;
          // Se local falhou, tenta externo; senão placeholder
          if (localLogo && target.src.includes(localLogo)) {
            target.src = src || fallbackSrc;
          } else {
            target.src = fallbackSrc;
          }
        }}
      />
    </div>
  );
}
