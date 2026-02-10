import { create } from 'zustand';
import type { FiltroEstatisticas, MandoFilter, PeriodoFilter } from '@/types';

interface FilterState {
  filtro: FiltroEstatisticas;
  periodo: PeriodoFilter;
  homeMando: MandoFilter;
  awayMando: MandoFilter;
  setFiltro: (filtro: FiltroEstatisticas) => void;
  setPeriodo: (periodo: PeriodoFilter) => void;
  setHomeMando: (mando: MandoFilter) => void;
  setAwayMando: (mando: MandoFilter) => void;
  toggleHomeMando: (mando: 'casa' | 'fora') => void;
  toggleAwayMando: (mando: 'casa' | 'fora') => void;
}

export const useFilterStore = create<FilterState>((set) => ({
  filtro: 'geral',
  periodo: 'integral',
  // Default pre-jogo: mandante em casa / visitante fora (alinha com o backend).
  homeMando: 'casa',
  awayMando: 'fora',
  setFiltro: (filtro) => set({ filtro }),
  setPeriodo: (periodo) => set({ periodo }),
  setHomeMando: (mando) => set({ homeMando: mando }),
  setAwayMando: (mando) => set({ awayMando: mando }),
  // Toggle: se já está ativo, desativa; se não, ativa
  toggleHomeMando: (mando) => set((state) => ({
    homeMando: state.homeMando === mando ? null : mando
  })),
  toggleAwayMando: (mando) => set((state) => ({
    awayMando: state.awayMando === mando ? null : mando
  })),
}));
