"""
Stats Service
=============

Logica de negocio para calculo de estatisticas.

Filtros:
- "geral": Busca ate 50 partidas disputadas (por time) e calcula CV real (time-weighting)
- "5" ou "10": Busca ultimas N partidas disputadas e calcula CV real (time-weighting)

Obs: seasonstats existe como fallback quando nao ha partidas individuais suficientes.
"""

import asyncio
import logging
import math
from datetime import date as dt_date
from typing import List, Literal, Optional

from ..config import settings
from ..models import (
    StatsResponse,
    PartidaResumo,
    TimeInfo,
    EstatisticaMetrica,
    EstatisticaFeitos,
    EstatisticasTime,
    TimeComEstatisticas,
    ArbitroInfo,
    ContextoPartida,
    ContextoTime,
    ClassificacaoTimeInfo,
    H2HInfo,
)
from ..repositories import VStatsRepository
from ..utils.cv_calculator import classify_cv, calculate_estabilidade
from ..utils.contexto_vstats import (
    compute_rest_context,
    extract_h2h_any_comp,
    extract_ranking_list,
    extract_stage_name,
    extract_team_table_entry,
)
from .cache_service import CacheService

logger = logging.getLogger(__name__)


class StatsService:
    """Servico para calculo de estatisticas de partidas."""

    # Time decay factor (Dixon-Coles standard: 0.0065)
    # Decay rate: 30 days = 82%, 60 days = 68%, 90 days = 56%
    TIME_DECAY_FACTOR = 0.0065

    def __init__(
        self,
        vstats_repo: VStatsRepository,
        cache: CacheService,
    ):
        self.vstats = vstats_repo
        self.cache = cache

    def _calculate_time_weight(self, match_date_str: str) -> float:
        """
        Calcula peso exponencial baseado na idade da partida.

        Usa decay exponencial padrao Dixon-Coles:
        weight = e^(-decay * days_ago)

        Com decay = 0.0065:
        - Partida de hoje: 100%
        - Partida de 30 dias: 82%
        - Partida de 60 dias: 68%
        - Partida de 90 dias: 56%
        - Partida de 180 dias: 31%

        Args:
            match_date_str: Data da partida no formato "YYYY-MM-DD"

        Returns:
            Peso entre 0 e 1
        """
        try:
            from datetime import datetime

            match_date = datetime.strptime(match_date_str, "%Y-%m-%d").date()
            days_ago = (dt_date.today() - match_date).days
            weight = math.exp(-self.TIME_DECAY_FACTOR * max(days_ago, 0))
            return weight
        except (ValueError, TypeError):
            # Se nao conseguir parsear data, retorna peso 1.0 (sem penalidade)
            return 1.0

    def _weighted_mean(self, values: List[float], weights: List[float]) -> float:
        """
        Calcula media ponderada.

        Args:
            values: Lista de valores
            weights: Lista de pesos correspondentes

        Returns:
            Media ponderada
        """
        if not values or not weights or len(values) != len(weights):
            return 0.0
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0
        return sum(v * w for v, w in zip(values, weights)) / total_weight

    def _weighted_cv(
        self, values: List[float], weights: List[float], wmean: float
    ) -> float:
        """
        Calcula coeficiente de variacao ponderado.

        Formula: sqrt(sum(w * (v - wmean)^2) / sum(w)) / wmean

        Args:
            values: Lista de valores
            weights: Lista de pesos correspondentes
            wmean: Media ponderada pre-calculada

        Returns:
            CV ponderado (0 a 1+)
        """
        if not values or not weights or len(values) != len(weights):
            return 0.0
        if wmean == 0:
            return 0.0
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0

        # Variancia ponderada
        variance = (
            sum(w * (v - wmean) ** 2 for v, w in zip(values, weights)) / total_weight
        )
        std_dev = math.sqrt(variance)
        return std_dev / wmean

    def _get_period_indices(self, periodo: str, is_home: bool) -> tuple:
        """
        Retorna (idx, opp_idx) baseado no período e posição do time.

        Arrays da API: [home_FT, away_FT, home_1T, away_1T, home_2T, away_2T]

        Args:
            periodo: "integral", "1T" ou "2T"
            is_home: True se o time é mandante

        Returns:
            Tupla (idx, opp_idx) com os índices corretos para o período
        """
        base_indices = {
            "integral": (0, 1),
            "1T": (2, 3),
            "2T": (4, 5),
        }
        home_idx, away_idx = base_indices.get(periodo, (0, 1))

        if is_home:
            return (home_idx, away_idx)
        else:
            return (away_idx, home_idx)

    async def calcular_stats(
        self,
        match_id: str,
        filtro: Literal["geral", "5", "10"] = "geral",
        periodo: Literal["integral", "1T", "2T"] = "integral",
        home_mando: Optional[Literal["casa", "fora"]] = None,
        away_mando: Optional[Literal["casa", "fora"]] = None,
        debug: bool = False,
    ) -> StatsResponse:
        """
        Calcula estatisticas para uma partida.

        Args:
            match_id: ID da partida
            filtro: Periodo de analise (geral, ultimas 5, ultimas 10)
            periodo: Tempo do jogo (integral, 1T, 2T)
            home_mando: Subfiltro para mandante (casa/fora/None)
            away_mando: Subfiltro para visitante (casa/fora/None)

        Returns:
            StatsResponse com estatisticas calculadas
        """
        logger.info(
            f"[STATS] Calculando stats para partida {match_id[:8]}... (filtro={filtro}, periodo={periodo}, home_mando={home_mando}, away_mando={away_mando}, debug={debug})"
        )

        cache_key = self.cache.build_key(
            "stats", match_id, filtro, periodo, home_mando or "all", away_mando or "all"
        )
        # Tenta cache de stats (incluindo subfiltros de mando e periodo).
        # Quando debug=1, pulamos cache para não "poluir" com payload maior.
        if not debug:
            cached = await self.cache.get(cache_key)
            if isinstance(cached, dict) and cached:
                # Regressão: em versões antigas, o split-mando podia gravar no cache uma
                # "amostra por lado" acima do filtro (ex: 20/5), o que quebra a UI/contrato.
                # Se detectarmos, invalidamos e recalculamos.
                if filtro != "geral":
                    limit = self._get_limit(filtro)

                    def _to_int(v):
                        if v is None:
                            return None
                        try:
                            return int(v)
                        except (TypeError, ValueError):
                            return None

                    ctx = cached.get("contexto")
                    ajustes = (
                        ctx.get("ajustes_aplicados", [])
                        if isinstance(ctx, dict)
                        else []
                    )
                    has_seasonstats_fallback = (
                        isinstance(ajustes, list) and "seasonstats_fallback" in ajustes
                    )

                    pa = _to_int(cached.get("partidas_analisadas"))
                    pah = _to_int(cached.get("partidas_analisadas_mandante"))
                    pav = _to_int(cached.get("partidas_analisadas_visitante"))
                    has_sample_above_filter = any(
                        v is not None and v > limit for v in (pa, pah, pav)
                    )
                    if has_sample_above_filter and not has_seasonstats_fallback:
                        logger.info(
                            "  [CACHE STALE] Cache com amostra acima do filtro, invalidando..."
                        )
                        await self.cache.delete(cache_key)
                    else:
                        try:
                            logger.info("  [CACHE HIT] Stats encontradas em cache")
                            return StatsResponse(**cached)
                        except Exception as e:
                            logger.info(
                                "  [CACHE STALE] Cache invalido (%r), invalidando...",
                                e,
                            )
                            await self.cache.delete(cache_key)
                else:
                    try:
                        logger.info("  [CACHE HIT] Stats encontradas em cache")
                        return StatsResponse(**cached)
                    except Exception as e:
                        logger.info(
                            "  [CACHE STALE] Cache invalido (%r), invalidando...",
                            e,
                        )
                        await self.cache.delete(cache_key)

        # Busca metadados da partida (cacheados quando listamos partidas)
        match_meta_key = self.cache.build_key("match_meta", match_id)
        logger.debug(f"  [LOOKUP] Buscando match_meta com chave: {match_meta_key}")
        match_meta = await self.cache.get(match_meta_key)

        if not match_meta:
            logger.warning(f"  [MISS] match_meta NAO encontrado para {match_id}")
            match_meta = await self._fetch_match_meta(match_id)
            if match_meta:
                await self.cache.set(
                    match_meta_key,
                    match_meta,
                    ttl=86400,
                )
            else:
                # Se nao tiver em cache e nao conseguir reconstruir, retorna erro claro
                raise ValueError(
                    f"Partida {match_id} nao encontrada. "
                    "Busque as partidas primeiro via GET /api/partidas"
                )

        logger.info(
            f"  [OK] match_meta encontrado: {match_meta.get('home_name')} vs {match_meta.get('away_name')}"
        )

        # Extrai dados do cache
        tournament_id = match_meta["tournament_id"]
        home_id = match_meta["home_id"]
        away_id = match_meta["away_id"]
        match_date_str = match_meta.get("data") or ""

        # Busca schedule UMA vez para ambos os times (otimização de performance)
        schedule = await self._fetch_tournament_schedule(tournament_id)

        # Extrai referee_id do cache (evita chamada redundante a fetch_match_stats)
        referee_id = match_meta.get("referee_id")

        # Busca estatisticas de cada time, arbitro e contexto (preview + standings) em paralelo
        home_stats, away_stats, arbitro, match_preview, standings = await asyncio.gather(
            self._get_team_stats(
                tournament_id,
                home_id,
                filtro,
                periodo,
                home_mando,
                schedule,
                debug=debug,
            ),
            self._get_team_stats(
                tournament_id,
                away_id,
                filtro,
                periodo,
                away_mando,
                schedule,
                debug=debug,
            ),
            self._get_referee_info(match_id, referee_id=referee_id),
            self._fetch_match_preview_cached(match_id),
            self._fetch_standings_cached(tournament_id),
        )

        # Monta partida a partir dos metadados
        partida = self._build_partida_from_meta(match_id, match_meta)

        # Determina numero de partidas analisadas
        limit = self._get_limit(filtro)

        home_matches = int(home_stats.get("matches", 0) or 0)
        away_matches = int(away_stats.get("matches", 0) or 0)
        home_season_fallback = bool(home_stats.get("_seasonstats_fallback"))
        away_season_fallback = bool(away_stats.get("_seasonstats_fallback"))
        seasonstats_fallback_any = home_season_fallback or away_season_fallback

        # Por contrato, "partidas_analisadas_*" devem refletir a amostra usada por lado.
        # Em modo "Últimos N", clampamos por time quando há partidas individuais; no fallback seasonstats,
        # preservamos o tamanho real (transparência para a UI).
        home_used = home_matches
        away_used = away_matches
        if filtro != "geral":
            if not home_season_fallback:
                home_used = min(home_matches, limit)
            if not away_season_fallback:
                away_used = min(away_matches, limit)

        # Calcula partidas analisadas (minimo 1 para satisfazer validacao Pydantic)
        # Preferimos refletir o "pior lado" (min), especialmente com subfiltros (mando/periodo).
        if filtro != "geral":
            if seasonstats_fallback_any:
                partidas_analisadas = max(1, min(home_used, away_used))
            else:
                partidas_analisadas = max(1, min(home_used, away_used, limit))
        else:
            partidas_analisadas = max(
                1,
                min(home_used, away_used) or max(home_used, away_used, 1),
            )

        logger.info(
            f"  [COUNT] Partidas analisadas: {partidas_analisadas} (home={home_used}, away={away_used}, seasonstats_fallback={seasonstats_fallback_any})"
        )

        # Contexto pre-jogo (best-effort: nunca deve quebrar a resposta)
        contexto = self._build_contexto(
            match_date_str=match_date_str,
            schedule=schedule,
            home_id=home_id,
            away_id=away_id,
            match_preview=match_preview,
            standings=standings,
        )
        if seasonstats_fallback_any:
            # Transparência: não foi possível obter partidas individuais no recorte; usamos seasonstats (agregado).
            if contexto is None:
                contexto = ContextoPartida(
                    mandante=ContextoTime(),
                    visitante=ContextoTime(),
                )
            if "seasonstats_fallback" not in contexto.ajustes_aplicados:
                contexto.ajustes_aplicados.append("seasonstats_fallback")
        if (
            contexto is not None
            and periodo != "integral"
            and (
                bool(home_stats.get("_period_fallback_any"))
                or bool(away_stats.get("_period_fallback_any"))
            )
        ):
            # Transparencia: periodo solicitado, mas alguns payloads nao trazem arrays por tempo.
            # Usamos fallback para o integral (best-effort).
            if "periodo_fallback_integral" not in contexto.ajustes_aplicados:
                contexto.ajustes_aplicados.append("periodo_fallback_integral")
        h2h_any = extract_h2h_any_comp(match_preview)
        h2h_model = None
        if h2h_any is not None:
            h2h_model = H2HInfo(
                total_matches=h2h_any.total_matches,
                avg_goals_per_match=round(h2h_any.avg_goals_per_match, 3),
                home_wins=h2h_any.home_wins,
                away_wins=h2h_any.away_wins,
                draws=h2h_any.draws,
            )

        try:
            debug_amostra = None
            if debug:
                dbg_home = home_stats.get("_debug_amostra")
                dbg_away = away_stats.get("_debug_amostra")
                if isinstance(dbg_home, dict) and isinstance(dbg_away, dict):
                    debug_amostra = {"mandante": dbg_home, "visitante": dbg_away}

            response = StatsResponse(
                partida=partida,
                filtro_aplicado=filtro,
                partidas_analisadas=partidas_analisadas,
                partidas_analisadas_mandante=home_used,
                partidas_analisadas_visitante=away_used,
                mandante=TimeComEstatisticas(
                    id=home_id,
                    nome=partida.mandante.nome,
                    escudo=None,
                    estatisticas=home_stats["estatisticas"],
                    recent_form=home_stats.get("recent_form", []),
                ),
                visitante=TimeComEstatisticas(
                    id=away_id,
                    nome=partida.visitante.nome,
                    escudo=None,
                    estatisticas=away_stats["estatisticas"],
                    recent_form=away_stats.get("recent_form", []),
                ),
                arbitro=arbitro,
                contexto=contexto,
                h2h_all_comps=h2h_model,
                debug_amostra=debug_amostra,
            )
        except Exception as e:
            logger.error(f"[ERROR] Falha ao construir StatsResponse: {e}")
            logger.error(f"[DEBUG] home_stats keys: {list(home_stats.keys())}")
            logger.error(f"[DEBUG] away_stats keys: {list(away_stats.keys())}")
            logger.error(f"[DEBUG] home_stats estatisticas type: {type(home_stats.get('estatisticas'))}")
            logger.error(f"[DEBUG] arbitro: {arbitro}")
            raise

        # Salva no cache
        if not debug:
            await self.cache.set(
                cache_key,
                response.model_dump(mode="json"),
                settings.cache_ttl_seasonstats,
            )

        return response

    async def _fetch_match_preview_cached(self, match_id: str) -> Optional[dict]:
        cache_key = self.cache.build_key("matchpreview", match_id)
        cached = await self.cache.get(cache_key)
        if isinstance(cached, dict) and cached:
            return cached

        try:
            data = await self.vstats.fetch_match_preview(match_id)
        except Exception as e:
            logger.debug("[MATCHPREVIEW] Falha ao buscar preview: %r", e)
            return None

        if isinstance(data, dict) and data:
            await self.cache.set(cache_key, data, ttl=settings.cache_ttl_matchpreview)
            return data
        return None

    async def _fetch_standings_cached(self, tournament_id: str) -> Optional[dict]:
        cache_key = self.cache.build_key("standings", tournament_id)
        cached = await self.cache.get(cache_key)
        if isinstance(cached, dict) and cached:
            return cached

        try:
            data = await self.vstats.fetch_standings(tournament_id, detailed=False)
        except Exception as e:
            logger.debug("[STANDINGS] Falha ao buscar standings: %r", e)
            return None

        if isinstance(data, dict) and data:
            await self.cache.set(cache_key, data, ttl=settings.cache_ttl_standings)
            return data
        return None

    def _build_contexto(
        self,
        match_date_str: str,
        schedule: dict,
        home_id: str,
        away_id: str,
        match_preview: Optional[dict],
        standings: Optional[dict],
    ) -> Optional[ContextoPartida]:
        try:
            md = None
            if match_date_str:
                from datetime import date as _date

                md = _date.fromisoformat(str(match_date_str).split("T", 1)[0])

            schedule_matches = schedule.get("matches", []) if isinstance(schedule, dict) else []
            dias_home = dias_away = None
            jogos7_home = jogos7_away = None
            jogos14_home = jogos14_away = None
            if md is not None and isinstance(schedule_matches, list):
                dias_home, jogos7_home, jogos14_home = compute_rest_context(
                    schedule_matches, home_id, md
                )
                dias_away, jogos7_away, jogos14_away = compute_rest_context(
                    schedule_matches, away_id, md
                )

            ranking_list = extract_ranking_list(standings) if standings else []
            home_row = extract_team_table_entry(ranking_list, home_id) if ranking_list else None
            away_row = extract_team_table_entry(ranking_list, away_id) if ranking_list else None

            def mk_classificacao(row: Optional[dict]) -> Optional[ClassificacaoTimeInfo]:
                if not row:
                    return None
                try:
                    pos = int(row.get("rank") or row.get("position") or 0)
                except Exception:
                    pos = 0
                if pos <= 0:
                    return None
                pontos = 0
                jogos = 0
                saldo = None
                try:
                    pontos = int(row.get("points") or 0)
                except Exception:
                    pontos = 0
                try:
                    jogos = int(row.get("matchesPlayed") or 0)
                except Exception:
                    jogos = 0
                try:
                    if row.get("goaldifference") is not None:
                        saldo = int(row.get("goaldifference"))
                except Exception:
                    saldo = None
                return ClassificacaoTimeInfo(
                    posicao=pos,
                    pontos=pontos,
                    jogos=jogos,
                    saldo_gols=saldo,
                )

            ch = mk_classificacao(home_row)
            ca = mk_classificacao(away_row)

            h2h_any = extract_h2h_any_comp(match_preview)
            h2h_model = None
            if h2h_any is not None:
                h2h_model = H2HInfo(
                    total_matches=h2h_any.total_matches,
                    avg_goals_per_match=round(h2h_any.avg_goals_per_match, 3),
                    home_wins=h2h_any.home_wins,
                    away_wins=h2h_any.away_wins,
                    draws=h2h_any.draws,
                )

            fase = extract_stage_name(match_preview) if match_preview else None

            return ContextoPartida(
                mandante=ContextoTime(
                    dias_descanso=dias_home,
                    jogos_7d=jogos7_home,
                    jogos_14d=jogos14_home,
                    posicao=ch.posicao if ch else None,
                ),
                visitante=ContextoTime(
                    dias_descanso=dias_away,
                    jogos_7d=jogos7_away,
                    jogos_14d=jogos14_away,
                    posicao=ca.posicao if ca else None,
                ),
                classificacao_mandante=ch,
                classificacao_visitante=ca,
                h2h_all_comps=h2h_model,
                fase=fase,
            )
        except Exception as e:
            logger.debug("[CONTEXTO] Falha ao construir contexto: %r", e)
            return None

    async def _get_team_stats(
        self,
        tournament_id: str,
        team_id: str,
        filtro: str,
        periodo: Literal["integral", "1T", "2T"] = "integral",
        mando: Optional[Literal["casa", "fora"]] = None,
        schedule: Optional[dict] = None,
        debug: bool = False,
    ) -> dict:
        """
        Busca e calcula estatisticas de um time.
        Agora usa partidas individuais para TODOS os filtros (CV real).

        Args:
            periodo: Tempo do jogo (integral, 1T, 2T)
            mando: Subfiltro de mando (casa=apenas jogos em casa, fora=apenas jogos fora)
            schedule: Schedule do torneio (opcional, evita busca duplicada)
        """
        limit = self._get_limit(filtro)

        # SEMPRE usa partidas individuais para calcular CV real
        return await self._get_recent_matches_stats(
            tournament_id, team_id, limit, periodo, mando, schedule, debug=debug
        )

    async def _get_season_stats(self, tournament_id: str, team_id: str) -> dict:
        """Busca estatisticas agregadas da temporada via seasonstats."""
        seasonstats = await self.vstats.fetch_seasonstats(tournament_id, team_id)
        stats_raw = self.vstats.extract_team_stats(seasonstats)
        matches_played = stats_raw.get("matchesPlayed", 1)

        # Calcula metricas (CV estimado pois nao temos dados por partida)
        estatisticas = self._calculate_metrics_from_season(stats_raw, matches_played)

        return {
            "estatisticas": estatisticas,
            "matches": matches_played,
            # Flag interna: não há partidas individuais suficientes; usamos agregado de temporada.
            "_seasonstats_fallback": True,
        }

    async def _seasonstats_fallback_result(
        self,
        tournament_id: str,
        team_id: str,
        limit: int,
        periodo: str,
        mando,
        debug: bool,
        reason: str,
    ) -> dict:
        """Retorna resultado de seasonstats quando não há partidas individuais."""
        fallback = await self._get_season_stats(tournament_id, team_id)
        fallback["recent_form"] = []
        if debug:
            n_used = int(fallback.get("matches", 0) or 0)
            fallback["_debug_amostra"] = {
                "source": "seasonstats_fallback",
                "limit": limit,
                "periodo": periodo,
                "mando": mando,
                "n_used": n_used,
                "match_ids": [],
                "match_dates": [],
                "weights": [],
                "reason": reason,
            }
        return fallback

    async def _get_recent_matches_stats(
        self,
        tournament_id: str,
        team_id: str,
        limit: int,
        periodo: Literal["integral", "1T", "2T"] = "integral",
        mando: Optional[Literal["casa", "fora"]] = None,
        schedule: Optional[dict] = None,
        debug: bool = False,
    ) -> dict:
        """
        Busca estatisticas das ultimas N partidas via get-match-stats.
        Calcula CV real a partir dos dados individuais COM TIME-WEIGHTING.
        Tambem retorna recent_form (W/D/L) calculado dos gols de cada partida.

        ATUALIZADO (28/12/2025): Usa medias ponderadas por tempo (Dixon-Coles decay).
        Partidas mais recentes tem peso maior no calculo.

        Args:
            periodo: Tempo do jogo (integral, 1T, 2T)
            mando: Subfiltro de mando (casa=apenas jogos em casa, fora=apenas jogos fora)
            schedule: Schedule do torneio (opcional, evita busca duplicada)
        """
        # 1. Busca IDs e datas das ultimas partidas
        matches_data = await self._get_recent_matches_with_form(
            tournament_id, team_id, limit, mando, schedule
        )
        match_ids = matches_data.get("match_ids", [])
        match_dates = matches_data.get("match_dates", [])
        match_date_by_id: dict[str, Optional[str]] = {
            mid: (match_dates[i] if i < len(match_dates) else None)
            for i, mid in enumerate(match_ids or [])
            if mid
        }

        # Evita duplicatas (a API/schedule pode repetir IDs em alguns cenarios).
        # Mantem a ordem e tenta preservar o alinhamento com match_dates.
        if match_ids:
            uniq_ids: List[str] = []
            uniq_dates: List[Optional[str]] = []
            seen: set[str] = set()
            for i, mid in enumerate(match_ids):
                if not mid or mid in seen:
                    continue
                seen.add(mid)
                uniq_ids.append(mid)
                uniq_dates.append(match_dates[i] if i < len(match_dates) else None)
            match_ids = uniq_ids
            match_dates = uniq_dates
            match_date_by_id = {
                mid: (uniq_dates[i] if i < len(uniq_dates) else None)
                for i, mid in enumerate(uniq_ids)
                if mid
            }

        if not match_ids:
            logger.warning(f"Nenhuma partida encontrada para time {team_id}")
            return await self._seasonstats_fallback_result(
                tournament_id, team_id, limit, periodo, mando, debug, "no_matches"
            )

        logger.info(
            f"[FETCH] Buscando stats de {len(match_ids)} partidas para time {team_id[:8]}..."
        )

        # 2. Busca stats de cada partida em paralelo
        match_stats_list = await self._fetch_matches_stats(match_ids, team_id, periodo)

        if not match_stats_list:
            logger.warning(f"Nenhuma estatistica encontrada para time {team_id}")
            return await self._seasonstats_fallback_result(
                tournament_id, team_id, limit, periodo, mando, debug, "no_match_stats"
            )

        # 3. Calcula recent_form (W/D/L) a partir dos gols de cada partida
        recent_form: List[Literal["W", "D", "L"]] = []
        for stats in match_stats_list:
            goals = stats.get("goals", 0)
            goals_conceded = stats.get("goalsConceded", 0)
            if goals > goals_conceded:
                recent_form.append("W")
            elif goals < goals_conceded:
                recent_form.append("L")
            else:
                recent_form.append("D")

        logger.info(f"[FORM] {team_id[:8]}: {recent_form}")

        # 4. Calcula pesos temporais para cada partida
        # Importante: match_stats_list pode ter "buracos" (falhas) e não é seguro assumir
        # que o índice i corresponde à data i. Usamos _match_id para alinhar.
        weights: List[float] = []
        for m in match_stats_list:
            mid = m.get("_match_id")
            mdate = match_date_by_id.get(mid) if isinstance(mid, str) else None
            if mdate:
                weights.append(self._calculate_time_weight(mdate))
            else:
                weights.append(1.0)  # sem data, peso máximo

        if weights:
            logger.info(
                f"[TIME-WEIGHT] Pesos: {[round(w, 2) for w in weights[:5]]}... (min={min(weights):.2f}, max={max(weights):.2f})"
            )

        # 5. Calcula medias e CV reais COM pesos temporais
        estatisticas = self._calculate_metrics_from_matches(match_stats_list, weights)

        period_fallback_any = any(bool(m.get("_period_fallback")) for m in match_stats_list)

        result: dict = {
            "estatisticas": estatisticas,
            "matches": len(match_stats_list),
            "recent_form": recent_form,
            "_period_fallback_any": period_fallback_any,
        }
        if debug:
            match_ids_used: List[str] = []
            match_dates_used: List[Optional[str]] = []
            weights_used: List[float] = []
            for m, w in zip(match_stats_list, weights):
                mid = m.get("_match_id")
                if isinstance(mid, str) and mid:
                    match_ids_used.append(mid)
                    match_dates_used.append(match_date_by_id.get(mid))
                    weights_used.append(float(w))

            result["_debug_amostra"] = {
                "source": "matches",
                "limit": limit,
                "periodo": periodo,
                "mando": mando,
                "n_used": len(match_ids_used),
                "match_ids": match_ids_used,
                "match_dates": match_dates_used,
                "weights": weights_used,
                "reason": None,
            }

        return result

    async def _fetch_tournament_schedule(self, tournament_id: str) -> dict:
        """
        Busca e cacheia schedule do torneio.
        Usado para compartilhar entre múltiplas chamadas na mesma requisição.

        Returns:
            dict com o schedule completo do torneio
        """
        cache_key = self.cache.build_key("schedule_full", tournament_id)
        cached = await self.cache.get(cache_key)

        if cached:
            logger.info(f"[SCHEDULE] Cache HIT para torneio {tournament_id[:8]}...")
            return cached

        logger.info(f"[SCHEDULE] Buscando schedule do torneio {tournament_id[:8]}...")
        schedule = await self.vstats.fetch_schedule_full(tournament_id)

        # Cache por 1 hora
        await self.cache.set(cache_key, schedule, ttl=3600)

        return schedule

    async def _get_recent_matches_with_form(
        self,
        tournament_id: str,
        team_id: str,
        limit: int,
        mando: Optional[Literal["casa", "fora"]] = None,
        schedule: Optional[dict] = None,
    ) -> dict:
        """
        Busca IDs e datas das ultimas N partidas realizadas pelo time.

        ATUALIZADO (28/12/2025): Agora retorna tambem match_dates para Time-Weighting.
        Partidas mais recentes recebem peso maior no calculo de estatisticas.

        Args:
            mando: Subfiltro de mando (casa=apenas jogos em casa, fora=apenas jogos fora)

        Returns:
            dict com {
                "match_ids": List[str],
                "match_dates": List[str],  # Formato "YYYY-MM-DD"
            }
        """
        try:
            # Usa schedule passado ou busca/cacheia se não fornecido
            if schedule is None:
                schedule = await self._fetch_tournament_schedule(tournament_id)
            all_matches = schedule.get("matches", [])

            logger.info(
                f"[SCHEDULE] Recebidas {len(all_matches)} partidas da temporada"
            )

            from datetime import datetime

            today = dt_date.today()
            logger.debug(f"[DATE] Hoje={today.isoformat()}, Time ID={team_id}")

            def parse_local_date(value: str):
                if not value or not isinstance(value, str):
                    return None
                try:
                    return datetime.strptime(value, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    return None

            def parse_score(match: dict, key: str, alt_key: str) -> Optional[float]:
                raw = match.get(key)
                if raw is None:
                    side = match.get(alt_key)
                    if isinstance(side, dict):
                        raw = side.get("score")
                if raw is None:
                    return None
                if isinstance(raw, bool):
                    return None
                if isinstance(raw, (int, float)):
                    return float(raw)
                if isinstance(raw, str) and raw.strip() != "":
                    try:
                        return float(raw)
                    except ValueError:
                        return None
                return None

            # Heurística:
            # 1) Se o schedule traz placares (homeScore/awayScore ou home.score/away.score) para ALGUMA partida,
            #    então exigimos placar para considerar "disputada". Isso evita pegar adiadas/sem placar.
            # 2) Se o schedule NÃO traz placares (algumas competições retornam apenas IDs + datas),
            #    não podemos usar esse critério; então usamos apenas data válida <= hoje.
            schedule_has_any_score = False
            for m in all_matches:
                if parse_score(m, "homeScore", "home") is not None or parse_score(
                    m, "awayScore", "away"
                ) is not None:
                    schedule_has_any_score = True
                    break

            # Filtra partidas do time.
            team_matches = []
            for match in all_matches:
                is_home = match.get("homeContestantId") == team_id
                is_away = match.get("awayContestantId") == team_id
                if not (is_home or is_away):
                    continue

                match_date_str = match.get("localDate", "")
                if not match_date_str and isinstance(match.get("date"), str):
                    # Alguns schedules retornam ISO datetime em "date".
                    # Ex: "2025-12-23T00:00:00+00:00" -> "2025-12-23"
                    match_date_str = str(match.get("date", "")).split("T", 1)[0]
                match_date = parse_local_date(match_date_str)
                if match_date is None:
                    # Evita casos como localDate="" (que antes passava pelo filtro de string).
                    continue

                home_score = parse_score(match, "homeScore", "home")
                away_score = parse_score(match, "awayScore", "away")

                if schedule_has_any_score:
                    # Modo estrito: considera disputada apenas com placar (evita jogos adiados/sem info).
                    is_played = home_score is not None and away_score is not None
                    if not is_played:
                        continue
                else:
                    # Modo relaxado: sem placares no schedule, então filtramos por data <= hoje.
                    # Jogos futuros podem passar se a API marcar errado; serão descartados mais tarde
                    # quando não conseguirmos extrair stats do "get-game-played-stats".
                    if match_date > today:
                        continue

                team_matches.append(
                    {
                        **match,
                        "_is_home": is_home,
                        "_local_date": match_date,
                        "_home_score": home_score,
                        "_away_score": away_score,
                    }
                )

            logger.info(
                f"[FILTER] {len(team_matches)} partidas disputadas do time {team_id[:8]}..."
            )

            # Ordena por data (mais recentes primeiro)
            team_matches.sort(
                key=lambda m: m.get("_local_date") or dt_date.min, reverse=True
            )

            # Aplica subfiltro de mando (casa/fora) se especificado
            if mando == "casa":
                team_matches = [m for m in team_matches if m.get("_is_home")]
                logger.info(
                    f"[MANDO] Filtrado para jogos em CASA: {len(team_matches)} partidas"
                )
            elif mando == "fora":
                team_matches = [m for m in team_matches if not m.get("_is_home")]
                logger.info(
                    f"[MANDO] Filtrado para jogos FORA: {len(team_matches)} partidas"
                )

            # Extrai IDs e datas das ultimas N
            match_ids = []
            match_dates = []  # Para Time-Weighting

            # Log para debug - verificar estrutura do primeiro match
            if team_matches:
                sample = team_matches[0]
                logger.info(f"[DEBUG] Sample match keys: {list(sample.keys())[:15]}")
                logger.info(
                    f"[DEBUG] homeScore={sample.get('homeScore')}, awayScore={sample.get('awayScore')}"
                )
                logger.info(
                    f"[DEBUG] score keys check: home.score={sample.get('home', {}).get('score') if isinstance(sample.get('home'), dict) else 'N/A'}"
                )

            for match in team_matches[:limit]:
                match_id = match.get("id")
                match_date = match.get("_local_date")
                if match_id:
                    match_ids.append(match_id)
                    match_dates.append(match_date.isoformat() if match_date else "")


            # Log de datas para verificar Time-Weighting
            if match_dates:
                logger.info(
                    f"[TIME-WEIGHT] Datas: {match_dates[:3]}... (total: {len(match_dates)})"
                )

            return {
                "match_ids": match_ids,
                "match_dates": match_dates,
            }

        except Exception as e:
            logger.error(f"Erro ao buscar partidas recentes: {e}")
            return {"match_ids": [], "match_dates": []}

    async def _fetch_matches_stats(
        self,
        match_ids: List[str],
        team_id: str,
        periodo: Literal["integral", "1T", "2T"] = "integral",
    ) -> List[dict]:
        """
        Busca estatisticas de cada partida em paralelo.

        Args:
            periodo: Tempo do jogo (integral, 1T, 2T)
        """

        # Limita concorrencia para reduzir timeouts/overload na VStats.
        sem = asyncio.Semaphore(10)

        async def fetch_one(match_id: str) -> Optional[dict]:
            try:
                # Cache individual — dados de partidas passadas são imutáveis.
                cache_key = self.cache.build_key("matchstats_raw", match_id)
                cached_raw = await self.cache.get(cache_key)
                if isinstance(cached_raw, dict) and cached_raw:
                    extracted = self._extract_team_match_stats(cached_raw, team_id, periodo)
                    if extracted is not None:
                        extracted["_match_id"] = match_id
                    return extracted

                # Usa /get-game-played-stats (11KB) ao invés de /get-match-stats (31KB).
                # Payload 64% mais leve; stats agregadas por time (sem dados por jogador).
                # _extract_team_match_stats já suporta o formato stats block (homeId/awayId).
                async with sem:
                    stats = await self.vstats.fetch_game_played_stats(match_id)

                # Cache do payload cru (independe de time/periodo)
                if isinstance(stats, dict) and stats:
                    await self.cache.set(
                        cache_key, stats, ttl=settings.cache_ttl_matchstats_raw
                    )

                extracted = self._extract_team_match_stats(stats, team_id, periodo)
                if extracted is None:
                    return None
                # Mantém o ID para alinhar pesos temporais (datas) mesmo quando há falhas.
                extracted["_match_id"] = match_id
                return extracted
            except Exception as e:
                logger.debug(f"Erro ao buscar stats da partida {match_id}: {e}")
                return None

        # Dedupe defensivo (mesmo apos dedupe acima): reduz chamadas duplicadas e logs repetidos.
        match_ids = list(dict.fromkeys([mid for mid in match_ids if mid]))

        results = await asyncio.gather(*[fetch_one(mid) for mid in match_ids])
        return [r for r in results if r is not None]

    def _extract_team_match_stats(
        self,
        match_data: dict,
        team_id: str,
        periodo: Literal["integral", "1T", "2T"] = "integral",
    ) -> Optional[dict]:
        """
        Extrai estatisticas de um time de uma partida especifica.

        Args:
            periodo: Tempo do jogo para extrair stats (integral, 1T, 2T)
                     Arrays da API: [home_FT, away_FT, home_1T, away_1T, home_2T, away_2T]
        """
        try:
            stats_block = match_data.get("stats")
            home_id = match_data.get("homeId")
            away_id = match_data.get("awayId")
            if stats_block and home_id and away_id:
                is_home = team_id == home_id
                is_away = team_id == away_id

                if not is_home and not is_away:
                    return None

                # Usa indices dinamicos baseados no periodo
                idx, opp_idx = self._get_period_indices(periodo, is_home)
                fallback_idx, fallback_opp_idx = self._get_period_indices("integral", is_home)
                period_fallback_used = False

                # Gols: homeScore/awayScore sao sempre full-time
                # Para 1T/2T, tentamos extrair do array "goals" se existir
                if is_home:
                    goals_ft = match_data.get("homeScore") or 0
                    goals_conceded_ft = match_data.get("awayScore") or 0
                else:
                    goals_ft = match_data.get("awayScore") or 0
                    goals_conceded_ft = match_data.get("homeScore") or 0

                def get_stat_value(
                    name: str,
                    index: int,
                    default: float = 0.0,
                    fallback_index: Optional[int] = None,
                ) -> float:
                    nonlocal period_fallback_used
                    values = stats_block.get(name) or []
                    if len(values) > index:
                        try:
                            return float(values[index])
                        except (TypeError, ValueError):
                            return default
                    if (
                        fallback_index is not None
                        and isinstance(fallback_index, int)
                        and len(values) > fallback_index
                    ):
                        try:
                            period_fallback_used = True
                            return float(values[fallback_index])
                        except (TypeError, ValueError):
                            return default
                    # Fallback: se array menor que esperado (ex: sem dados por tempo)
                    return default

                # Stats com dados por periodo (6 elementos)
                fb_idx = fallback_idx if periodo != "integral" else None
                fb_opp = fallback_opp_idx if periodo != "integral" else None
                total_scoring_att = get_stat_value("attempts", idx, fallback_index=fb_idx)
                total_scoring_att_conceded = get_stat_value(
                    "attempts", opp_idx, fallback_index=fb_opp
                )
                on_target = get_stat_value(
                    "attemptsOnGoal", idx, fallback_index=fb_idx
                )
                on_target_conceded = get_stat_value(
                    "attemptsOnGoal", opp_idx, fallback_index=fb_opp
                )
                won_corners = get_stat_value("corners", idx, fallback_index=fb_idx)
                lost_corners = get_stat_value("corners", opp_idx, fallback_index=fb_opp)
                yellow_cards = get_stat_value(
                    "yellowCards", idx, fallback_index=fb_idx
                )
                fouls = get_stat_value("fouls", idx, fallback_index=fb_idx)
                saves = get_stat_value("saves", idx, fallback_index=fb_idx)

                # Gols por periodo (se disponivel no array "goals")
                goals_array = stats_block.get("goals") or []
                if len(goals_array) > max(idx, opp_idx):
                    goals = get_stat_value("goals", idx)
                    goals_conceded = get_stat_value("goals", opp_idx)
                else:
                    # Fallback para full-time se nao tem por periodo
                    goals = float(goals_ft)
                    goals_conceded = float(goals_conceded_ft)

                out = {
                    "wonCorners": won_corners,
                    "lostCorners": lost_corners,
                    "goals": goals,
                    "goalsConceded": goals_conceded,
                    "totalScoringAtt": total_scoring_att,
                    "totalShotsConceded": total_scoring_att_conceded,
                    "ontargetScoringAtt": on_target,
                    "ontargetScoringAttConceded": on_target_conceded,
                    "totalYellowCard": yellow_cards,
                    "totalRedCard": get_stat_value(
                        "redCards", idx, fallback_index=fb_idx
                    ),
                    "fkFoulLost": fouls,
                    "saves": saves,
                }
                if periodo != "integral" and period_fallback_used:
                    out["_period_fallback"] = True
                return out

            lineup = match_data.get("liveData", {}).get("lineUp", [])
            period_fallback_used = False

            def parse_float(v, default: float = 0.0) -> float:
                try:
                    return float(v)
                except (TypeError, ValueError):
                    return default

            def pick_lineup_value(stat: dict) -> float:
                nonlocal period_fallback_used
                # VStats lineUp.stat includes full match in `value` and halves in `fh`/`sh`.
                # If `fh`/`sh` is missing, fall back to full match value so the endpoint
                # still returns something (best-effort).
                if periodo == "1T":
                    fh = stat.get("fh")
                    if fh is not None:
                        return parse_float(fh)
                    period_fallback_used = True
                    return parse_float(stat.get("value", 0))
                if periodo == "2T":
                    sh = stat.get("sh")
                    if sh is not None:
                        return parse_float(sh)
                    period_fallback_used = True
                    return parse_float(stat.get("value", 0))
                return parse_float(stat.get("value", 0))

            # Build stats dict for each team
            team_stats_map = {}
            for team in lineup:
                contest_id = team.get("contestantId")
                if contest_id:
                    team_stats_map[contest_id] = {
                        s.get("type"): pick_lineup_value(s)
                        for s in team.get("stat", [])
                    }

            # Get our team's stats
            if team_id not in team_stats_map:
                return None

            stats = team_stats_map[team_id]

            # Find opponent's stats for conceded values
            # VStats API doesn't return "totalShotsConceded" - it's opponent's totalScoringAtt
            opponent_stats = None
            for contest_id, opp_stats in team_stats_map.items():
                if contest_id != team_id:
                    opponent_stats = opp_stats
                    break

            # Get conceded values from opponent's stats
            shots_conceded = 0.0
            shots_on_target_conceded = 0.0
            if opponent_stats:
                shots_conceded = opponent_stats.get("totalScoringAtt", 0)
                shots_on_target_conceded = opponent_stats.get("ontargetScoringAtt", 0)

            out = {
                "wonCorners": stats.get("wonCorners", 0),
                "lostCorners": stats.get("lostCorners", 0),
                "goals": stats.get("goals", 0),
                "goalsConceded": stats.get("goalsConceded", 0),
                "totalScoringAtt": stats.get("totalScoringAtt", 0),
                "totalShotsConceded": shots_conceded,
                "ontargetScoringAtt": stats.get("ontargetScoringAtt", 0),
                "ontargetScoringAttConceded": shots_on_target_conceded,
                "totalYellowCard": stats.get("totalYellowCard", 0),
                "totalRedCard": stats.get("totalRedCard", 0),
                "fkFoulLost": stats.get("fkFoulLost", 0),
                "saves": stats.get("saves", 0),
            }
            if periodo != "integral" and period_fallback_used:
                out["_period_fallback"] = True
            return out
        except Exception:
            return None

    def _calculate_metrics_from_matches(
        self, matches: List[dict], weights: Optional[List[float]] = None
    ) -> EstatisticasTime:
        """
        Calcula metricas com CV real a partir de partidas individuais.

        ATUALIZADO (28/12/2025): Usa medias ponderadas por tempo (Time-Weighting).
        Partidas mais recentes tem peso maior no calculo de media e CV.

        Args:
            matches: Lista de estatisticas de cada partida
            weights: Lista de pesos temporais (opcional, default=pesos iguais)
        """
        # Se nao tiver pesos, usa pesos iguais (1.0 para todos)
        if weights is None or len(weights) != len(matches):
            weights = [1.0] * len(matches)

        def calc_metric(field: str, stat_type: str) -> EstatisticaMetrica:
            values = [float(m.get(field, 0)) for m in matches]

            if len(values) < 2:
                # Menos de 2 valores - CV nao e confiavel.
                media = sum(values) / len(values) if values else 0
                return EstatisticaMetrica(
                    media=round(media, 2),
                    cv=1.0,
                    classificacao="N/A",
                    estabilidade=0,
                )

            # Calcula media ponderada
            wmean = self._weighted_mean(values, weights)

            # Media ~0 => CV indefinido; evita "confianca falsa" (1 - 0).
            if wmean == 0:
                return EstatisticaMetrica(
                    media=round(wmean, 2),
                    cv=1.0,
                    classificacao="N/A",
                    estabilidade=0,
                )

            # Calcula CV ponderado
            cv = self._weighted_cv(values, weights, wmean)

            # Classifica CV usando funcoes existentes
            classificacao = classify_cv(cv, stat_type)
            estabilidade = calculate_estabilidade(cv, stat_type)

            return EstatisticaMetrica(
                media=round(wmean, 2),
                cv=round(cv, 3),
                classificacao=classificacao,
                estabilidade=estabilidade,
            )

        def calc_feitos(
            field_made: str, field_conceded: str, stat_type: str
        ) -> EstatisticaFeitos:
            return EstatisticaFeitos(
                feitos=calc_metric(field_made, stat_type),
                sofridos=calc_metric(field_conceded, stat_type),
            )

        return EstatisticasTime(
            escanteios=calc_feitos("wonCorners", "lostCorners", "escanteios"),
            gols=calc_feitos("goals", "goalsConceded", "gols"),
            finalizacoes=calc_feitos(
                "totalScoringAtt", "totalShotsConceded", "finalizacoes"
            ),
            finalizacoes_gol=calc_feitos(
                "ontargetScoringAtt", "ontargetScoringAttConceded", "finalizacoes_gol"
            ),
            cartoes_amarelos=calc_metric("totalYellowCard", "cartoes_amarelos"),
            faltas=calc_metric("fkFoulLost", "faltas"),
        )

    def _calculate_metrics_from_season(
        self, stats: dict, matches: int
    ) -> EstatisticasTime:
        """
        Calcula metricas a partir de seasonstats (dados agregados).
        CV é estimado pois não temos dados por partida.
        """

        def make_metric(
            value: float, stat_type: str, cv_estimate: float = 0.35
        ) -> EstatisticaMetrica:
            media = round(value / max(matches, 1), 2)
            estabilidade = calculate_estabilidade(cv_estimate, stat_type)
            return EstatisticaMetrica(
                media=media,
                cv=cv_estimate,
                classificacao=classify_cv(cv_estimate, stat_type),
                estabilidade=estabilidade,
            )

        def make_feitos(
            made: float, conceded: float, stat_type: str
        ) -> EstatisticaFeitos:
            return EstatisticaFeitos(
                feitos=make_metric(made, stat_type),
                sofridos=make_metric(conceded, stat_type),
            )

        total_shots = stats.get("totalScoringAtt", 0)
        shots_conceded = stats.get("totalShotsConceded")
        if shots_conceded is None:
            shots_conceded = total_shots * 0.8

        shots_on_target = stats.get("ontargetScoringAtt", 0)
        shots_on_target_conceded = stats.get("ontargetScoringAttConceded")
        if shots_on_target_conceded is None:
            shots_on_target_conceded = shots_on_target * 0.7

        return EstatisticasTime(
            escanteios=make_feitos(
                stats.get("wonCorners", 0),
                stats.get("lostCorners", 0),
                "escanteios",
            ),
            gols=make_feitos(
                stats.get("goals", 0),
                stats.get("goalsConceded", 0),
                "gols",
            ),
            finalizacoes=make_feitos(
                total_shots,
                shots_conceded,
                "finalizacoes",
            ),
            finalizacoes_gol=make_feitos(
                shots_on_target,
                shots_on_target_conceded,
                "finalizacoes_gol",
            ),
            cartoes_amarelos=make_metric(
                stats.get("totalYellowCard", 0), "cartoes_amarelos", 0.55
            ),
            faltas=make_metric(stats.get("fkFoulLost", 0), "faltas", 0.40),
        )

    def _get_limit(self, filtro: str) -> int:
        """Retorna limite de partidas baseado no filtro."""
        if filtro == "5":
            return 5
        elif filtro == "10":
            return 10
        return 50  # geral - busca até 50 partidas da temporada

    def _parse_time(self, time_str: str):
        """
        Parse time string em varios formatos possiveis.

        Formatos suportados:
        - "HH:MM:SS" (ex: "17:00:00")
        - "HH:MM:SS.ffffff" (ex: "17:00:00.000000")
        - "HH:MM" (ex: "17:00")
        """
        from datetime import datetime, time

        if not time_str:
            return time(0, 0, 0)

        # Remove microsegundos se existirem
        if "." in time_str:
            time_str = time_str.split(".")[0]

        # Tenta diferentes formatos
        formats = ["%H:%M:%S", "%H:%M"]
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt).time()
            except ValueError:
                continue

        logger.warning(
            f"[WARN] Formato de hora desconhecido: {time_str}, usando 00:00:00"
        )
        return time(0, 0, 0)

    async def _fetch_match_meta(self, match_id: str) -> Optional[dict]:
        """Busca metadados da partida diretamente da VStats."""
        try:
            match_data = await self.vstats.fetch_match_stats(match_id)
        except Exception as e:
            logger.error(f"[ERROR] Falha ao buscar match_meta da VStats: {e}")
            return None

        match_info = match_data.get("matchInfo", {})
        tournament_calendar = match_info.get("tournamentCalendar", {})
        tournament_id = tournament_calendar.get("id")

        contestants = match_info.get("contestant", [])
        home = next((c for c in contestants if c.get("position") == "home"), None)
        away = next((c for c in contestants if c.get("position") == "away"), None)

        if not tournament_id or not home or not away:
            logger.warning("[WARN] match_meta incompleto ao reconstruir via VStats")
            return None

        home_id = home.get("id")
        away_id = away.get("id")
        if not home_id or not away_id:
            logger.warning("[WARN] IDs dos times ausentes no match_meta")
            return None

        competition = match_info.get("competition", {})
        competition_name = (
            competition.get("knownName") or competition.get("name") or "Desconhecida"
        )

        # Alinhamento de timezone:
        # - matchInfo.time e matchInfo.date vem em UTC (com 'Z')
        # - os endpoints de schedule ja retornam horario em America/Sao_Paulo
        # Para manter consistencia (mesmo sem ter listado partidas antes), convertemos UTC -> target_timezone.
        data_str = ""
        horario_str = "00:00:00"

        raw_date_utc = match_info.get("date")
        raw_time_utc = match_info.get("time")

        if isinstance(raw_date_utc, str) and isinstance(raw_time_utc, str):
            try:
                from datetime import datetime
                from datetime import timedelta, timezone

                try:
                    from zoneinfo import ZoneInfo  # Python 3.9+
                except Exception:  # pragma: no cover
                    ZoneInfo = None  # type: ignore[assignment]

                date_part = raw_date_utc.split("T", 1)[0]
                time_part = raw_time_utc.strip()
                if "T" in time_part:
                    time_part = time_part.split("T")[-1]
                time_part = time_part.replace("Z", "")
                time_part = time_part.split(".", 1)[0]  # remove ms se existirem
                time_part = time_part[:8]
                if len(time_part) == 5:
                    time_part = f"{time_part}:00"

                dt_utc = datetime.fromisoformat(f"{date_part}T{time_part}+00:00")

                # Windows/Python pode nao ter base IANA instalada (tzdata),
                # entao fazemos fallback para offset fixo quando necessario.
                target_tz = None
                if ZoneInfo is not None:
                    try:
                        target_tz = ZoneInfo(settings.target_timezone)
                    except Exception:
                        target_tz = None

                if target_tz is None:
                    if settings.target_timezone == "America/Sao_Paulo":
                        target_tz = timezone(timedelta(hours=-3))
                    else:
                        target_tz = timezone.utc

                dt_br = dt_utc.astimezone(target_tz)
                data_str = dt_br.date().isoformat()
                horario_str = dt_br.time().replace(tzinfo=None).isoformat(timespec="seconds")
            except Exception:
                # Fallback abaixo (nao deve ser comum).
                pass

        if not data_str:
            local_date = match_info.get("localDate") or match_info.get("date")
            if isinstance(local_date, str) and "T" in local_date:
                local_date = local_date.split("T", 1)[0]

            local_time = (
                match_info.get("localTime") or match_info.get("time") or "00:00:00"
            )
            if isinstance(local_time, str):
                local_time = local_time.strip()
                if "T" in local_time:
                    local_time = local_time.split("T")[-1]
                local_time = local_time.replace("Z", "")
                local_time = local_time.split(".", 1)[0]
                local_time = local_time[:8]
                if len(local_time) == 5:
                    local_time = f"{local_time}:00"

            data_str = local_date or ""
            horario_str = local_time or "00:00:00"

        def pick_name(contestant: dict) -> str:
            return (
                contestant.get("officialName")
                or contestant.get("name")
                or contestant.get("shortName")
                or ""
            )

        # Extrai referee_id para evitar chamada redundante em _get_referee_info
        match_officials = (
            match_data.get("liveData", {})
            .get("matchDetailExtra", {})
            .get("matchOfficials", [])
        )
        main_referee = next(
            (ref for ref in match_officials if ref.get("type") == "Main"), None
        )
        referee_id = main_referee.get("id") if main_referee else None

        return {
            "tournament_id": tournament_id,
            "home_id": home_id,
            "home_name": pick_name(home),
            "away_id": away_id,
            "away_name": pick_name(away),
            "competicao": competition_name,
            "data": data_str,
            "horario": horario_str,
            "referee_id": referee_id,
        }

    def _build_partida_from_meta(self, match_id: str, meta: dict) -> PartidaResumo:
        """Constroi PartidaResumo a partir de metadados cacheados."""
        from datetime import datetime

        try:
            data_obj = datetime.strptime(meta["data"], "%Y-%m-%d").date()
        except (ValueError, KeyError) as e:
            logger.error(f"[ERROR] Erro ao parsear data: {meta.get('data')} - {e}")
            raise ValueError(f"Formato de data invalido: {meta.get('data')}")

        horario_obj = self._parse_time(meta.get("horario", "00:00:00"))

        return PartidaResumo(
            id=match_id,
            tournament_id=meta["tournament_id"],
            data=data_obj,
            horario=horario_obj,
            competicao=meta["competicao"],
            estadio=None,  # Nao temos no cache, mas nao e essencial
            mandante=TimeInfo(
                id=meta["home_id"],
                nome=meta["home_name"],
                codigo=meta["home_name"][:3].upper(),
            ),
            visitante=TimeInfo(
                id=meta["away_id"],
                nome=meta["away_name"],
                codigo=meta["away_name"][:3].upper(),
            ),
        )

    async def _get_referee_info(
        self, match_id: str, referee_id: Optional[str] = None
    ) -> Optional[ArbitroInfo]:
        """
        Busca informacoes do arbitro da partida.

        Args:
            match_id: ID da partida
            referee_id: ID do arbitro (opcional, evita chamada a fetch_match_stats)

        1. Se referee_id fornecido, pula fetch_match_stats
        2. Busca estatisticas do arbitro via get-by-prsn
        """
        main_referee: Optional[dict] = None
        try:
            # Se nao temos referee_id, busca da partida
            if not referee_id:
                match_data = await self.vstats.fetch_match_stats(match_id)

                match_detail_extra = match_data.get("liveData", {}).get(
                    "matchDetailExtra", {}
                )
                match_officials = match_detail_extra.get("matchOfficials", [])

                if not match_officials:
                    logger.info(
                        f"[REFEREE] Nenhum arbitro encontrado para partida {match_id[:8]}"
                    )
                    return None

                main_referee = next(
                    (ref for ref in match_officials if ref.get("type") == "Main"), None
                )

                if not main_referee:
                    return None

                referee_id = main_referee.get("id")
                if not referee_id:
                    return None
            else:
                logger.info(
                    f"[REFEREE] Usando referee_id do cache: {referee_id[:8]}..."
                )

            # Busca estatisticas do arbitro
            referee_stats = await self.vstats.fetch_referee_stats(referee_id)

            # Extrai nome
            nome = referee_stats.get("name", "")
            if not nome and main_referee:
                first_name = main_referee.get("firstName", "")
                last_name = main_referee.get("lastName", "")
                nome = f"{first_name} {last_name}".strip()
            if not nome:
                nome = "Arbitro nao identificado"

            # Extrai estatisticas do torneio
            tournament_stats = referee_stats.get("tournamentStats", [])

            if tournament_stats:
                # Primeira competicao (assume que é a principal/atual)
                stats_competicao = tournament_stats[0]
                partidas_competicao = int(stats_competicao.get("matches", 0))
                avg_cards_competicao = float(stats_competicao.get("averageCards", 0))
                avg_fouls = stats_competicao.get("averageFouls")
                if avg_fouls:
                    avg_fouls = float(avg_fouls)

                # Total na temporada (soma de TODAS as competicoes)
                partidas_temporada = sum(
                    int(t.get("matches", 0)) for t in tournament_stats
                )

                # Media de cartoes na temporada (media ponderada)
                total_cartoes = sum(
                    int(t.get("matches", 0)) * float(t.get("averageCards", 0))
                    for t in tournament_stats
                )
                avg_cards_temporada = (
                    total_cartoes / partidas_temporada
                    if partidas_temporada > 0
                    else 0.0
                )
            else:
                partidas_competicao = 0
                partidas_temporada = 0
                avg_cards_competicao = 0.0
                avg_cards_temporada = 0.0
                avg_fouls = None

            logger.info(
                f"[REFEREE] {nome}: {partidas_competicao} jogos/{avg_cards_competicao:.1f} cartoes (comp), "
                f"{partidas_temporada} jogos/{avg_cards_temporada:.1f} cartoes (temp)"
            )

            return ArbitroInfo(
                id=referee_id,
                nome=nome,
                partidas=partidas_competicao,
                partidas_temporada=partidas_temporada,
                media_cartoes_amarelos=avg_cards_competicao,
                media_cartoes_temporada=avg_cards_temporada,
                media_faltas=avg_fouls,
            )

        except Exception as e:
            logger.warning(f"[REFEREE] Erro ao buscar arbitro: {e}")
            return None
