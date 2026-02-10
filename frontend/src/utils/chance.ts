export function clamp01(x: number): number {
  if (!Number.isFinite(x)) return 0;
  return Math.max(0, Math.min(1, x));
}

/**
 * Chance ajustada: p_adj = 0.5 + (p - 0.5) * c_line
 * - confidence: 0..1 (qualidade do modelo)
 * - uncertainty: 0..1 (largura relativa do IC/variabilidade na linha)
 */
export function calcAdjustedChance(
  p: number,
  confidence: number,
  uncertainty: number = 0
): number {
  const p0 = clamp01(p);
  const c = clamp01(confidence) * (1 - clamp01(uncertainty));
  return clamp01(0.5 + (p0 - 0.5) * clamp01(c));
}

export function formatPercent(p: number): string {
  const x = clamp01(p);
  if (x < 0.01) return '<1%';
  if (x > 0.99) return '>99%';
  return `${Math.round(x * 100)}%`;
}

