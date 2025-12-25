"""
Modelos de Partida
==================

Schemas para representacao de partidas e times.
"""

from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, Field


class TimeInfo(BaseModel):
    """Informacoes basicas de um time (mandante/visitante)."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="ID unico do time na VStats API",
    )
    nome: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nome oficial do time",
    )
    codigo: str = Field(
        ...,
        min_length=2,
        max_length=5,
        description="Codigo do time (ex: ARS)",
    )
    escudo: Optional[str] = Field(
        None,
        description="URL do escudo/logo do time",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "4dsgumo7d4zupm2ugsvm4zm4d",
                "nome": "Arsenal",
                "codigo": "ARS",
                "escudo": "https://www.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png",
            }
        }
    }


class PartidaResumo(BaseModel):
    """Resumo de uma partida (usado em listas)."""

    id: str = Field(..., description="ID unico da partida")
    tournament_id: str = Field(..., description="ID da competicao (tournamentCalendarId)")
    data: date = Field(..., description="Data da partida")
    horario: time = Field(..., description="Horario da partida")
    competicao: str = Field(..., max_length=100, description="Nome da competicao")
    estadio: Optional[str] = Field(None, max_length=100, description="Nome do estadio")
    mandante: TimeInfo = Field(..., description="Time mandante")
    visitante: TimeInfo = Field(..., description="Time visitante")

    model_config = {
        "json_schema_extra": {
            "example": {
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
                    "escudo": None,
                },
                "visitante": {
                    "id": "1c8m2ko0wxq1asfkuykurdr0y",
                    "nome": "Crystal Palace",
                    "codigo": "CRY",
                    "escudo": None,
                },
            }
        }
    }


class PartidaListResponse(BaseModel):
    """Response para GET /api/partidas."""

    data: date = Field(..., description="Data das partidas")
    total_partidas: int = Field(..., ge=0, description="Total de partidas encontradas")
    partidas: List[PartidaResumo] = Field(..., description="Lista de partidas")

    model_config = {
        "json_schema_extra": {
            "example": {
                "data": "2025-12-27",
                "total_partidas": 5,
                "partidas": [],
            }
        }
    }
