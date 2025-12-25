import { create } from 'zustand';
import type { FiltroEstatisticas } from '@/types';

interface FilterState {
  filtro: FiltroEstatisticas;
  setFiltro: (filtro: FiltroEstatisticas) => void;
}

export const useFilterStore = create<FilterState>((set) => ({
  filtro: 'geral',
  setFiltro: (filtro) => set({ filtro }),
}));
