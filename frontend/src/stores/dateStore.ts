import { create } from 'zustand';

/**
 * Formata uma data para o formato YYYY-MM-DD
 */
function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Parse de string YYYY-MM-DD para Date (evita problemas de timezone)
 */
function parseDate(dateStr: string): Date {
  const [year, month, day] = dateStr.split('-').map(Number);
  return new Date(year, month - 1, day);
}

interface DateState {
  selectedDate: string;
  setSelectedDate: (date: string) => void;
  goToToday: () => void;
  goToPreviousDay: () => void;
  goToNextDay: () => void;
}

export const useDateStore = create<DateState>((set, get) => ({
  selectedDate: formatDate(new Date()),

  setSelectedDate: (date: string) => set({ selectedDate: date }),

  goToToday: () => set({ selectedDate: formatDate(new Date()) }),

  goToPreviousDay: () => {
    const current = parseDate(get().selectedDate);
    current.setDate(current.getDate() - 1);
    set({ selectedDate: formatDate(current) });
  },

  goToNextDay: () => {
    const current = parseDate(get().selectedDate);
    current.setDate(current.getDate() + 1);
    set({ selectedDate: formatDate(current) });
  },
}));
