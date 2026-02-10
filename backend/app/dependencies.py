"""
Dependency Injection
====================

Factory functions para injecao de dependencias no FastAPI.
"""

from functools import lru_cache

from .repositories import VStatsRepository, BadgeRepository
from .services import (
    PartidasService,
    StatsService,
    CompeticoesService,
    EscudosService,
    get_cache_service,
)


@lru_cache
def get_vstats_repository() -> VStatsRepository:
    """Retorna instancia do VStatsRepository."""
    return VStatsRepository()


@lru_cache
def get_badge_repository() -> BadgeRepository:
    """Retorna instancia do BadgeRepository."""
    return BadgeRepository()


def get_partidas_service() -> PartidasService:
    """Retorna instancia do PartidasService."""
    return PartidasService(
        vstats_repo=get_vstats_repository(),
        cache=get_cache_service(),
    )


def get_stats_service() -> StatsService:
    """Retorna instancia do StatsService."""
    return StatsService(
        vstats_repo=get_vstats_repository(),
        cache=get_cache_service(),
    )


def get_competicoes_service() -> CompeticoesService:
    """Retorna instancia do CompeticoesService."""
    return CompeticoesService(
        cache=get_cache_service(),
    )


def get_escudos_service() -> EscudosService:
    """Retorna instancia do EscudosService."""
    return EscudosService(
        badge_repo=get_badge_repository(),
        cache=get_cache_service(),
    )
