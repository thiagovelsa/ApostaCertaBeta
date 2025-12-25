import { useQuery } from '@tanstack/react-query';
import { getPartidasByDate } from '@/services/partidasService';

interface UsePartidasOptions {
  enabled?: boolean;
}

/**
 * Hook para buscar partidas de uma data específica
 * staleTime: 1 hora (partidas não mudam com frequência)
 * enabled: controla se a busca deve ser executada (padrão: false)
 */
export function usePartidas(date: string, options: UsePartidasOptions = {}) {
  const { enabled = false } = options;

  return useQuery({
    queryKey: ['partidas', date],
    queryFn: () => getPartidasByDate(date),
    staleTime: 1000 * 60 * 60, // 1 hour
    enabled: Boolean(date) && enabled,
  });
}
