"""
Cache Service
=============

Servico de cache com suporte a Redis ou fallback in-memory.
"""

import asyncio
import inspect
import json
import logging
import time
from typing import Any, Optional
from functools import lru_cache

from ..config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    Servico de cache abstrato.

    Se CACHE_ENABLED=true e Redis disponivel, usa Redis.
    Caso contrario, usa cache in-memory simples.
    """

    def __init__(self):
        self.enabled = settings.cache_enabled
        # In-memory cache supports TTL so dev/prod behavior is closer to Redis.
        # Value format: key -> (payload, expires_at_monotonic).
        # Backward compatible: if older entries exist as raw payloads, we still return them.
        self._memory_cache: dict = {}
        self._redis_client = None
        # Evita "loop" de tentativas de conexao quando Redis nao esta disponivel.
        # Importante: em dev, isso pode serializar chamadas async (parece que a API esta "em loop").
        self._redis_init_lock = asyncio.Lock()
        self._redis_disabled_until = 0.0

    async def _init_redis(self):
        """Inicializa conexao Redis assincrona se disponivel."""
        try:
            import redis.asyncio as aioredis

            # Nota: alguns ambientes nao tem Redis local. Nesses casos, a conexao pode ser lenta.
            # Usamos timeouts curtos e backoff para evitar travar o event loop.
            client = aioredis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
            )
            if inspect.isawaitable(client):
                client = await client
            self._redis_client = client
            await self._redis_client.ping()

            # Redis OK: libera backoff.
            self._redis_disabled_until = 0.0
            logger.info("[CACHE] Redis conectado (cache remoto habilitado).")
        except Exception as e:
            # Se falhar, usa cache in-memory e aplica backoff para nao tentar a cada get/set.
            self._redis_client = None
            self._redis_disabled_until = time.monotonic() + 60.0
            logger.info(
                "[CACHE] Redis indisponivel; usando cache in-memory (nova tentativa em ~60s)."
            )
            logger.debug("[CACHE] Detalhes falha Redis: %r", e)

    async def _ensure_redis(self):
        """Garante que o Redis foi inicializado (lazy init)."""
        if not self.enabled:
            return

        if not getattr(settings, "redis_url", None):
            return

        if self._redis_client is not None:
            return

        # Backoff apos falha para nao gerar "loop" de tentativas.
        if time.monotonic() < self._redis_disabled_until:
            return

        # Se outra task ja esta inicializando, nao aguarde: use fallback in-memory.
        if self._redis_init_lock.locked():
            return

        async with self._redis_init_lock:
            # Revalida dentro do lock.
            if self._redis_client is not None:
                return
            if time.monotonic() < self._redis_disabled_until:
                return
            await self._init_redis()

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

        await self._ensure_redis()

        if self._redis_client:
            try:
                value = await self._redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception:
                pass

        # Fallback para memoria
        entry = self._memory_cache.get(key)
        if entry is None:
            return None

        # Backward compatible with older in-memory values (stored without TTL).
        if not (isinstance(entry, tuple) and len(entry) == 2):
            return entry

        value, expires_at = entry
        try:
            expires_at_f = float(expires_at)
        except (TypeError, ValueError):
            return value

        if expires_at_f and time.monotonic() > expires_at_f:
            # Expired: evict.
            try:
                del self._memory_cache[key]
            except KeyError:
                pass
            return None

        return value

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

        await self._ensure_redis()

        if self._redis_client:
            try:
                await self._redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str),
                )
                return True
            except Exception:
                pass

        # Fallback para memoria (com TTL)
        expires_at = time.monotonic() + max(0, int(ttl or 0))
        self._memory_cache[key] = (value, expires_at)
        return True

    async def delete(self, key: str) -> bool:
        """
        Remove valor do cache.

        Args:
            key: Chave do cache

        Returns:
            True se sucesso
        """
        await self._ensure_redis()

        if self._redis_client:
            try:
                await self._redis_client.delete(key)
            except Exception:
                pass

        if key in self._memory_cache:
            del self._memory_cache[key]

        return True

    async def clear(self) -> bool:
        """Limpa todo o cache."""
        await self._ensure_redis()

        if self._redis_client:
            try:
                await self._redis_client.flushdb()
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
