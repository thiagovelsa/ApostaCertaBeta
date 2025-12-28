import { Icon } from '@/components/atoms';
import { OpportunityCard } from '@/components/molecules';
import type { SmartSearchResult, SmartSearchProgress } from '@/types';

interface SmartSearchResultsProps {
  result: SmartSearchResult | null;
  progress: SmartSearchProgress | null;
  isAnalyzing: boolean;
  onClose?: () => void;
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
function EmptyState() {
  return (
    <div className="bg-dark-secondary rounded-xl p-8 border border-dark-tertiary text-center">
      <Icon name="search" size="lg" className="text-gray-600 mx-auto mb-4" />
      <h3 className="text-white font-medium mb-2">
        Nenhuma oportunidade encontrada
      </h3>
      <p className="text-sm text-gray-400 max-w-md mx-auto">
        Não foram encontradas oportunidades que atendam aos critérios de
        confiança alta e probabilidade favorável para as partidas do dia.
      </p>
    </div>
  );
}

/**
 * Header com estatísticas do resultado
 */
function ResultHeader({
  result,
  onClose,
}: {
  result: SmartSearchResult;
  onClose?: () => void;
}) {
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
              {result.total_oportunidades} oportunidades em {result.partidas_com_oportunidades} partidas
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
                {result.total_oportunidades}
              </div>
              <div className="text-xs text-gray-500">Encontradas</div>
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
  // Mostra barra de progresso durante análise
  if (isAnalyzing && progress) {
    return <ProgressBar progress={progress} />;
  }

  // Sem resultado ainda
  if (!result) {
    return null;
  }

  // Sem oportunidades
  if (result.oportunidades.length === 0) {
    return (
      <>
        <ResultHeader result={result} onClose={onClose} />
        <EmptyState />
      </>
    );
  }

  // Com oportunidades
  return (
    <div className="space-y-4">
      <ResultHeader result={result} onClose={onClose} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {result.oportunidades.map((op, index) => (
          <OpportunityCard
            key={`${op.matchId}-${op.estatistica}-${op.tipo}-${op.linha}`}
            oportunidade={op}
            rank={index + 1}
          />
        ))}
      </div>

      {/* Nota sobre critérios */}
      <div className="text-xs text-gray-500 text-center mt-4">
        Exibindo top {result.oportunidades.length} de {result.total_oportunidades} oportunidades.
        Critérios: Confiança Alta + Prob. Over {'\u2265'}60% ou Under {'\u2265'}70%
      </div>
    </div>
  );
}
