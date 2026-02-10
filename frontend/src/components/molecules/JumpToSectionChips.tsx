import { Icon, type IconName } from '@/components/atoms';

export interface JumpSection {
  id: string;
  label: string;
  icon?: IconName;
}

function highlightSection(el: HTMLElement) {
  el.classList.add('ring-1', 'ring-primary-500/40', 'shadow-glow');
  window.setTimeout(() => {
    el.classList.remove('ring-1', 'ring-primary-500/40', 'shadow-glow');
  }, 900);
}

export function JumpToSectionChips({ sections }: { sections: JumpSection[] }) {
  const onJump = (id: string) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    highlightSection(el);
  };

  return (
    <div className="flex flex-wrap items-center gap-2 py-1">
      <span className="text-sm text-gray-400 flex-shrink-0 font-medium">Pular para</span>
      {sections.map((s) => (
        <button
          key={s.id}
          onClick={() => onJump(s.id)}
          className="focus-ring flex items-center gap-1 px-3 py-2 sm:py-1.5 min-h-[44px] sm:min-h-0 rounded-full text-xs font-medium border border-dark-quaternary bg-dark-tertiary/60 text-gray-300 hover:text-white hover:border-primary-500/40 hover:bg-dark-tertiary transition-all duration-200"
          type="button"
        >
          {s.icon && <Icon name={s.icon} size="sm" className="text-primary-400" />}
          {s.label}
        </button>
      ))}
    </div>
  );
}
