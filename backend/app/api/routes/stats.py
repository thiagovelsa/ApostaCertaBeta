"""
Stats Routes
============

GET /api/partida/{matchId}/stats - Estatisticas de uma partida
"""

import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, HTTPException, Path

from ...models import StatsResponse
from ...services import StatsService
from ...dependencies import get_stats_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/partida/{match_id}/stats",
    response_model=StatsResponse,
    summary="Estatisticas detalhadas de uma partida",
    description="""
    Retorna estatisticas agregadas (medias e CVs) dos times
    em um periodo especifico.
    """,
)
async def get_stats(
    match_id: str = Path(
        ...,
        description="ID unico da partida",
        example="f4vscquffy37afgv0arwcbztg",
    ),
    filtro: Literal["geral", "5", "10"] = Query(
        default="geral",
        description="Periodo de analise (geral, ultimas 5, ultimas 10)",
    ),
    periodo: Literal["integral", "1T", "2T"] = Query(
        default="integral",
        description="Tempo do jogo para analise (integral, 1T=primeiro tempo, 2T=segundo tempo)",
    ),
    home_mando: Optional[Literal["casa", "fora"]] = Query(
        default=None,
        description="Subfiltro de mando para o mandante (casa=apenas jogos em casa, fora=apenas jogos fora)",
    ),
    away_mando: Optional[Literal["casa", "fora"]] = Query(
        default=None,
        description="Subfiltro de mando para o visitante (casa=apenas jogos em casa, fora=apenas jogos fora)",
    ),
    service: StatsService = Depends(get_stats_service),
) -> StatsResponse:
    """
    Busca estatisticas detalhadas de uma partida.

    - **match_id**: ID da partida (obrigatorio)
    - **filtro**: Periodo de analise
        - `geral`: Toda a temporada
        - `5`: Ultimas 5 partidas
        - `10`: Ultimas 10 partidas
    - **periodo**: Tempo do jogo para analise
        - `integral`: Jogo completo (90 minutos)
        - `1T`: Primeiro tempo (0-45 min)
        - `2T`: Segundo tempo (45-90 min)
    - **home_mando**: Subfiltro de mando para o mandante (opcional)
        - `casa`: Apenas jogos em casa
        - `fora`: Apenas jogos fora
    - **away_mando**: Subfiltro de mando para o visitante (opcional)
        - `casa`: Apenas jogos em casa
        - `fora`: Apenas jogos fora

    Retorna estatisticas de ambos os times com medias,
    coeficiente de variacao (CV) e classificacao de estabilidade.
    """
    try:
        return await service.calcular_stats(
            match_id, filtro, periodo, home_mando, away_mando
        )
    except ValueError as e:
        error_msg = str(e)
        # Diferencia erro de cache miss de outros erros de validacao
        if "nao encontrada" in error_msg.lower():
            logger.warning(f"[404] Partida nao encontrada: {match_id}")
            raise HTTPException(
                status_code=404,
                detail=error_msg,
            )
        else:
            # Outros ValueErrors (parsing, validacao)
            logger.error(f"[ERROR] Erro de validacao ao calcular stats: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro de validacao: {error_msg}",
            )
    except Exception as e:
        logger.exception(f"❌ Erro inesperado ao calcular stats para {match_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular estatisticas: {str(e)}",
        )
