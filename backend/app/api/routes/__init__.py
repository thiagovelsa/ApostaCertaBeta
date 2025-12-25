"""
API Routes
==========

Rotas organizadas por recurso.
"""

from fastapi import APIRouter

from .partidas import router as partidas_router
from .stats import router as stats_router
from .competicoes import router as competicoes_router

# Router principal que agrupa todas as rotas
api_router = APIRouter(prefix="/api")

api_router.include_router(partidas_router, tags=["Partidas"])
api_router.include_router(stats_router, tags=["Estatísticas"])
api_router.include_router(competicoes_router, tags=["Competições"])
