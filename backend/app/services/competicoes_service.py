"""
Competicoes Service
===================

Logica de negocio para listagem de competicoes.
"""

from ..models import CompeticaoInfo, CompeticaoListResponse
from ..utils.constants import ACTIVE_COMPETITIONS
from .cache_service import CacheService


class CompeticoesService:
    """Servico para operacoes com competicoes."""

    def __init__(self, cache: CacheService):
        self.cache = cache

    async def listar_competicoes(self) -> CompeticaoListResponse:
        """
        Lista todas as competicoes suportadas.

        Returns:
            CompeticaoListResponse com lista de competicoes
        """
        # Tenta cache
        cache_key = "competicoes:list"
        cached = await self.cache.get(cache_key)
        if cached:
            return CompeticaoListResponse(**cached)

        # Converte para modelos
        competicoes = [
            CompeticaoInfo(
                id=comp["id"],
                nome=comp["nome"],
                pais=comp["pais"],
                tipo=comp["tipo"],
            )
            for comp in ACTIVE_COMPETITIONS
        ]

        response = CompeticaoListResponse(
            total=len(competicoes),
            competicoes=competicoes,
        )

        # Cache por 12 horas (competicoes nao mudam frequentemente)
        await self.cache.set(cache_key, response.model_dump(mode="json"), 43200)

        return response

    async def get_competicao_por_id(self, comp_id: str) -> CompeticaoInfo | None:
        """
        Busca competicao por ID.

        Args:
            comp_id: ID da competicao

        Returns:
            CompeticaoInfo ou None se nao encontrada
        """
        for comp in ACTIVE_COMPETITIONS:
            if comp["id"] == comp_id:
                return CompeticaoInfo(
                    id=comp["id"],
                    nome=comp["nome"],
                    pais=comp["pais"],
                    tipo=comp["tipo"],
                )
        return None
