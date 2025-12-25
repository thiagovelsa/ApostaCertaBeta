"""
Modelos de Escudo
=================

Schemas para escudos/logos de times.
"""

from typing import Optional

from pydantic import BaseModel, Field


class EscudoResponse(BaseModel):
    """Response para GET /api/time/{teamId}/escudo."""

    team_id: str = Field(..., description="ID do time")
    team_name: str = Field(..., description="Nome do time")
    escudo_url: Optional[str] = Field(None, description="URL do escudo")
    fonte: str = Field(
        default="TheSportsDB",
        description="Fonte do escudo",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "team_id": "4dsgumo7d4zupm2ugsvm4zm4d",
                "team_name": "Arsenal",
                "escudo_url": "https://www.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png",
                "fonte": "TheSportsDB",
            }
        }
    }
