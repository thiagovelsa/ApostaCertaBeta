interface TeamBadgeProps {
  src?: string;
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

export function TeamBadge({ src, alt, size = 'md', className = '' }: TeamBadgeProps) {
  const fallbackSrc = '/placeholder-badge.svg';

  return (
    <div
      className={`
        rounded-full bg-dark-tertiary flex items-center justify-center overflow-hidden
        ${sizeStyles[size]} ${className}
      `}
    >
      <img
        src={src || fallbackSrc}
        alt={alt}
        className="h-full w-full object-contain p-1"
        onError={(e) => {
          const target = e.target as HTMLImageElement;
          target.src = fallbackSrc;
        }}
      />
    </div>
  );
}
