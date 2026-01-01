"""
Configuracao da Aplicacao
=========================

Carrega configuracoes do ambiente usando Pydantic Settings.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracoes da aplicacao carregadas do .env"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # VStats API
    vstats_api_url: str = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"
    vstats_api_timeout: int = 30

    # TheSportsDB API
    thesportsdb_api_key: str = "3"
    thesportsdb_api_url: str = "https://www.thesportsdb.com/api/v1/json"
    thesportsdb_api_timeout: int = 5

    # Cache Configuration
    redis_url: str = "redis://localhost:6379/0"
    cache_enabled: bool = True
    cache_version: int = 15  # Adiciona conversão de timezone para Brasil
    cache_ttl_schedule: int = 3600  # 1 hora
    cache_ttl_seasonstats: int = 21600  # 6 horas
    cache_ttl_badges: int = 604800  # 7 dias

    # Timezone
    target_timezone: str = "America/Sao_Paulo"

    # Application
    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS
    allowed_origins: str = (
        "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Retorna lista de origens permitidas para CORS"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Verifica se esta em ambiente de desenvolvimento"""
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        """Verifica se esta em ambiente de producao"""
        return self.env == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Retorna instancia singleton das configuracoes.
    Usa lru_cache para evitar recarregar .env a cada chamada.
    """
    return Settings()


# Instancia global para uso direto
settings = get_settings()
