import { api } from './api';
import type { PartidaListResponse } from '@/types';

/**
 * Busca partidas para uma data específica
 */
export async function getPartidasByDate(date: string): Promise<PartidaListResponse> {
  const response = await api.get<PartidaListResponse>('/api/partidas', {
    params: { data: date },
  });
  return response.data;
}

/**
 * Busca partidas para hoje
 */
export async function getPartidasHoje(): Promise<PartidaListResponse> {
  const today = new Date().toISOString().split('T')[0];
  return getPartidasByDate(today);
}
