"""Schemas Pydantic para análise consolidada (stats + previsões + over/under)."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .estatisticas import StatsResponse


ConfiancaLabel = Literal["Baixa", "Média", "Alta"]


class PrevisaoValor(BaseModel):
    valor: float
    confianca: float = Field(..., ge=0, le=1)
    confiancaLabel: ConfiancaLabel


class PrevisaoEstatistica(BaseModel):
    home: PrevisaoValor
    away: PrevisaoValor
    total: PrevisaoValor


class PrevisaoPartida(BaseModel):
    gols: PrevisaoEstatistica
    escanteios: PrevisaoEstatistica
    finalizacoes: PrevisaoEstatistica
    finalizacoes_gol: PrevisaoEstatistica
    cartoes_amarelos: PrevisaoEstatistica
    faltas: PrevisaoEstatistica


DistributionType = Literal["poisson", "normal", "negbin"]


class OverUnderLine(BaseModel):
    line: float
    over: float = Field(..., ge=0, le=1)
    under: float = Field(..., ge=0, le=1)
    ci_lower: Optional[float] = Field(default=None, ge=0, le=1)
    ci_upper: Optional[float] = Field(default=None, ge=0, le=1)
    uncertainty: Optional[float] = Field(default=None, ge=0, le=1)


class OverUnderStat(BaseModel):
    label: str
    icon: str
    lambda_: float = Field(..., alias="lambda")
    lambdaHome: float
    lambdaAway: float
    # Intervalo de previsao para contagem total (mu), usado para Min/Max na UI.
    # Mantemos em camelCase para alinhar com o frontend.
    predMin: float
    predMax: float
    intervalLevel: float = Field(default=0.9, ge=0, le=1)
    sigma: Optional[float] = None
    distribution: DistributionType
    lines: List[OverUnderLine]
    confidence: float = Field(..., ge=0, le=1)
    confidenceLabel: ConfiancaLabel

    model_config = {"populate_by_name": True, "serialize_by_alias": True}


class OverUnderPartida(BaseModel):
    gols: OverUnderStat
    escanteios: OverUnderStat
    finalizacoes: OverUnderStat
    finalizacoes_gol: OverUnderStat
    cartoes_amarelos: OverUnderStat
    faltas: OverUnderStat


class StatsAnalysisResponse(StatsResponse):
    previsoes: PrevisaoPartida
    over_under: OverUnderPartida
