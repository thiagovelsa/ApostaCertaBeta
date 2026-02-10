"""
Competicoes Routes
==================

GET /api/competicoes - Lista competicoes suportadas
"""

from fastapi import APIRouter, Depends

from ...models import CompeticaoListResponse
from ...services import CompeticoesService
from ...dependencies import get_competicoes_service

router = APIRouter()


@router.get(
    "/competicoes",
    response_model=CompeticaoListResponse,
    summary="Lista competicoes suportadas",
    description="""
    Retorna todas as competicoes disponiveis no sistema.
    """,
)
async def listar_competicoes(
    service: CompeticoesService = Depends(get_competicoes_service),
) -> CompeticaoListResponse:
    """
    Lista todas as competicoes suportadas.

    Retorna informacoes como nome, pais e tipo (liga, copa).
    """
    return await service.listar_competicoes()
