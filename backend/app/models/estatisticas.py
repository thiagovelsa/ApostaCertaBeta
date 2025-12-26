"""
Modelos de Estatisticas
=======================

Schemas para estatisticas de times e partidas.
"""

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from .partida import PartidaResumo


class EstatisticaMetrica(BaseModel):
    """Metrica de estatistica com media, CV e classificacao."""

    media: float = Field(..., ge=0, description="Valor medio")
    cv: float = Field(..., ge=0, description="Coeficiente de Variacao")
    classificacao: Literal[
        "Muito Estável",
        "Estável",
        "Moderado",
        "Instável",
        "Muito Instável",
    ] = Field(..., description="Classificacao baseada no CV")

    @field_validator("media", "cv")
    @classmethod
    def arredondar(cls, v: float) -> float:
        """Arredonda para 2 casas decimais."""
        return round(v, 2)

    model_config = {
        "json_schema_extra": {
            "example": {
                "media": 5.88,
                "cv": 0.32,
                "classificacao": "Moderado",
            }
        }
    }


class EstatisticaFeitos(BaseModel):
    """Estatisticas feitas vs sofridas."""

    feitos: EstatisticaMetrica = Field(..., description="Estatistica feita pelo time")
    sofridos: EstatisticaMetrica = Field(
        ..., description="Estatistica sofrida pelo time"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "feitos": {"media": 5.88, "cv": 0.32, "classificacao": "Moderado"},
                "sofridos": {"media": 3.50, "cv": 0.28, "classificacao": "Estável"},
            }
        }
    }


class EstatisticasTime(BaseModel):
    """Todas as estatisticas de um time."""

    escanteios: EstatisticaFeitos = Field(..., description="Escanteios")
    gols: EstatisticaFeitos = Field(..., description="Gols")
    finalizacoes: EstatisticaFeitos = Field(..., description="Finalizacoes totais")
    finalizacoes_gol: EstatisticaFeitos = Field(
        ..., description="Finalizacoes no gol"
    )
    cartoes_amarelos: EstatisticaMetrica = Field(..., description="Cartoes amarelos")
    cartoes_vermelhos: EstatisticaMetrica = Field(..., description="Cartoes vermelhos")
    faltas: EstatisticaMetrica = Field(..., description="Faltas cometidas")


class TimeComEstatisticas(BaseModel):
    """Time com suas estatisticas."""

    id: str = Field(..., description="ID do time")
    nome: str = Field(..., description="Nome do time")
    escudo: Optional[str] = Field(None, description="URL do escudo")
    estatisticas: EstatisticasTime = Field(..., description="Estatisticas do time")
    recent_form: List[Literal["W", "D", "L"]] = Field(
        default_factory=list,
        description="Sequencia de resultados recentes (W=win, D=draw, L=loss)",
    )


class ArbitroInfo(BaseModel):
    """Informacoes do arbitro da partida com estatisticas."""

    id: str = Field(..., description="ID do arbitro")
    nome: str = Field(..., description="Nome do arbitro")
    partidas: int = Field(..., ge=0, description="Partidas apitadas na competicao")
    media_cartoes_amarelos: float = Field(
        ..., ge=0, description="Media de cartoes amarelos por jogo"
    )
    media_faltas: Optional[float] = Field(
        None, ge=0, description="Media de faltas por jogo"
    )

    @field_validator("media_cartoes_amarelos", "media_faltas", mode="before")
    @classmethod
    def parse_float(cls, v):
        """Converte string para float se necessario."""
        if v is None:
            return None
        try:
            return round(float(v), 2)
        except (TypeError, ValueError):
            return 0.0


class StatsResponse(BaseModel):
    """Response para GET /api/partida/{matchId}/stats."""

    partida: PartidaResumo = Field(..., description="Informacoes da partida")
    filtro_aplicado: Literal["geral", "5", "10"] = Field(
        ..., description="Periodo analisado"
    )
    partidas_analisadas: int = Field(
        ..., ge=1, description="Numero de partidas usadas no calculo"
    )
    mandante: TimeComEstatisticas = Field(
        ..., description="Estatisticas do time mandante"
    )
    visitante: TimeComEstatisticas = Field(
        ..., description="Estatisticas do time visitante"
    )
    arbitro: Optional[ArbitroInfo] = Field(
        None, description="Informacoes do arbitro da partida"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "partida": {
                    "id": "f4vscquffy37afgv0arwcbztg",
                    "tournament_id": "51r6ph2woavlbbpk8f29nynf8",
                    "data": "2025-12-27",
                    "horario": "17:00:00",
                    "competicao": "Premier League",
                    "estadio": "Emirates Stadium",
                    "mandante": {
                        "id": "4dsgumo7d4zupm2ugsvm4zm4d",
                        "nome": "Arsenal",
                        "codigo": "ARS",
                    },
                    "visitante": {
                        "id": "1c8m2ko0wxq1asfkuykurdr0y",
                        "nome": "Crystal Palace",
                        "codigo": "CRY",
                    },
                },
                "filtro_aplicado": "5",
                "partidas_analisadas": 5,
            }
        }
    }
