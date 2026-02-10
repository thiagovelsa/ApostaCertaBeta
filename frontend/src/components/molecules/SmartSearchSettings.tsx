/**
 * Painel de configurações para Busca Inteligente
 * Permite configurar thresholds e tipos de oportunidade
 */

import { useState } from 'react';
import { Icon } from '@/components/atoms';
import { useSmartSearchSettingsStore } from '@/stores';
import { STAT_LABELS } from '@/types/smartSearch';

interface SmartSearchSettingsProps {
  isOpen: boolean;
  onToggle: () => void;
}

/**
 * Input de slider com label e valor
 */
function SliderInput({
  label,
  value,
  onChange,
  min,
  max,
  step = 0.05,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <label className="text-sm text-gray-400 min-w-[100px]">{label}</label>
      <div className="flex items-center gap-2 flex-1">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="flex-1 h-2 bg-dark-quaternary rounded-lg appearance-none cursor-pointer accent-primary-500"
        />
        <span className="text-sm text-white font-medium w-12 text-right">
          {Math.round(value * 100)}%
        </span>
      </div>
    </div>
  );
}

/**
 * Toggle switch estilizado
 */
function ToggleSwitch({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className="flex items-center justify-between cursor-pointer">
      <span className="text-sm text-gray-400">{label}</span>
      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={`
          relative w-11 h-6 rounded-full transition-colors
          ${checked ? 'bg-primary-500' : 'bg-dark-quaternary'}
        `}
      >
        <span
          className={`
            absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform
            ${checked ? 'translate-x-5' : 'translate-x-0'}
          `}
        />
      </button>
    </label>
  );
}

export function SmartSearchSettings({ isOpen, onToggle }: SmartSearchSettingsProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const {
    showOver,
    showUnder,
    globalThresholds,
    statThresholds,
    setShowOver,
    setShowUnder,
    setGlobalThreshold,
    setStatThreshold,
    resetToDefaults,
  } = useSmartSearchSettingsStore();

  return (
    <div className="bg-dark-secondary rounded-xl border border-dark-tertiary">
      {/* Header - sempre visível */}
      <button
        type="button"
        onClick={onToggle}
        className="focus-ring w-full flex items-center justify-between p-4 hover:bg-dark-tertiary/50 transition-colors rounded-xl"
      >
        <div className="flex items-center gap-2">
          <Icon name="settings" size="sm" className="text-gray-400" />
          <span className="text-sm text-gray-400">Ajustar critérios</span>
        </div>
        <Icon
          name="chevron-right"
          size="sm"
          className={`text-gray-400 transform transition-transform ${isOpen ? 'rotate-90' : ''}`}
        />
      </button>

      {/* Conteúdo expansível */}
      {isOpen && (
        <div className="p-4 pt-0 space-y-6">
          {/* Seção: Tipos de Oportunidade */}
          <div className="space-y-3">
            <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wider">
              Tipos de mercado
            </h4>
            <ToggleSwitch
              label="Mostrar Over"
              checked={showOver}
              onChange={setShowOver}
            />
            <ToggleSwitch
              label="Mostrar Under"
              checked={showUnder}
              onChange={setShowUnder}
            />
          </div>

          <div className="h-px bg-dark-tertiary" />

          {/* Seção: Limiares Globais */}
          <div className="space-y-3">
            <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wider">
              Critérios gerais
            </h4>
            <SliderInput
              label="Corte de probabilidade"
              value={globalThresholds.probabilityCutoff}
              onChange={(v) => setGlobalThreshold('probabilityCutoff', v)}
              min={0.90}
              max={1.00}
              step={0.01}
            />
            <SliderInput
              label="Margem mínima"
              value={globalThresholds.minEdge}
              onChange={(v) => setGlobalThreshold('minEdge', v)}
              min={0.10}
              max={0.50}
              step={0.05}
            />
          </div>

          <div className="h-px bg-dark-tertiary" />

          {/* Seção: Configurações Avançadas */}
          <div>
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="focus-ring flex items-center gap-2 text-xs text-gray-400 hover:text-white transition-colors rounded-lg px-2 py-1 -mx-2"
            >
              <Icon
                name="chevron-right"
                size="sm"
                className={`transform transition-transform ${showAdvanced ? 'rotate-90' : ''}`}
              />
              <span>Configurar por estatística</span>
            </button>

            {showAdvanced && (
              <div className="mt-4 space-y-4">
                {Object.entries(statThresholds).map(([stat, thresholds]) => (
                  <div
                    key={stat}
                    className="p-3 bg-dark-tertiary/30 rounded-lg space-y-2"
                  >
                    <h5 className="text-sm font-medium text-white">
                      {STAT_LABELS[stat] || stat}
                    </h5>
                    <SliderInput
                      label="Over Mín."
                      value={thresholds.overMin}
                      onChange={(v) => setStatThreshold(stat, 'overMin', v)}
                      min={0.50}
                      max={0.90}
                    />
                    <SliderInput
                      label="Under Mín."
                      value={thresholds.underMin}
                      onChange={(v) => setStatThreshold(stat, 'underMin', v)}
                      min={0.50}
                      max={0.90}
                    />
                    <SliderInput
                      label="Confiança Mín."
                      value={thresholds.confiancaMin}
                      onChange={(v) => setStatThreshold(stat, 'confiancaMin', v)}
                      min={0.50}
                      max={0.90}
                    />
                    <div className="flex items-center justify-between gap-4">
                      <label className="text-sm text-gray-400 min-w-[100px]">Linha Mín.</label>
                      <div className="flex items-center gap-2 flex-1">
                        <input
                          type="number"
                          min={0}
                          max={50}
                          step={0.5}
                          value={thresholds.lineMin}
                          onChange={(e) => setStatThreshold(stat, 'lineMin', parseFloat(e.target.value) || 0)}
                          className="w-20 px-2 py-1 text-sm text-white bg-dark-quaternary border border-dark-tertiary rounded-lg text-right appearance-none"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="h-px bg-dark-tertiary" />

          {/* Botão Reset */}
          <button
            type="button"
            onClick={resetToDefaults}
            className="w-full py-2 text-sm text-gray-400 hover:text-white hover:bg-dark-tertiary rounded-lg transition-colors"
          >
            Restaurar padrão
          </button>
        </div>
      )}
    </div>
  );
}
