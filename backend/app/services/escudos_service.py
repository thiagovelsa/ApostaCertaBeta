"""
Escudos Service
===============

Logica de negocio para busca de escudos de times.
"""

from typing import Optional

from ..config import settings
from ..models import EscudoResponse
from ..repositories import BadgeRepository
from .cache_service import CacheService


class EscudosService:
    """Servico para operacoes com escudos."""

    def __init__(
        self,
        badge_repo: BadgeRepository,
        cache: CacheService,
    ):
        self.badges = badge_repo
        self.cache = cache

    async def get_escudo(
        self,
        team_id: str,
        team_name: Optional[str] = None,
    ) -> EscudoResponse:
        """
        Busca escudo de um time.

        Args:
            team_id: ID do time na VStats
            team_name: Nome do time (opcional, usado para busca)

        Returns:
            EscudoResponse com URL do escudo
        """
        # Tenta cache
        cache_key = self.cache.build_key("escudo", team_id)
        cached = await self.cache.get(cache_key)
        if cached:
            return EscudoResponse(**cached)

        escudo_url = None
        final_name = team_name or team_id

        if team_name:
            try:
                # Normaliza nome e busca
                normalized = self.badges.normalize_team_name(team_name)
                escudo_url = await self.badges.get_badge_url(normalized)
            except Exception:
                pass

        response = EscudoResponse(
            team_id=team_id,
            team_name=final_name,
            escudo_url=escudo_url,
            fonte="TheSportsDB" if escudo_url else "Não encontrado",
        )

        # Cache por 7 dias
        await self.cache.set(
            cache_key,
            response.model_dump(mode="json"),
            settings.cache_ttl_badges,
        )

        return response

    async def get_escudo_por_nome(self, team_name: str) -> EscudoResponse:
        """
        Busca escudo pelo nome do time.

        Args:
            team_name: Nome do time

        Returns:
            EscudoResponse com URL do escudo
        """
        # Normaliza nome
        normalized = self.badges.normalize_team_name(team_name)

        # Busca info completa do time
        team_info = await self.badges.get_team_info(normalized)

        if team_info:
            return EscudoResponse(
                team_id=team_info.get("id", ""),
                team_name=team_info.get("name", team_name),
                escudo_url=team_info.get("badge_url"),
                fonte="TheSportsDB",
            )

        return EscudoResponse(
            team_id="",
            team_name=team_name,
            escudo_url=None,
            fonte="Não encontrado",
        )
