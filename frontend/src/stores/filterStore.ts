import { create } from 'zustand';
import type { FiltroEstatisticas, MandoFilter } from '@/types';

interface FilterState {
  filtro: FiltroEstatisticas;
  homeMando: MandoFilter;
  awayMando: MandoFilter;
  setFiltro: (filtro: FiltroEstatisticas) => void;
  setHomeMando: (mando: MandoFilter) => void;
  setAwayMando: (mando: MandoFilter) => void;
  toggleHomeMando: (mando: 'casa' | 'fora') => void;
  toggleAwayMando: (mando: 'casa' | 'fora') => void;
}

export const useFilterStore = create<FilterState>((set, get) => ({
  filtro: 'geral',
  homeMando: null,
  awayMando: null,
  setFiltro: (filtro) => set({ filtro }),
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
