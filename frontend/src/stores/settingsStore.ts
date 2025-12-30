/**
 * Store de configurações para Busca Inteligente
 * Persiste preferências do usuário no localStorage
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { StatThresholds } from '@/types/smartSearch';

/**
 * Thresholds padrão por estatística (configuração relaxada)
 *
 * - overMin/underMin: 55% = mostra mais oportunidades
 * - confiancaMin: 65% = aceita confiança "Média-Alta"
 */
export const DEFAULT_STAT_THRESHOLDS: Record<string, StatThresholds> = {
  gols: { overMin: 0.55, underMin: 0.55, confiancaMin: 0.65 },
  escanteios: { overMin: 0.55, underMin: 0.55, confiancaMin: 0.65 },
  finalizacoes: { overMin: 0.55, underMin: 0.55, confiancaMin: 0.65 },
  finalizacoes_gol: { overMin: 0.55, underMin: 0.55, confiancaMin: 0.65 },
  cartoes_amarelos: { overMin: 0.55, underMin: 0.55, confiancaMin: 0.65 },
  faltas: { overMin: 0.55, underMin: 0.55, confiancaMin: 0.65 },
};

/**
 * Thresholds globais padrão (configuração relaxada)
 *
 * - probabilityCutoff (98%): Só filtra quase-certezas
 * - minEdge (15%): Aceita margens menores
 */
export const DEFAULT_GLOBAL_THRESHOLDS = {
  probabilityCutoff: 0.98,
  minEdge: 0.15,
};

interface GlobalThresholds {
  probabilityCutoff: number;
  minEdge: number;
}

interface SmartSearchSettingsState {
  // Visibilidade
  showOver: boolean;
  showUnder: boolean;

  // Thresholds globais
  globalThresholds: GlobalThresholds;

  // Thresholds por estatística
  statThresholds: Record<string, StatThresholds>;

  // Actions
  setShowOver: (show: boolean) => void;
  setShowUnder: (show: boolean) => void;
  setGlobalThreshold: <K extends keyof GlobalThresholds>(
    key: K,
    value: GlobalThresholds[K]
  ) => void;
  setStatThreshold: (
    stat: string,
    key: keyof StatThresholds,
    value: number
  ) => void;
  resetToDefaults: () => void;
}

export const useSmartSearchSettingsStore = create<SmartSearchSettingsState>()(
  persist(
    (set) => ({
      // Estado inicial
      showOver: true,
      showUnder: true,
      globalThresholds: { ...DEFAULT_GLOBAL_THRESHOLDS },
      statThresholds: { ...DEFAULT_STAT_THRESHOLDS },

      // Actions
      setShowOver: (show) => set({ showOver: show }),
      setShowUnder: (show) => set({ showUnder: show }),

      setGlobalThreshold: (key, value) =>
        set((state) => ({
          globalThresholds: { ...state.globalThresholds, [key]: value },
        })),

      setStatThreshold: (stat, key, value) =>
        set((state) => ({
          statThresholds: {
            ...state.statThresholds,
            [stat]: { ...state.statThresholds[stat], [key]: value },
          },
        })),

      resetToDefaults: () =>
        set({
          showOver: true,
          showUnder: true,
          globalThresholds: { ...DEFAULT_GLOBAL_THRESHOLDS },
          statThresholds: { ...DEFAULT_STAT_THRESHOLDS },
        }),
    }),
    {
      name: 'smart-search-settings',
      version: 1,
    }
  )
);
