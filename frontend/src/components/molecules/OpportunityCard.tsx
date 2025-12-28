import { useNavigate } from 'react-router-dom';
import { Icon, TeamBadge, type IconName } from '@/components/atoms';
import type { Oportunidade } from '@/types';
import { formatarProbabilidade, getScoreColor, getTipoBgColor } from '@/utils/smartSearch';

interface OpportunityCardProps {
  oportunidade: Oportunidade;
  rank?: number;
}

/**
 * Ícones por estatística
 */
const STAT_ICONS: Record<string, IconName> = {
  gols: 'goal',
  escanteios: 'corner',
  finalizacoes: 'shot',
  finalizacoes_gol: 'target',
  cartoes_amarelos: 'card',
  faltas: 'foul',
};

/**
 * Card individual de oportunidade de aposta
 * Exibe times, estatística, linha e probabilidade
 */
export function OpportunityCard({ oportunidade, rank }: OpportunityCardProps) {
  const navigate = useNavigate();
  const {
    matchId,
    mandante,
    visitante,
    competicao,
    horario,
    estatistica,
    estatisticaLabel,
    tipo,
    linha,
    probabilidade,
    confiancaLabel,
    score,
  } = oportunidade;

  const icon = STAT_ICONS[estatistica] || 'stats';
  const scoreColor = getScoreColor(score);
  const tipoBg = getTipoBgColor(tipo);

  const handleClick = () => {
    navigate(`/estatisticas/${matchId}`);
  };

  return (
    <div
      onClick={handleClick}
      className="bg-dark-secondary rounded-xl p-4 border border-dark-tertiary hover:border-primary-500/50 transition-all cursor-pointer">
      {/* Header: Times + Horário */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          {/* Rank badge */}
          {rank !== undefined && (
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-500/20 text-primary-400 text-xs font-bold flex items-center justify-center">
              {rank}
            </div>
          )}

          {/* Times */}
          <div className="flex items-center gap-1.5 min-w-0">
            <TeamBadge
              src={mandante.escudo || undefined}
              alt={mandante.nome}
              size="sm"
            />
            <span className="text-xs text-gray-400 truncate max-w-[80px]" title={mandante.nome}>
              {mandante.nome}
            </span>
            <span className="text-gray-600 text-xs">vs</span>
            <span className="text-xs text-gray-400 truncate max-w-[80px]" title={visitante.nome}>
              {visitante.nome}
            </span>
            <TeamBadge
              src={visitante.escudo || undefined}
              alt={visitante.nome}
              size="sm"
            />
          </div>
        </div>

        {/* Horário */}
        <div className="text-xs text-gray-500 flex-shrink-0">
          {horario}
        </div>
      </div>

      {/* Competição */}
      <div className="text-xs text-gray-500 mb-3 truncate" title={competicao}>
        {competicao}
      </div>

      {/* Divisor */}
      <div className="h-px bg-dark-tertiary mb-3" />

      {/* Oportunidade: Estatística + Tipo + Linha */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon name={icon} size="sm" className="text-primary-400" />
          <span className="text-sm font-medium text-white">
            {estatisticaLabel}
          </span>
          <span className={`px-2 py-0.5 rounded text-xs font-medium uppercase ${tipoBg}`}>
            {tipo} {linha}
          </span>
        </div>

        {/* Probabilidade + Confiança */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-lg font-bold text-white">
              {formatarProbabilidade(probabilidade)}
            </div>
            <div className="text-xs text-gray-500">
              Prob.
            </div>
          </div>

          <div className="w-px h-8 bg-dark-tertiary" />

          <div className="text-right">
            <div className={`text-sm font-medium ${confiancaLabel === 'Alta' ? 'text-success' : confiancaLabel === 'Média' ? 'text-warning' : 'text-danger'}`}>
              {confiancaLabel}
            </div>
            <div className="text-xs text-gray-500">
              Conf.
            </div>
          </div>
        </div>
      </div>

      {/* Score bar */}
      <div className="mt-3">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-gray-500">Score</span>
          <span className={`font-medium ${scoreColor}`}>
            {Math.round(score * 100)}
          </span>
        </div>
        <div className="h-1 bg-dark-quaternary rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary-500 to-success transition-all duration-500"
            style={{ width: `${score * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
