"""
Partidas Routes
===============

GET /api/partidas - Lista partidas por data
"""

from datetime import date
import logging

from fastapi import APIRouter, Depends, Query, HTTPException

logger = logging.getLogger(__name__)

from ...models import PartidaListResponse
from ...services import PartidasService
from ...dependencies import get_partidas_service

router = APIRouter()


@router.get(
    "/partidas",
    response_model=PartidaListResponse,
    summary="Lista partidas por data",
    description="""
    Retorna todas as partidas agendadas para uma data especifica
    de todas as competicoes suportadas.
    """,
)
async def listar_partidas(
    data: date = Query(
        ...,
        description="Data no formato YYYY-MM-DD",
        examples=["2025-12-27"],
    ),
    service: PartidasService = Depends(get_partidas_service),
) -> PartidaListResponse:
    """
    Lista todas as partidas de uma data.

    - **data**: Data das partidas (obrigatorio, formato YYYY-MM-DD)

    Retorna lista de partidas com informacoes dos times,
    horarios e competicoes.
    """
    try:
        return await service.get_partidas_por_data(data)
    except Exception:
        logger.exception("❌ Erro inesperado ao buscar partidas")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao buscar partidas. Tente novamente mais tarde.",
        )
