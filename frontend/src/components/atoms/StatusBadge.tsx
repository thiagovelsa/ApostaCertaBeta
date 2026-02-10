import { Icon } from './Icon';
import { type MatchStatus } from '@/utils/matchStatus';

interface StatusBadgeProps {
    status: MatchStatus;
    /** Minutes until match starts (for 'soon' status display) */
    minutesUntil?: number;
}

const statusConfig = {
    live: {
        label: 'Ao Vivo',
        className: 'bg-accent-live/20 text-accent-live',
        icon: 'live' as const,
        pulse: true,
    },
    soon: {
        label: 'Em breve',
        className: 'bg-accent-soon/20 text-accent-soon',
        icon: 'clock' as const,
        pulse: false,
    },
    finished: {
        label: 'Finalizado',
        className: 'bg-gray-500/20 text-gray-400',
        icon: 'check' as const,
        pulse: false,
    },
    scheduled: {
        label: '',
        className: '',
        icon: null,
        pulse: false,
    },
};

export function StatusBadge({ status, minutesUntil }: StatusBadgeProps) {
    if (status === 'scheduled') {
        return null;
    }

    const config = statusConfig[status];
    const displayLabel = status === 'soon' && minutesUntil !== undefined
        ? `Em ${minutesUntil}min`
        : config.label;

    return (
        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
            {config.pulse && (
                <span className="relative flex h-2 w-2">
                    <span className="animate-ping motion-reduce:animate-none absolute inline-flex h-full w-full rounded-full bg-accent-live opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-live" />
                </span>
            )}
            {config.icon && !config.pulse && (
                <Icon name={config.icon} size="sm" />
            )}
            {displayLabel}
        </span>
    );
}
