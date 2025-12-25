"""
Badge Repository
================

Cliente para buscar escudos de times via TheSportsDB.
"""

import asyncio
import logging
from typing import Dict, Optional

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


class BadgeAPIError(Exception):
    """Erro ao buscar escudo."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class BadgeRepository:
    """Cliente HTTP para TheSportsDB API."""

    # Cache de escudos em memoria (persiste entre requests)
    _badge_cache: Dict[str, Optional[str]] = {}

    # Semaforo para rate limiting (max 2 requests por segundo)
    _semaphore: Optional[asyncio.Semaphore] = None

    # Flag de rate limiting (para permanentemente nesta sessao)
    _rate_limited: bool = False

    def __init__(self):
        self.api_key = settings.thesportsdb_api_key
        self.base_url = settings.thesportsdb_api_url
        self.timeout = settings.thesportsdb_api_timeout

    @classmethod
    def _get_semaphore(cls) -> asyncio.Semaphore:
        """Retorna semaforo para rate limiting."""
        if cls._semaphore is None:
            cls._semaphore = asyncio.Semaphore(2)
        return cls._semaphore

    @classmethod
    def is_rate_limited(cls) -> bool:
        """Verifica se estamos em rate limit."""
        return cls._rate_limited

    @classmethod
    def _set_rate_limited(cls):
        """Marca como rate limited (permanente nesta sessao)."""
        if not cls._rate_limited:
            cls._rate_limited = True
            logger.warning("🚫 TheSportsDB rate limit - escudos desativados")

    async def search_team(self, team_name: str) -> Optional[dict]:
        """
        Busca um time pelo nome.

        Args:
            team_name: Nome do time (ex: "Arsenal")

        Returns:
            Dados do time ou None se nao encontrado
        """
        url = f"{self.base_url}/{self.api_key}/searchteams.php"
        params = {"t": team_name}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                teams = data.get("teams")
                if teams and len(teams) > 0:
                    return teams[0]
                return None

            except httpx.TimeoutException:
                raise BadgeAPIError("Timeout ao buscar escudo")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise BadgeAPIError("Rate limit excedido - TheSportsDB")
                raise BadgeAPIError(f"Erro HTTP: {e.response.status_code}")
            except httpx.RequestError as e:
                raise BadgeAPIError(f"Erro de conexao: {str(e)}")

    async def get_badge_url(self, team_name: str) -> Optional[str]:
        """
        Busca a URL do escudo de um time (com cache).

        Args:
            team_name: Nome do time

        Returns:
            URL do escudo ou None
        """
        # Verifica cache primeiro
        cache_key = team_name.lower().strip()
        if cache_key in self._badge_cache:
            return self._badge_cache[cache_key]

        # Rate limiting: aguarda slot disponivel
        semaphore = self._get_semaphore()
        async with semaphore:
            # Verifica cache novamente (pode ter sido preenchido enquanto esperava)
            if cache_key in self._badge_cache:
                return self._badge_cache[cache_key]

            try:
                # Delay para evitar rate limiting (500ms entre requests)
                await asyncio.sleep(0.5)

                team = await self.search_team(team_name)

                if team:
                    badge_url = team.get("strTeamBadge")
                    self._badge_cache[cache_key] = badge_url
                    return badge_url

                self._badge_cache[cache_key] = None
                return None

            except BadgeAPIError as e:
                logger.warning(f"Erro ao buscar escudo de {team_name}: {e.message}")
                # Se for rate limit, ativa flag global
                if "Rate limit" in e.message or "429" in e.message:
                    self._set_rate_limited()
                # Nao cacheia erros para tentar novamente depois
                return None

    async def get_team_info(self, team_name: str) -> Optional[dict]:
        """
        Busca informacoes completas de um time.

        Args:
            team_name: Nome do time

        Returns:
            Dicionario com informacoes do time
        """
        team = await self.search_team(team_name)

        if team:
            return {
                "id": team.get("idTeam"),
                "name": team.get("strTeam"),
                "short_name": team.get("strTeamShort"),
                "badge_url": team.get("strTeamBadge"),
                "jersey_url": team.get("strTeamJersey"),
                "stadium": team.get("strStadium"),
                "country": team.get("strCountry"),
                "league": team.get("strLeague"),
            }

        return None

    # Mapeamento de nomes VStats -> TheSportsDB (quando diferentes)
    TEAM_NAME_MAPPING = {
        "Man City": "Manchester City",
        "Man Utd": "Manchester United",
        "Man United": "Manchester United",
        "Spurs": "Tottenham",
        "Wolves": "Wolverhampton Wanderers",
        "Brighton": "Brighton and Hove Albion",
        "West Ham": "West Ham United",
        "Newcastle": "Newcastle United",
        "Nottm Forest": "Nottingham Forest",
        "Nott'm Forest": "Nottingham Forest",
        "Sheffield Utd": "Sheffield United",
        "Luton": "Luton Town",
    }

    def normalize_team_name(self, vstats_name: str) -> str:
        """
        Normaliza nome do time para busca no TheSportsDB.

        Args:
            vstats_name: Nome do time como vem da VStats

        Returns:
            Nome normalizado para busca
        """
        return self.TEAM_NAME_MAPPING.get(vstats_name, vstats_name)
