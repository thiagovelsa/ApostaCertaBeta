"""
Stats Service
=============

Logica de negocio para calculo de estatisticas.

Filtros:
- "geral": Usa seasonstats (dados agregados da temporada)
- "5" ou "10": Busca ultimas N partidas via get-match-stats e calcula CV real
"""

import asyncio
import logging
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
)
from ..repositories import VStatsRepository
from ..utils.cv_calculator import calculate_cv, classify_cv
from .cache_service import CacheService

logger = logging.getLogger(__name__)


class StatsService:
    """Servico para calculo de estatisticas de partidas."""

    def __init__(
        self,
        vstats_repo: VStatsRepository,
        cache: CacheService,
    ):
        self.vstats = vstats_repo
        self.cache = cache

    async def calcular_stats(
        self,
        match_id: str,
        filtro: Literal["geral", "5", "10"] = "geral",
    ) -> StatsResponse:
        """
        Calcula estatisticas para uma partida.

        Args:
            match_id: ID da partida
            filtro: Periodo de analise (geral, ultimas 5, ultimas 10)

        Returns:
            StatsResponse com estatisticas calculadas
        """
        logger.info(f"[STATS] Calculando stats para partida {match_id[:8]}... (filtro={filtro})")

        # Tenta cache de stats
        cache_key = self.cache.build_key("stats", match_id, filtro)
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"  [CACHE HIT] Stats encontradas em cache")
            return StatsResponse(**cached)

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

        logger.info(f"  [OK] match_meta encontrado: {match_meta.get('home_name')} vs {match_meta.get('away_name')}")

        # Extrai dados do cache
        tournament_id = match_meta["tournament_id"]
        home_id = match_meta["home_id"]
        away_id = match_meta["away_id"]
        home_name = match_meta["home_name"]
        away_name = match_meta["away_name"]

        # Busca estatisticas de cada time
        home_stats = await self._get_team_stats(tournament_id, home_id, filtro)
        away_stats = await self._get_team_stats(tournament_id, away_id, filtro)

        # Monta partida a partir dos metadados
        partida = self._build_partida_from_meta(match_id, match_meta)

        # Determina numero de partidas analisadas
        limit = self._get_limit(filtro)

        # Calcula partidas analisadas (minimo 1 para satisfazer validacao Pydantic)
        if filtro != "geral":
            partidas_analisadas = limit
        else:
            # Para "geral", usa o numero de partidas do time
            # Se for 0 (time novo ou sem partidas), usa 1 como fallback
            partidas_analisadas = max(home_stats.get("matches", 20), 1)

        logger.info(f"  [COUNT] Partidas analisadas: {partidas_analisadas}")

        response = StatsResponse(
            partida=partida,
            filtro_aplicado=filtro,
            partidas_analisadas=partidas_analisadas,
            mandante=TimeComEstatisticas(
                id=home_id,
                nome=partida.mandante.nome,
                escudo=None,
                estatisticas=home_stats["estatisticas"],
            ),
            visitante=TimeComEstatisticas(
                id=away_id,
                nome=partida.visitante.nome,
                escudo=None,
                estatisticas=away_stats["estatisticas"],
            ),
        )

        # Salva no cache
        await self.cache.set(
            cache_key,
            response.model_dump(mode="json"),
            settings.cache_ttl_seasonstats,
        )

        return response

    async def _get_team_stats(
        self,
        tournament_id: str,
        team_id: str,
        filtro: str,
    ) -> dict:
        """
        Busca e calcula estatisticas de um time.

        - Filtro "geral": usa seasonstats (agregado)
        - Filtro "5" ou "10": busca partidas individuais e calcula CV real
        """
        limit = self._get_limit(filtro)

        if filtro == "geral":
            # Usa seasonstats (dados agregados da temporada)
            return await self._get_season_stats(tournament_id, team_id)
        else:
            # Busca ultimas N partidas e calcula estatisticas reais
            return await self._get_recent_matches_stats(tournament_id, team_id, limit)

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
        }

    async def _get_recent_matches_stats(
        self,
        tournament_id: str,
        team_id: str,
        limit: int,
    ) -> dict:
        """
        Busca estatisticas das ultimas N partidas via get-match-stats.
        Calcula CV real a partir dos dados individuais.
        """
        # 1. Busca IDs das ultimas partidas do time
        match_ids = await self._get_recent_match_ids(tournament_id, team_id, limit)

        if not match_ids:
            logger.warning(f"Nenhuma partida encontrada para time {team_id}")
            # Fallback para seasonstats
            return await self._get_season_stats(tournament_id, team_id)

        logger.info(f"[FETCH] Buscando stats de {len(match_ids)} partidas para time {team_id[:8]}...")

        # 2. Busca stats de cada partida em paralelo
        match_stats_list = await self._fetch_matches_stats(match_ids, team_id)

        if not match_stats_list:
            logger.warning(f"Nenhuma estatistica encontrada para time {team_id}")
            return await self._get_season_stats(tournament_id, team_id)

        # 3. Calcula medias e CV reais
        estatisticas = self._calculate_metrics_from_matches(match_stats_list)

        return {
            "estatisticas": estatisticas,
            "matches": len(match_stats_list),
        }

    async def _get_recent_match_ids(
        self,
        tournament_id: str,
        team_id: str,
        limit: int,
    ) -> List[str]:
        """
        Busca IDs das ultimas N partidas realizadas pelo time.

        ATUALIZADO (25/12/2025): Usa fetch_schedule_full em vez de fetch_schedule_month
        para obter a temporada completa (~380 jogos), garantindo que sempre haja
        partidas suficientes para os filtros 5/10.

        NOTA: O endpoint /schedule NAO retorna homeScore/awayScore na listagem,
        entao usamos a data como indicador (localDate < hoje = partida realizada).
        """
        from datetime import date as dt_date

        try:
            # MUDANCA: Usar schedule completo em vez de schedule/month
            # /schedule retorna ~380 jogos da temporada inteira
            # /schedule/month retorna apenas ~16 jogos do mes atual
            schedule = await self.vstats.fetch_schedule_full(tournament_id)
            all_matches = schedule.get("matches", [])

            logger.info(f"[SCHEDULE] Recebidas {len(all_matches)} partidas da temporada")

            # Data de hoje para comparacao
            today_str = dt_date.today().isoformat()  # YYYY-MM-DD
            logger.info(f"[DATE] Hoje={today_str}, Time ID={team_id}")

            # Filtra partidas do time que ja foram realizadas (data < hoje)
            # NOTA: O endpoint /schedule NAO retorna homeScore na listagem,
            # entao usamos localDate < hoje como proxy para "partida realizada"
            team_matches = []
            for match in all_matches:
                is_home = match.get("homeContestantId") == team_id
                is_away = match.get("awayContestantId") == team_id
                match_date = match.get("localDate", "")
                is_played = match_date < today_str  # Partida anterior a hoje

                if (is_home or is_away) and is_played:
                    team_matches.append(match)

            logger.info(f"[FILTER] {len(team_matches)} partidas disputadas do time {team_id[:8]}...")

            # Ordena por data (mais recentes primeiro)
            team_matches.sort(key=lambda m: m.get("localDate", ""), reverse=True)

            # Retorna IDs das ultimas N
            return [m.get("id") for m in team_matches[:limit] if m.get("id")]

        except Exception as e:
            logger.error(f"Erro ao buscar partidas recentes: {e}")
            return []

    async def _fetch_matches_stats(
        self,
        match_ids: List[str],
        team_id: str,
    ) -> List[dict]:
        """Busca estatisticas de cada partida em paralelo."""
        async def fetch_one(match_id: str) -> Optional[dict]:
            try:
                stats = await self.vstats.fetch_game_played_stats(match_id)
                return self._extract_team_match_stats(stats, team_id)
            except Exception as e:
                logger.debug(f"Erro ao buscar stats da partida {match_id}: {e}")
                return None

        results = await asyncio.gather(*[fetch_one(mid) for mid in match_ids])
        return [r for r in results if r is not None]

    def _extract_team_match_stats(self, match_data: dict, team_id: str) -> Optional[dict]:
        """Extrai estatisticas de um time de uma partida especifica."""
        try:
            stats_block = match_data.get("stats")
            home_id = match_data.get("homeId")
            away_id = match_data.get("awayId")
            if stats_block and home_id and away_id:
                if team_id == home_id:
                    idx = 0
                    opp_idx = 1
                    goals = match_data.get("homeScore")
                    goals_conceded = match_data.get("awayScore")
                elif team_id == away_id:
                    idx = 1
                    opp_idx = 0
                    goals = match_data.get("awayScore")
                    goals_conceded = match_data.get("homeScore")
                else:
                    return None

                def get_stat_value(name: str, index: int, default: float = 0.0) -> float:
                    values = stats_block.get(name) or []
                    if len(values) > index:
                        try:
                            return float(values[index])
                        except (TypeError, ValueError):
                            return default
                    return default

                total_scoring_att = get_stat_value("attempts", idx)
                total_scoring_att_conceded = get_stat_value("attempts", opp_idx)
                on_target = get_stat_value("attemptsOnGoal", idx)
                on_target_conceded = get_stat_value("attemptsOnGoal", opp_idx)
                won_corners = get_stat_value("corners", idx)
                lost_corners = get_stat_value("corners", opp_idx)

                return {
                    "wonCorners": won_corners,
                    "lostCorners": lost_corners,
                    "goals": float(goals or 0),
                    "goalsConceded": float(goals_conceded or 0),
                    "totalScoringAtt": total_scoring_att,
                    "totalShotsConceded": total_scoring_att_conceded,
                    "ontargetScoringAtt": on_target,
                    "ontargetScoringAttConceded": on_target_conceded,
                    "totalYellowCard": get_stat_value("yellowCards", idx),
                    "totalRedCard": get_stat_value("redCards", idx),
                    "fkFoulLost": get_stat_value("fouls", idx),
                    "saves": get_stat_value("saves", idx),
                }

            lineup = match_data.get("liveData", {}).get("lineUp", [])

            for team in lineup:
                if team.get("contestantId") == team_id:
                    stats = {s.get("type"): float(s.get("value", 0)) for s in team.get("stat", [])}
                    return {
                        "wonCorners": stats.get("wonCorners", 0),
                        "lostCorners": stats.get("lostCorners", 0),
                        "goals": stats.get("goals", 0),
                        "goalsConceded": stats.get("goalsConceded", 0),
                        "totalScoringAtt": stats.get("totalScoringAtt", 0),
                        "totalShotsConceded": stats.get("totalShotsConceded", 0),
                        "ontargetScoringAtt": stats.get("ontargetScoringAtt", 0),
                        "ontargetScoringAttConceded": stats.get("ontargetScoringAttConceded", 0),
                        "totalYellowCard": stats.get("totalYellowCard", 0),
                        "totalRedCard": stats.get("totalRedCard", 0),
                        "fkFoulLost": stats.get("fkFoulLost", 0),
                        "saves": stats.get("saves", 0),
                    }
            return None
        except Exception:
            return None

    def _calculate_metrics_from_matches(self, matches: List[dict]) -> EstatisticasTime:
        """Calcula metricas com CV real a partir de partidas individuais."""

        def calc_metric(field: str) -> EstatisticaMetrica:
            values = [m.get(field, 0) for m in matches]
            result = calculate_cv(values)

            if result is None:
                # Menos de 2 valores - usa media simples sem CV
                media = sum(values) / len(values) if values else 0
                return EstatisticaMetrica(
                    media=round(media, 2),
                    cv=0.0,
                    classificacao="Muito Estável",
                )

            media, cv, classificacao = result
            return EstatisticaMetrica(
                media=media,
                cv=cv,
                classificacao=classificacao,
            )

        def calc_feitos(field_made: str, field_conceded: str) -> EstatisticaFeitos:
            return EstatisticaFeitos(
                feitos=calc_metric(field_made),
                sofridos=calc_metric(field_conceded),
            )

        return EstatisticasTime(
            escanteios=calc_feitos("wonCorners", "lostCorners"),
            gols=calc_feitos("goals", "goalsConceded"),
            finalizacoes=calc_feitos("totalScoringAtt", "totalShotsConceded"),
            finalizacoes_gol=calc_feitos("ontargetScoringAtt", "ontargetScoringAttConceded"),
            cartoes_amarelos=calc_metric("totalYellowCard"),
            cartoes_vermelhos=calc_metric("totalRedCard"),
            faltas=calc_metric("fkFoulLost"),
        )

    def _calculate_metrics_from_season(self, stats: dict, matches: int) -> EstatisticasTime:
        """
        Calcula metricas a partir de seasonstats (dados agregados).
        CV é estimado pois não temos dados por partida.
        """

        def make_metric(value: float, cv_estimate: float = 0.35) -> EstatisticaMetrica:
            media = round(value / max(matches, 1), 2)
            return EstatisticaMetrica(
                media=media,
                cv=cv_estimate,
                classificacao=classify_cv(cv_estimate),
            )

        def make_feitos(made: float, conceded: float) -> EstatisticaFeitos:
            return EstatisticaFeitos(
                feitos=make_metric(made),
                sofridos=make_metric(conceded),
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
            ),
            gols=make_feitos(
                stats.get("goals", 0),
                stats.get("goalsConceded", 0),
            ),
            finalizacoes=make_feitos(
                total_shots,
                shots_conceded,
            ),
            finalizacoes_gol=make_feitos(
                shots_on_target,
                shots_on_target_conceded,
            ),
            cartoes_amarelos=make_metric(stats.get("totalYellowCard", 0), 0.55),
            cartoes_vermelhos=make_metric(stats.get("totalRedCard", 0), 0.85),
            faltas=make_metric(stats.get("fkFoulLost", 0), 0.40),
        )

    def _get_limit(self, filtro: str) -> int:
        """Retorna limite de partidas baseado no filtro."""
        if filtro == "5":
            return 5
        elif filtro == "10":
            return 10
        return 20  # geral

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

        logger.warning(f"[WARN] Formato de hora desconhecido: {time_str}, usando 00:00:00")
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
            competition.get("knownName")
            or competition.get("name")
            or "Desconhecida"
        )

        local_date = match_info.get("localDate") or match_info.get("date")
        if isinstance(local_date, str) and "T" in local_date:
            local_date = local_date.split("T")[0]

        local_time = match_info.get("localTime") or match_info.get("time") or "00:00:00"
        if isinstance(local_time, str):
            local_time = local_time.replace("Z", "")
            if "T" in local_time:
                local_time = local_time.split("T")[-1]
            local_time = local_time[:8]

        def pick_name(contestant: dict) -> str:
            return (
                contestant.get("officialName")
                or contestant.get("name")
                or contestant.get("shortName")
                or ""
            )

        return {
            "tournament_id": tournament_id,
            "home_id": home_id,
            "home_name": pick_name(home),
            "away_id": away_id,
            "away_name": pick_name(away),
            "competicao": competition_name,
            "data": local_date or "",
            "horario": local_time or "00:00:00",
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
