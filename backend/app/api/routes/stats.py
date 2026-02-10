"""Stats Routes.

Endpoints:
- GET /api/partida/{matchId}/stats
- GET /api/partida/{matchId}/analysis
"""

import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, HTTPException, Path

from ...models import StatsResponse, StatsAnalysisResponse
from ...services import StatsService, AnalysisService
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
        examples=["f4vscquffy37afgv0arwcbztg"],
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


@router.get(
    "/partida/{match_id}/analysis",
    response_model=StatsAnalysisResponse,
    summary="Análise consolidada (stats + previsões + over/under)",
)
async def get_analysis(
    match_id: str = Path(
        ...,
        description="ID unico da partida",
        examples=["f4vscquffy37afgv0arwcbztg"],
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
    debug: bool = Query(
        default=False,
        description="Quando true (ex: debug=1), inclui 'debug_amostra' com IDs/datas/pesos das partidas usadas no recorte",
    ),
    service: StatsService = Depends(get_stats_service),
) -> StatsAnalysisResponse:
    """Retorna stats + previsões + over/under no mesmo payload."""

    analysis_service = AnalysisService()

    no_subfilters = not home_mando and not away_mando
    same_subfilter = home_mando and away_mando and home_mando == away_mando

    try:
        if no_subfilters or same_subfilter:
            logger.info(f"[ANALYSIS] Buscando stats para {match_id[:8]}...")
            stats = await service.calcular_stats(
                match_id, filtro, periodo, home_mando, away_mando, debug=debug
            )
            logger.info(f"[ANALYSIS] Stats obtidas com sucesso")
        else:
            # Busca cada lado separadamente para não contaminar os filtros
            logger.info(f"[ANALYSIS] Buscando stats separados para {match_id[:8]}...")
            home_stats = await service.calcular_stats(
                match_id, filtro, periodo, home_mando, None, debug=debug
            )
            away_stats = await service.calcular_stats(
                match_id, filtro, periodo, None, away_mando, debug=debug
            )
            stats = home_stats
            stats.visitante = away_stats.visitante
            stats.partidas_analisadas_visitante = away_stats.partidas_analisadas_visitante
            stats.arbitro = home_stats.arbitro or away_stats.arbitro
            stats.contexto = home_stats.contexto or away_stats.contexto
            stats.h2h_all_comps = home_stats.h2h_all_comps or away_stats.h2h_all_comps
            # Merge do debug_amostra no modo split-mando (preserva o recorte por lado).
            if home_stats.debug_amostra is not None:
                merged_dbg = home_stats.debug_amostra.model_copy(deep=True)
                if away_stats.debug_amostra is not None:
                    merged_dbg.visitante = away_stats.debug_amostra.visitante
                stats.debug_amostra = merged_dbg
            elif away_stats.debug_amostra is not None:
                stats.debug_amostra = away_stats.debug_amostra.model_copy(deep=True)
            # Recalcula n efetivo (min) após merge.
            nh = stats.partidas_analisadas_mandante or stats.partidas_analisadas
            na = stats.partidas_analisadas_visitante or stats.partidas_analisadas
            try:
                nh_i = int(nh)
            except (TypeError, ValueError):
                nh_i = int(stats.partidas_analisadas)
            try:
                na_i = int(na)
            except (TypeError, ValueError):
                na_i = int(stats.partidas_analisadas)

            has_seasonstats_fallback = bool(
                stats.contexto
                and getattr(stats.contexto, "ajustes_aplicados", None)
                and "seasonstats_fallback" in stats.contexto.ajustes_aplicados
            )

            # Respeita o filtro no modo split-mando (quando há partidas individuais).
            # Se houve fallback seasonstats, mantemos a amostra real (transparência e coerência).
            if filtro != "geral":
                if has_seasonstats_fallback:
                    stats.partidas_analisadas = max(1, min(nh_i, na_i))
                else:
                    try:
                        limit = int(filtro)
                    except (TypeError, ValueError):
                        limit = 50
                    stats.partidas_analisadas = max(1, min(nh_i, na_i, limit))
            else:
                stats.partidas_analisadas = max(1, min(nh_i, na_i))
            logger.info(f"[ANALYSIS] Stats separados obtidos com sucesso")

        logger.info(f"[ANALYSIS] Calculando previsões...")
        previsoes = analysis_service.build_previsoes(stats, home_mando, away_mando)
        logger.info(f"[ANALYSIS] Previsões calculadas com sucesso")
        
        logger.info(f"[ANALYSIS] Calculando over/under...")
        over_under = analysis_service.build_over_under(
            stats, previsoes, home_mando, away_mando
        )
        logger.info(f"[ANALYSIS] Over/under calculado com sucesso")

        logger.info(f"[ANALYSIS] Construindo resposta final...")
        response = StatsAnalysisResponse(
            **stats.model_dump(mode="python"),
            previsoes=previsoes,
            over_under=over_under,
        )
        logger.info(f"[ANALYSIS] Resposta construída com sucesso!")
        return response
    except ValueError as e:
        error_msg = str(e)
        if "nao encontrada" in error_msg.lower():
            logger.warning(f"[404] Partida nao encontrada: {match_id}")
            raise HTTPException(status_code=404, detail=error_msg)
        logger.error(f"[ANALYSIS ERROR] ValueError: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Erro de validacao: {error_msg}")
    except Exception as e:
        logger.exception(f"❌ Erro inesperado ao calcular análise para {match_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular análise: {str(e)}",
        )
