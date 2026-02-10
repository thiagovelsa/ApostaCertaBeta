/**
 * Hook para Busca Inteligente
 * Analisa todas as partidas do dia e identifica oportunidades de aposta
 */

import { useState, useCallback } from 'react';
import { getPartidasByDate } from '@/services/partidasService';
import { getMatchStats } from '@/services/statsService';
import { analisarPartida, criarResultado, type AnalysisConfig } from '@/utils/smartSearch';
import { useSmartSearchSettingsStore } from '@/stores';
import type {
  SmartSearchResult,
  SmartSearchProgress,
  Oportunidade,
  StatsResponse,
  PartidaResumo,
} from '@/types';

/**
 * Configuração de rate limiting
 */
const BATCH_SIZE = 5; // Requests paralelos
const BATCH_DELAY = 100; // ms entre batches

/**
 * Estado do hook
 */
interface SmartSearchState {
  isLoading: boolean;
  isAnalyzing: boolean;
  progress: SmartSearchProgress | null;
  result: SmartSearchResult | null;
  error: Error | null;
}

/**
 * Retorno do hook
 */
interface UseSmartSearchReturn extends SmartSearchState {
  search: (date: string) => Promise<void>;
  reset: () => void;
}

/**
 * Delay helper
 */
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Processa partidas em batches com rate limiting
 */
async function processarEmBatches<T, R>(
  items: T[],
  processor: (item: T, index: number) => Promise<R>,
  onProgress: (completed: number, total: number) => void,
  batchSize: number = BATCH_SIZE,
  batchDelay: number = BATCH_DELAY
): Promise<R[]> {
  const results: R[] = [];

  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);

    const batchResults = await Promise.allSettled(
      batch.map((item, idx) => processor(item, i + idx))
    );

    for (const result of batchResults) {
      if (result.status === 'fulfilled') {
        results.push(result.value);
      }
    }

    onProgress(Math.min(i + batchSize, items.length), items.length);

    // Delay entre batches (exceto no último)
    if (i + batchSize < items.length) {
      await delay(batchDelay);
    }
  }

  return results;
}

/**
 * Hook principal de Busca Inteligente
 */
export function useSmartSearch(): UseSmartSearchReturn {
  const [state, setState] = useState<SmartSearchState>({
    isLoading: false,
    isAnalyzing: false,
    progress: null,
    result: null,
    error: null,
  });

  // Configurações do store
  const { showOver, showUnder, globalThresholds, statThresholds } =
    useSmartSearchSettingsStore();

  const reset = useCallback(() => {
    setState({
      isLoading: false,
      isAnalyzing: false,
      progress: null,
      result: null,
      error: null,
    });
  }, []);

  const search = useCallback(async (date: string) => {
    // Monta configuração de análise a partir do store
    const config: AnalysisConfig = {
      probabilityCutoff: globalThresholds.probabilityCutoff,
      minEdge: globalThresholds.minEdge,
      statThresholds,
      showOver,
      showUnder,
    };
    setState(prev => ({
      ...prev,
      isLoading: true,
      isAnalyzing: false,
      progress: null,
      result: null,
      error: null,
    }));

    try {
      // 1. Buscar partidas do dia
      const partidasResponse = await getPartidasByDate(date);
      const partidas = partidasResponse.partidas;

      if (partidas.length === 0) {
        setState(prev => ({
          ...prev,
          isLoading: false,
          result: {
            partidas_analisadas: 0,
            partidas_com_oportunidades: 0,
            total_oportunidades: 0,
            oportunidades: [],
            timestamp: new Date().toISOString(),
          },
        }));
        return;
      }

      setState(prev => ({
        ...prev,
        isLoading: false,
        isAnalyzing: true,
        progress: {
          total: partidas.length,
          analisadas: 0,
          porcentagem: 0,
        },
      }));

      // 2. Buscar stats de cada partida em batch
      const todasOportunidades: Oportunidade[] = [];

      const resultados = await processarEmBatches<
        PartidaResumo,
        { partida: PartidaResumo; stats: StatsResponse } | null
      >(
        partidas,
        async (partida) => {
          try {
            // Preferimos "10 corridos" por velocidade (menos chamadas/menos dados).
            const stats = await getMatchStats(partida.id, '10');
            return { partida, stats };
          } catch {
            // Ignora partidas com erro (ex: sem dados suficientes)
            return null;
          }
        },
        (completed, total) => {
          setState(prev => ({
            ...prev,
            progress: {
              total,
              analisadas: completed,
              porcentagem: Math.round((completed / total) * 100),
            },
          }));
        }
      );

      // 3. Analisar cada resultado e calcular oportunidades
      for (const resultado of resultados) {
        if (!resultado) continue;

        const { partida, stats } = resultado;

        try {
          const overUnder = stats.over_under;
          if (!overUnder) {
            continue;
          }

          // Analisar e extrair oportunidades
          const oportunidades = analisarPartida(partida, stats, overUnder, config);
          todasOportunidades.push(...oportunidades);
        } catch {
          // Ignora erros de cálculo
          continue;
        }
      }

      // 4. Criar resultado final
      const resultado = criarResultado(
        todasOportunidades,
        resultados.filter(r => r !== null).length
      );

      setState(prev => ({
        ...prev,
        isAnalyzing: false,
        progress: null,
        result: resultado,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        isAnalyzing: false,
        progress: null,
        error: error instanceof Error ? error : new Error('Erro desconhecido'),
      }));
    }
  }, [showOver, showUnder, globalThresholds, statThresholds]);

  return {
    ...state,
    search,
    reset,
  };
}
