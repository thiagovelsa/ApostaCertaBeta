import { useEffect, useMemo, useRef, useState } from 'react';
import type { PartidaResumo } from '@/types';
import { MatchCard } from '@/components/organisms/MatchCard';

type Cols = 1 | 2 | 3 | 4;

const colStyles: Record<Cols, string> = {
  1: 'grid-cols-1',
  2: 'grid-cols-1 md:grid-cols-2',
  3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
};

const gapStyles: Record<'sm' | 'md' | 'lg', string> = {
  sm: 'gap-3',
  md: 'gap-4',
  lg: 'gap-6',
};

function useResizeObserver(elRef: React.RefObject<HTMLElement | null>) {
  const [rect, setRect] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const el = elRef.current;
    if (!el) return;

    const obs = new ResizeObserver((entries) => {
      const cr = entries[0]?.contentRect;
      if (!cr) return;
      setRect({ width: cr.width, height: cr.height });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, [elRef]);

  return rect;
}

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

export function VirtualizedMatchesGrid({
  matches,
  cols = 2,
  gap = 'md',
  estimatedItemHeight = 210,
  overscanRows = 6,
  className = '',
}: {
  matches: PartidaResumo[];
  cols?: Cols;
  gap?: 'sm' | 'md' | 'lg';
  estimatedItemHeight?: number;
  overscanRows?: number;
  className?: string;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const { width: viewportWidth, height: viewportHeight } = useResizeObserver(containerRef);
  // Track scroll by row to avoid re-rendering on every pixel scroll.
  const [scrollRow, setScrollRow] = useState(0);
  const lastRowRef = useRef(0);

  // Count columns based on breakpoint. We mirror Tailwind grid col rules.
  const columns = useMemo(() => {
    const w = viewportWidth;
    if (cols === 1) return 1;
    if (cols === 2) return w >= 768 ? 2 : 1;
    if (cols === 3) return w >= 1024 ? 3 : w >= 768 ? 2 : 1;
    // cols === 4
    if (w >= 1280) return 4;
    if (w >= 1024) return 3;
    if (w >= 640) return 2;
    return 1;
  }, [cols, viewportWidth]);

  const rows = Math.max(1, Math.ceil(matches.length / columns));
  const totalHeight = rows * estimatedItemHeight;

  const visible = useMemo(() => {
    const vh = viewportHeight || (typeof window !== 'undefined' ? window.innerHeight : 800);
    const scrollTop = scrollRow * estimatedItemHeight;
    const startRow = scrollRow;
    const endRow = Math.ceil((scrollTop + vh) / estimatedItemHeight);
    const fromRow = clamp(startRow - overscanRows, 0, rows);
    const toRow = clamp(endRow + overscanRows, 0, rows);

    const fromIdx = fromRow * columns;
    const toIdx = Math.min(matches.length, toRow * columns);

    return {
      fromRow,
      toRow,
      fromIdx,
      toIdx,
      padTop: fromRow * estimatedItemHeight,
      padBottom: Math.max(0, totalHeight - toRow * estimatedItemHeight),
    };
  }, [columns, estimatedItemHeight, matches.length, overscanRows, rows, scrollRow, totalHeight, viewportHeight]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const onScroll = () => {
      const row = Math.floor(el.scrollTop / estimatedItemHeight);
      if (row !== lastRowRef.current) {
        lastRowRef.current = row;
        setScrollRow(row);
      }
    };
    el.addEventListener('scroll', onScroll, { passive: true });
    return () => el.removeEventListener('scroll', onScroll);
  }, [estimatedItemHeight]);

  const slice = matches.slice(visible.fromIdx, visible.toIdx);

  return (
    <div
      ref={containerRef}
      className={`relative overflow-auto max-h-[calc(100vh-240px)] scrollbar-thin ${className}`}
      aria-label="Lista de partidas"
    >
      <div style={{ height: visible.padTop }} aria-hidden />

      <div className={`grid ${colStyles[cols]} ${gapStyles[gap]}`}>
        {slice.map((match) => (
          <MatchCard key={match.id} match={match} />
        ))}
      </div>

      <div style={{ height: visible.padBottom }} aria-hidden />
    </div>
  );
}
