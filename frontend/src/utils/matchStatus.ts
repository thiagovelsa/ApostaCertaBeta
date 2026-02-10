export type MatchStatus = 'live' | 'soon' | 'finished' | 'scheduled';

function parseLocalDate(dateStr: string): { y: number; m: number; d: number } | null {
  const [y, m, d] = dateStr.split('-').map((n) => Number(n));
  if (!Number.isFinite(y) || !Number.isFinite(m) || !Number.isFinite(d)) return null;
  return { y, m, d };
}

function parseTime(timeStr: string): { hh: number; mm: number; ss: number } | null {
  const [hhRaw, mmRaw, ssRaw] = timeStr.split(':');
  const hh = Number(hhRaw);
  const mm = Number(mmRaw);
  const ss = Number(ssRaw ?? 0);
  if (!Number.isFinite(hh) || !Number.isFinite(mm) || !Number.isFinite(ss)) return null;
  return { hh, mm, ss };
}

function toLocalDateTime(dateStr: string, timeStr: string): Date | null {
  const d = parseLocalDate(dateStr);
  const t = parseTime(timeStr);
  if (!d || !t) return null;
  return new Date(d.y, d.m - 1, d.d, t.hh, t.mm, t.ss, 0);
}

/**
 * True if the match hasn't started yet (based on local device time).
 * Invalid/unknown date/time returns true so we don't hide matches unexpectedly.
 */
export function isMatchUpcoming(matchDateStr: string, matchTimeStr: string, now = new Date()): boolean {
  const matchDt = toLocalDateTime(matchDateStr, matchTimeStr);
  if (!matchDt) return true;
  return matchDt.getTime() >= now.getTime();
}

/**
 * Determine match status based on local time.
 * Note: pre-jogo only; for true live status prefer API-provided status if available.
 */
export function getMatchStatus(matchTimeStr: string): { status: MatchStatus; minutesUntil?: number };
export function getMatchStatus(matchDateStr: string, matchTimeStr: string): { status: MatchStatus; minutesUntil?: number };
export function getMatchStatus(
  a: string,
  b?: string
): { status: MatchStatus; minutesUntil?: number } {
  const now = new Date();

  const matchTime = b ? toLocalDateTime(a, b) : (() => {
    const t = parseTime(a);
    if (!t) return null;
    const dt = new Date();
    dt.setHours(t.hh, t.mm, t.ss, 0);
    return dt;
  })();

  if (!matchTime) {
    return { status: 'scheduled' };
  }

  const diffMs = matchTime.getTime() - now.getTime();
  const diffMinutes = Math.floor(diffMs / (1000 * 60));

  // Match is happening now (within 2 hour window after start)
  if (diffMinutes < 0 && diffMinutes > -120) {
    return { status: 'live' };
  }

  // Match starts within 30 minutes
  if (diffMinutes >= 0 && diffMinutes <= 30) {
    return { status: 'soon', minutesUntil: diffMinutes };
  }

  // Match finished (more than 2 hours ago)
  if (diffMinutes <= -120) {
    return { status: 'finished' };
  }

  // Scheduled for later
  return { status: 'scheduled' };
}
