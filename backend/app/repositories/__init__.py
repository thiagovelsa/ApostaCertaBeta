"""
Repositorios (Clientes API Externos)
====================================

Camada de acesso a dados externos (VStats API).
"""

from .vstats_repository import VStatsRepository

__all__ = [
    "VStatsRepository",
]
