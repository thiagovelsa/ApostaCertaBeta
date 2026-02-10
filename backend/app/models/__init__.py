"""
Modelos Pydantic (Schemas/DTOs)
===============================

Modelos para validacao e serializacao de dados.
"""

from .partida import TimeInfo, PartidaResumo, PartidaListResponse
from .estatisticas import (
    EstatisticaMetrica,
    EstatisticaFeitos,
    EstatisticasTime,
    TimeComEstatisticas,
    ArbitroInfo,
    DebugAmostraTime,
    DebugAmostra,
    StatsResponse,
)
from .contexto import ClassificacaoTimeInfo, ContextoPartida, ContextoTime, H2HInfo
from .competicao import CompeticaoInfo, CompeticaoListResponse
from .escudo import EscudoResponse
from .analysis import (
    PrevisaoValor,
    PrevisaoEstatistica,
    PrevisaoPartida,
    OverUnderLine,
    OverUnderStat,
    OverUnderPartida,
    StatsAnalysisResponse,
)

__all__ = [
    # Partida
    "TimeInfo",
    "PartidaResumo",
    "PartidaListResponse",
    # Estatisticas
    "EstatisticaMetrica",
    "EstatisticaFeitos",
    "EstatisticasTime",
    "TimeComEstatisticas",
    "ArbitroInfo",
    "DebugAmostraTime",
    "DebugAmostra",
    "StatsResponse",
    # Contexto
    "ClassificacaoTimeInfo",
    "ContextoPartida",
    "ContextoTime",
    "H2HInfo",
    # Competicao
    "CompeticaoInfo",
    "CompeticaoListResponse",
    # Escudo
    "EscudoResponse",
    # Analysis
    "PrevisaoValor",
    "PrevisaoEstatistica",
    "PrevisaoPartida",
    "OverUnderLine",
    "OverUnderStat",
    "OverUnderPartida",
    "StatsAnalysisResponse",
]
