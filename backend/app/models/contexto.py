"""Modelos Pydantic para contexto pre-jogo (features explicaveis).

Mantido separado para evitar inflar estatisticas.py e para facilitar reutilizacao.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ClassificacaoTimeInfo(BaseModel):
    posicao: int = Field(..., ge=1)
    pontos: int = Field(default=0, ge=0)
    jogos: int = Field(default=0, ge=0)
    saldo_gols: Optional[int] = None


class H2HInfo(BaseModel):
    total_matches: int = Field(..., ge=0)
    avg_goals_per_match: float = Field(..., ge=0)
    home_wins: int = Field(default=0, ge=0)
    away_wins: int = Field(default=0, ge=0)
    draws: int = Field(default=0, ge=0)


class ContextoTime(BaseModel):
    dias_descanso: Optional[int] = Field(default=None, ge=0)
    jogos_7d: Optional[int] = Field(default=None, ge=0)
    jogos_14d: Optional[int] = Field(default=None, ge=0)
    posicao: Optional[int] = Field(default=None, ge=1)


class ContextoPartida(BaseModel):
    mandante: ContextoTime
    visitante: ContextoTime
    classificacao_mandante: Optional[ClassificacaoTimeInfo] = None
    classificacao_visitante: Optional[ClassificacaoTimeInfo] = None
    h2h_all_comps: Optional[H2HInfo] = None
    fase: Optional[str] = None
    ajustes_aplicados: List[str] = Field(default_factory=list)

