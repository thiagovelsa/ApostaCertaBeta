"""
Escudos Routes
==============

GET /api/time/{teamId}/escudo - Busca escudo de um time
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Path

from ...models import EscudoResponse
from ...services import EscudosService
from ...dependencies import get_escudos_service

router = APIRouter()


@router.get(
    "/time/{team_id}/escudo",
    response_model=EscudoResponse,
    summary="Busca escudo de um time",
    description="""
    Retorna a URL do escudo/logo de um time.
    Os escudos sao obtidos do TheSportsDB.
    """,
)
async def get_escudo(
    team_id: str = Path(
        ...,
        description="ID do time na VStats API",
        example="4dsgumo7d4zupm2ugsvm4zm4d",
    ),
    nome: Optional[str] = Query(
        None,
        description="Nome do time (ajuda na busca)",
        example="Arsenal",
    ),
    service: EscudosService = Depends(get_escudos_service),
) -> EscudoResponse:
    """
    Busca o escudo de um time.

    - **team_id**: ID do time (obrigatorio)
    - **nome**: Nome do time (opcional, melhora precisao da busca)

    Retorna URL do escudo ou null se nao encontrado.
    """
    return await service.get_escudo(team_id, nome)
