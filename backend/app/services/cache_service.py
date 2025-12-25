"""
Cache Service
=============

Servico de cache com suporte a Redis ou fallback in-memory.
"""

import json
from typing import Any, Optional
from functools import lru_cache

from ..config import settings


class CacheService:
    """
    Servico de cache abstrato.

    Se CACHE_ENABLED=true e Redis disponivel, usa Redis.
    Caso contrario, usa cache in-memory simples.
    """

    def __init__(self):
        self.enabled = settings.cache_enabled
        self._memory_cache: dict = {}
        self._redis_client = None

        if self.enabled:
            self._init_redis()

    def _init_redis(self):
        """Inicializa conexao Redis se disponivel."""
        try:
            import redis

            self._redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
            # Testa conexao
            self._redis_client.ping()
        except Exception:
            # Se falhar, usa cache in-memory
            self._redis_client = None

    async def get(self, key: str) -> Optional[Any]:
        """
        Busca valor do cache.

        Args:
            key: Chave do cache

        Returns:
            Valor armazenado ou None
        """
        if not self.enabled:
            return None

        if self._redis_client:
            try:
                value = self._redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception:
                pass

        # Fallback para memoria
        return self._memory_cache.get(key)

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Armazena valor no cache.

        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: Tempo de vida em segundos

        Returns:
            True se sucesso
        """
        if not self.enabled:
            return False

        if self._redis_client:
            try:
                self._redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str),
                )
                return True
            except Exception:
                pass

        # Fallback para memoria (sem TTL)
        self._memory_cache[key] = value
        return True

    async def delete(self, key: str) -> bool:
        """
        Remove valor do cache.

        Args:
            key: Chave do cache

        Returns:
            True se sucesso
        """
        if self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception:
                pass

        if key in self._memory_cache:
            del self._memory_cache[key]

        return True

    async def clear(self) -> bool:
        """Limpa todo o cache."""
        if self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception:
                pass

        self._memory_cache.clear()
        return True

    def build_key(self, prefix: str, *args) -> str:
        """
        Constroi chave de cache padronizada.

        Args:
            prefix: Prefixo da chave (ex: 'partidas', 'stats')
            *args: Partes da chave

        Returns:
            Chave formatada (ex: 'partidas:2025-12-27')
        """
        parts = [f"v{settings.cache_version}", prefix] + [str(arg) for arg in args]
        return ":".join(parts)


@lru_cache
def get_cache_service() -> CacheService:
    """Retorna instancia singleton do CacheService."""
    return CacheService()
