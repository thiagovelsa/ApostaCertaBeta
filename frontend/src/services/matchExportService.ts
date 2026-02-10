import { getMatchStats } from './statsService';
import type { FiltroEstatisticas, MandoFilter, PeriodoFilter, StatsResponse } from '@/types';

export type ExportContextKey = 'selected' | 'last10_corridos' | 'last5_casa_fora';

export type ExportFilters = {
  filtro: FiltroEstatisticas;
  periodo: PeriodoFilter;
  homeMando: MandoFilter;
  awayMando: MandoFilter;
};

export interface ExportContext {
  key: ExportContextKey;
  label: string;
  endpoint: '/api/partida/{matchId}/analysis';
  params: {
    filtro: FiltroEstatisticas;
    periodo: PeriodoFilter;
    home_mando: MandoFilter;
    away_mando: MandoFilter;
    debug?: 0 | 1;
  };
  analysis: StatsResponse | null;
  error: string | null;
}

export interface MatchExportBundle {
  app: 'ApostaMestre';
  export_version: '1';
  generated_at: string;
  match_id: string;
  contexts: ExportContext[];
}

function tryGetAxiosDetail(err: unknown): string | null {
  if (!err || typeof err !== 'object') return null;

  const obj = err as Record<string, unknown>;
  const response = obj.response;
  if (!response || typeof response !== 'object') return null;

  const respObj = response as Record<string, unknown>;
  const data = respObj.data;
  if (!data || typeof data !== 'object') return null;

  const dataObj = data as Record<string, unknown>;
  const detail = dataObj.detail;
  if (typeof detail !== 'string') return null;

  const trimmed = detail.trim();
  return trimmed !== '' ? trimmed : null;
}

function formatErrorMessage(err: unknown): string {
  // Axios errors can carry useful details in response.data.detail.
  const detail = tryGetAxiosDetail(err);
  if (detail) return detail;
  return err instanceof Error ? err.message : String(err);
}

const EXPORT_ENDPOINT: ExportContext['endpoint'] = '/api/partida/{matchId}/analysis';

export async function buildMatchExportBundle(
  matchId: string,
  selected: ExportFilters
): Promise<MatchExportBundle> {
  const generatedAt = new Date().toISOString();

  const contextsToFetch: Array<{
    key: ExportContextKey;
    label: string;
    filters: ExportFilters;
  }> = [
    {
      key: 'selected',
      label: 'Recorte atual (tela)',
      filters: selected,
    },
    {
      key: 'last10_corridos',
      label: 'Últimos 10 corridos (sem mando)',
      filters: {
        filtro: '10',
        periodo: 'integral',
        homeMando: null,
        awayMando: null,
      },
    },
    {
      key: 'last5_casa_fora',
      label: 'Últimos 5 (mandante casa, visitante fora)',
      filters: {
        filtro: '5',
        periodo: 'integral',
        homeMando: 'casa',
        awayMando: 'fora',
      },
    },
  ];

  const contexts: ExportContext[] = await Promise.all(
    contextsToFetch.map(async (ctx) => {
      const { filtro, periodo, homeMando, awayMando } = ctx.filters;
      try {
        const analysis = await getMatchStats(
          matchId,
          filtro,
          periodo,
          homeMando,
          awayMando,
          true
        );
        return {
          key: ctx.key,
          label: ctx.label,
          endpoint: EXPORT_ENDPOINT,
          params: {
            filtro,
            periodo,
            home_mando: homeMando,
            away_mando: awayMando,
            debug: 1,
          },
          analysis,
          error: null,
        };
      } catch (err) {
        return {
          key: ctx.key,
          label: ctx.label,
          endpoint: EXPORT_ENDPOINT,
          params: {
            filtro,
            periodo,
            home_mando: homeMando,
            away_mando: awayMando,
            debug: 1,
          },
          analysis: null,
          error: formatErrorMessage(err),
        };
      }
    })
  );

  return {
    app: 'ApostaMestre',
    export_version: '1',
    generated_at: generatedAt,
    match_id: matchId,
    contexts,
  };
}
