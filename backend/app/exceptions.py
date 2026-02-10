"""
Excecoes Customizadas
=====================

Excecoes especificas da aplicacao.
"""

from typing import Optional


class AppException(Exception):
    """Excecao base da aplicacao."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)


class NotFoundError(AppException):
    """Recurso nao encontrado."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} nao encontrado: {identifier}",
            status_code=404,
        )


class ValidationError(AppException):
    """Erro de validacao de dados."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
        )


class VStatsAPIError(AppException):
    """Erro ao comunicar com VStats API."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(
            message=f"Erro VStats API: {message}",
            status_code=status_code,
        )


class BadgeAPIError(AppException):
    """Erro ao buscar escudo."""

    def __init__(self, message: str):
        super().__init__(
            message=f"Erro ao buscar escudo: {message}",
            status_code=502,
        )
