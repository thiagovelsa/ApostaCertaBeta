"""
Camada de Servicos (Business Logic)
====================================

Servicos que implementam a logica de negocio da aplicacao.
"""

from .cache_service import CacheService, get_cache_service
from .partidas_service import PartidasService
from .stats_service import StatsService
from .competicoes_service import CompeticoesService
from .analysis_service import AnalysisService
from .escudos_service import EscudosService

__all__ = [
    "CacheService",
    "get_cache_service",
    "PartidasService",
    "StatsService",
    "CompeticoesService",
    "AnalysisService",
    "EscudosService",
]
