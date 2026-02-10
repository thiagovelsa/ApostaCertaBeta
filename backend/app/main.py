"""
FastAPI Application
===================

Ponto de entrada da aplicacao.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .api.routes import api_router
from .dependencies import get_vstats_repository
from .exceptions import AppException

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicacao."""
    # Startup
    print(f"[START] Iniciando API em modo {settings.env}")
    print(f"[VSTATS] VStats API: {settings.vstats_api_url}")
    print(f"[CACHE] Cache habilitado: {settings.cache_enabled}")

    yield

    # Shutdown - fecha conexões HTTP
    print("[STOP] Encerrando API")
    vstats_repo = get_vstats_repository()
    await vstats_repo.close()


# Cria aplicacao FastAPI
app = FastAPI(
    title="Sistema de Análise de Estatísticas de Futebol",
    description="""
    API para análise detalhada de estatísticas de futebol com integração
    aos dados da VStats API. Fornece comparativas de desempenho home/away
    e métricas de estabilidade (Coeficiente de Variação).
    """,
    version="1.0.0",
    contact={
        "name": "Suporte",
        "email": "contato@palpitremestre.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Handler global de excecoes
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handler para excecoes da aplicacao."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "detail": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handler para excecoes nao tratadas."""
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Erro interno",
                "detail": str(exc),
            },
        )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "detail": "Ocorreu um erro inesperado",
        },
    )


# Inclui rotas da API
app.include_router(api_router)


# Rota de health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica se a API esta funcionando."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.env,
    }


# Rota raiz
@app.get("/", tags=["Root"])
async def root():
    """Rota raiz com informacoes da API."""
    return {
        "name": "Sistema de Análise de Estatísticas de Futebol",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Desabilitado em produção",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
    )
