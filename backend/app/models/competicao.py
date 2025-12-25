"""
Modelos de Competicao
=====================

Schemas para competicoes suportadas.
"""

from typing import List

from pydantic import BaseModel, Field


class CompeticaoInfo(BaseModel):
    """Informacoes de uma competicao."""

    id: str = Field(..., description="ID unico da competicao na VStats API")
    nome: str = Field(..., max_length=100, description="Nome da competicao")
    pais: str = Field(..., max_length=50, description="Pais da competicao")
    tipo: str = Field(..., description="Tipo de competicao (Liga, Copa)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "51r6ph2woavlbbpk8f29nynf8",
                "nome": "Premier League 2025/26",
                "pais": "Inglaterra",
                "tipo": "Liga",
            }
        }
    }


class CompeticaoListResponse(BaseModel):
    """Response para GET /api/competicoes."""

    total: int = Field(..., ge=0, description="Total de competicoes")
    competicoes: List[CompeticaoInfo] = Field(..., description="Lista de competicoes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 6,
                "competicoes": [
                    {
                        "id": "51r6ph2woavlbbpk8f29nynf8",
                        "nome": "Premier League 2025/26",
                        "pais": "Inglaterra",
                        "tipo": "Liga",
                    }
                ],
            }
        }
    }
