import { useState, useMemo } from 'react';
import { Icon, type IconName } from '@/components/atoms';
import { OpportunityCard, SmartSearchSettings } from '@/components/molecules';
import { useSmartSearchSettingsStore } from '@/stores';
import type { SmartSearchResult, SmartSearchProgress } from '@/types';

interface SmartSearchResultsProps {
  result: SmartSearchResult | null;
  progress: SmartSearchProgress | null;
  isAnalyzing: boolean;
  onClose?: () => void;
}

/**
 * Opções de estatísticas para o filtro
 */
const STAT_OPTIONS: { key: string; label: string; icon: IconName }[] = [
  { key: 'gols', label: 'Gols', icon: 'goal' },
  { key: 'escanteios', label: 'Escanteios', icon: 'corner' },
  { key: 'finalizacoes', label: 'Chutes', icon: 'shot' },
  { key: 'finalizacoes_gol', label: 'Chutes ao Gol', icon: 'target' },
  { key: 'cartoes_amarelos', label: 'Cartões', icon: 'card' },
  { key: 'faltas', label: 'Faltas', icon: 'foul' },
];

/**
 * Todas as estatísticas ativas por padrão
 */
const ALL_STATS = new Set(STAT_OPTIONS.map(s => s.key));

/**
 * Componente de filtro de estatísticas
 */
function StatFilter({
  ativos,
  onToggle,
}: {
  ativos: Set<string>;
  onToggle: (key: string) => void;
}) {
  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary mb-4">
      <div className="flex items-center gap-2 mb-3">
        <Icon name="filter" size="sm" className="text-gray-400" />
        <span className="text-sm text-gray-400">Filtrar por estatística:</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {STAT_OPTIONS.map(({ key, label, icon }) => {
          const isActive = ativos.has(key);
          return (
            <button
              key={key}
              onClick={() => onToggle(key)}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
                border transition-all duration-200
                ${isActive
                  ? 'bg-primary-500/20 text-primary-400 border-primary-500/50'
                  : 'bg-dark-tertiary text-gray-500 border-dark-quaternary hover:border-gray-600'
                }
              `}
            >
              <Icon name={icon} size="sm" />
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/**
 * Barra de progresso durante análise
 */
function ProgressBar({ progress }: { progress: SmartSearchProgress }) {
  return (
    <div className="bg-dark-secondary rounded-xl p-6 border border-dark-tertiary">
      <div className="flex items-center gap-3 mb-4">
        <div className="animate-spin">
          <Icon name="refresh" size="md" className="text-primary-400" />
        </div>
        <div>
          <h3 className="text-white font-medium">Analisando partidas...</h3>
          <p className="text-sm text-gray-400">
            {progress.analisadas} de {progress.total} partidas
          </p>
        </div>
      </div>

      <div className="h-2 bg-dark-quaternary rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-primary-500 to-success transition-all duration-300"
          style={{ width: `${progress.porcentagem}%` }}
        />
      </div>

      <div className="text-center text-sm text-gray-500 mt-2">
        {progress.porcentagem}%
      </div>
    </div>
  );
}

/**
 * Estado vazio quando não há oportunidades
 */
function EmptyState({ isFiltered }: { isFiltered?: boolean }) {
  return (
    <div className="bg-dark-secondary rounded-xl p-8 border border-dark-tertiary text-center">
      <Icon name="search" size="lg" className="text-gray-600 mx-auto mb-4" />
      <h3 className="text-white font-medium mb-2">
        {isFiltered ? 'Nenhuma oportunidade com os filtros selecionados' : 'Nenhuma oportunidade encontrada'}
      </h3>
      <p className="text-sm text-gray-400 max-w-md mx-auto">
        {isFiltered
          ? 'Tente selecionar outras estatísticas no filtro acima.'
          : 'Não foram encontradas oportunidades que atendam aos critérios de confiança alta e probabilidade favorável para as partidas do dia.'
        }
      </p>
    </div>
  );
}

/**
 * Header com estatísticas do resultado
 */
function ResultHeader({
  result,
  filteredCount,
  onClose,
}: {
  result: SmartSearchResult;
  filteredCount: number;
  onClose?: () => void;
}) {
  const isFiltered = filteredCount !== result.total_oportunidades;

  return (
    <div className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary mb-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-2 rounded-lg bg-primary-500/20">
            <Icon name="target" size="md" className="text-primary-400" />
          </div>
          <div>
            <h3 className="text-white font-semibold">
              Busca Inteligente
            </h3>
            <p className="text-sm text-gray-400">
              {isFiltered ? (
                <>{filteredCount} de {result.total_oportunidades} oportunidades</>
              ) : (
                <>{result.total_oportunidades} oportunidades em {result.partidas_com_oportunidades} partidas</>
              )}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Estatísticas */}
          <div className="flex items-center gap-6 text-center">
            <div>
              <div className="text-xl font-bold text-white">
                {result.partidas_analisadas}
              </div>
              <div className="text-xs text-gray-500">Analisadas</div>
            </div>
            <div>
              <div className="text-xl font-bold text-success">
                {isFiltered ? filteredCount : result.total_oportunidades}
              </div>
              <div className="text-xs text-gray-500">
                {isFiltered ? 'Filtradas' : 'Encontradas'}
              </div>
            </div>
          </div>

          {/* Botão fechar */}
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-dark-tertiary transition-colors text-gray-400 hover:text-white"
            >
              <Icon name="close" size="sm" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Container de resultados da Busca Inteligente
 */
export function SmartSearchResults({
  result,
  progress,
  isAnalyzing,
  onClose,
}: SmartSearchResultsProps) {
  // Estado dos filtros (todas as estatísticas ativas por padrão)
  const [filtrosAtivos, setFiltrosAtivos] = useState<Set<string>>(ALL_STATS);
  const [showSettings, setShowSettings] = useState(false);

  // Configurações do store
  const { showOver, showUnder, statThresholds } = useSmartSearchSettingsStore();

  // Filtra oportunidades baseado nos filtros ativos + showOver/showUnder + lineMin
  const oportunidadesFiltradas = useMemo(() => {
    if (!result) return [];
    return result.oportunidades.filter(op => {
      // Filtra por tipo (Over/Under)
      if (op.tipo === 'over' && !showOver) return false;
      if (op.tipo === 'under' && !showUnder) return false;
      // Filtra por estatística
      if (!filtrosAtivos.has(op.estatistica)) return false;
      // Filtra por linha mínima (reativo às configurações)
      const threshold = statThresholds[op.estatistica];
      if (threshold && op.linha < threshold.lineMin) return false;
      return true;
    });
  }, [result, filtrosAtivos, showOver, showUnder, statThresholds]);

  // Handler para toggle de filtro
  const handleToggle = (key: string) => {
    setFiltrosAtivos(prev => {
      const next = new Set(prev);

      // Impede desativar o último (pelo menos 1 ativo)
      if (next.has(key) && next.size === 1) {
        return prev;
      }

      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }

      return next;
    });
  };

  // Mostra barra de progresso durante análise
  if (isAnalyzing && progress) {
    return <ProgressBar progress={progress} />;
  }

  // Sem resultado ainda
  if (!result) {
    return null;
  }

  // Sem oportunidades originais
  if (result.oportunidades.length === 0) {
    return (
      <>
        <ResultHeader result={result} filteredCount={0} onClose={onClose} />
        <EmptyState />
      </>
    );
  }

  const isFiltered = filtrosAtivos.size !== ALL_STATS.size;

  // Com oportunidades
  return (
    <div className="space-y-4">
      <ResultHeader
        result={result}
        filteredCount={oportunidadesFiltradas.length}
        onClose={onClose}
      />

      {/* Painel de configurações */}
      <SmartSearchSettings
        isOpen={showSettings}
        onToggle={() => setShowSettings(!showSettings)}
      />

      {/* Filtro de estatísticas */}
      <StatFilter ativos={filtrosAtivos} onToggle={handleToggle} />

      {/* Grid de oportunidades ou estado vazio se filtrado */}
      {oportunidadesFiltradas.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {oportunidadesFiltradas.map((op, index) => (
            <OpportunityCard
              key={`${op.matchId}-${op.estatistica}-${op.tipo}-${op.linha}`}
              oportunidade={op}
              rank={index + 1}
            />
          ))}
        </div>
      ) : (
        <EmptyState isFiltered />
      )}

      {/* Nota sobre critérios */}
      <div className="text-xs text-gray-500 text-center mt-4">
        {isFiltered || !showOver || !showUnder ? (
          <>Exibindo {oportunidadesFiltradas.length} de {result.total_oportunidades} oportunidades (filtrado).</>
        ) : (
          <>Exibindo top {result.oportunidades.length} de {result.total_oportunidades} oportunidades.</>
        )}
        {' '}Critérios: Confiança {'\u2265'}{Math.round(statThresholds.gols.confiancaMin * 100)}%
        {showOver && <> + Prob. Over {'\u2265'}{Math.round(statThresholds.gols.overMin * 100)}%</>}
        {showOver && showUnder && ' ou'}
        {showUnder && <> Under {'\u2265'}{Math.round(statThresholds.gols.underMin * 100)}%</>}
      </div>
    </div>
  );
}
