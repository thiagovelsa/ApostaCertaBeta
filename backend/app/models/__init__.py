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
    StatsResponse,
)
from .competicao import CompeticaoInfo, CompeticaoListResponse
from .escudo import EscudoResponse

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
    "StatsResponse",
    # Competicao
    "CompeticaoInfo",
    "CompeticaoListResponse",
    # Escudo
    "EscudoResponse",
]
