/**
 * Utilities for exporting JSON files from the browser.
 */

/**
 * Produces a filesystem-friendly filename segment.
 *
 * - Removes accents/diacritics (NFD)
 * - Replaces any non-alphanumeric characters with "-"
 * - Collapses repeated "-"
 * - Trims leading/trailing "-"
 */
export function toSafeFilenameSegment(input: string): string {
  const raw = String(input ?? '');

  // Normalize + strip diacritics.
  const noAccents = raw.normalize('NFD').replace(/[\u0300-\u036f]/g, '');

  // Replace anything that isn't a letter or number with '-'.
  const dashed = noAccents.replace(/[^a-zA-Z0-9]+/g, '-');

  // Collapse repeated '-' and trim.
  return dashed.replace(/-+/g, '-').replace(/^-|-$/g, '');
}

export function downloadJson(filename: string, data: unknown): void {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json;charset=utf-8' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.rel = 'noopener';
  a.click();

  // Revoke on next tick to ensure the download has started.
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

