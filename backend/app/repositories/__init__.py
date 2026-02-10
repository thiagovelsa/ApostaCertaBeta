"""
Repositorios (Clientes API Externos)
====================================

Camada de acesso a dados externos (VStats API).
"""

from .vstats_repository import VStatsRepository
from .badge_repository import BadgeRepository

__all__ = [
    "VStatsRepository",
    "BadgeRepository",
]

