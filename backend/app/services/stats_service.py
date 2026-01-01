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
)
from ..repositories import VStatsRepository
from ..utils.cv_calculator import classify_cv, calculate_estabilidade
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
            f"[STATS] Calculando stats para partida {match_id[:8]}... (filtro={filtro}, periodo={periodo}, home_mando={home_mando}, away_mando={away_mando})"
        )

        # Tenta cache de stats (incluindo subfiltros de mando e periodo)
        cache_key = self.cache.build_key(
            "stats", match_id, filtro, periodo, home_mando or "all", away_mando or "all"
        )
        cached = await self.cache.get(cache_key)
        if cached:
            # Verifica se o cache tem dados validos do arbitro (nao apenas null)
            # cached.get("arbitro") retorna None se a chave nao existe OU se o valor eh null
            if cached.get("arbitro") is not None:
                logger.info("  [CACHE HIT] Stats encontradas em cache (com arbitro)")
                return StatsResponse(**cached)
            else:
                logger.info(
                    "  [CACHE STALE] Cache sem dados de arbitro, invalidando..."
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

        # Busca schedule UMA vez para ambos os times (otimização de performance)
        schedule = await self._fetch_tournament_schedule(tournament_id)

        # Extrai referee_id do cache (evita chamada redundante a fetch_match_stats)
        referee_id = match_meta.get("referee_id")

        # Busca estatisticas de cada time e arbitro em paralelo
        home_stats, away_stats, arbitro = await asyncio.gather(
            self._get_team_stats(
                tournament_id, home_id, filtro, periodo, home_mando, schedule
            ),
            self._get_team_stats(
                tournament_id, away_id, filtro, periodo, away_mando, schedule
            ),
            self._get_referee_info(match_id, referee_id=referee_id),
        )

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
        periodo: Literal["integral", "1T", "2T"] = "integral",
        mando: Optional[Literal["casa", "fora"]] = None,
        schedule: Optional[dict] = None,
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
            tournament_id, team_id, limit, periodo, mando, schedule
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
        }

    async def _get_recent_matches_stats(
        self,
        tournament_id: str,
        team_id: str,
        limit: int,
        periodo: Literal["integral", "1T", "2T"] = "integral",
        mando: Optional[Literal["casa", "fora"]] = None,
        schedule: Optional[dict] = None,
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

        if not match_ids:
            logger.warning(f"Nenhuma partida encontrada para time {team_id}")
            # Fallback para seasonstats
            fallback = await self._get_season_stats(tournament_id, team_id)
            fallback["recent_form"] = []
            return fallback

        logger.info(
            f"[FETCH] Buscando stats de {len(match_ids)} partidas para time {team_id[:8]}..."
        )

        # 2. Busca stats de cada partida em paralelo
        match_stats_list = await self._fetch_matches_stats(match_ids, team_id, periodo)

        if not match_stats_list:
            logger.warning(f"Nenhuma estatistica encontrada para time {team_id}")
            fallback = await self._get_season_stats(tournament_id, team_id)
            fallback["recent_form"] = []
            return fallback

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
        # Ajusta match_dates ao tamanho real de match_stats_list (podem diferir se alguma falhou)
        weights = []
        for i in range(len(match_stats_list)):
            if i < len(match_dates) and match_dates[i]:
                weight = self._calculate_time_weight(match_dates[i])
            else:
                weight = 1.0  # Sem data, peso maximo
            weights.append(weight)

        if weights:
            logger.info(
                f"[TIME-WEIGHT] Pesos: {[round(w, 2) for w in weights[:5]]}... (min={min(weights):.2f}, max={max(weights):.2f})"
            )

        # 5. Calcula medias e CV reais COM pesos temporais
        estatisticas = self._calculate_metrics_from_matches(match_stats_list, weights)

        return {
            "estatisticas": estatisticas,
            "matches": len(match_stats_list),
            "recent_form": recent_form,
        }

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
        Busca IDs das ultimas N partidas realizadas pelo time E calcula W/D/L.

        ATUALIZADO (28/12/2025): Agora retorna tambem match_dates para Time-Weighting.
        Partidas mais recentes recebem peso maior no calculo de estatisticas.

        Args:
            mando: Subfiltro de mando (casa=apenas jogos em casa, fora=apenas jogos fora)

        Returns:
            dict com {
                "match_ids": List[str],
                "match_dates": List[str],  # Formato "YYYY-MM-DD"
                "recent_form": List[Literal["W", "D", "L"]]
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

            today_str = dt_date.today().isoformat()
            logger.debug(f"[DATE] Hoje={today_str}, Time ID={team_id}")

            # Filtra partidas do time que ja foram realizadas
            team_matches = []
            for match in all_matches:
                is_home = match.get("homeContestantId") == team_id
                is_away = match.get("awayContestantId") == team_id
                match_date = match.get("localDate", "")
                is_played = match_date < today_str

                if (is_home or is_away) and is_played:
                    team_matches.append(
                        {
                            **match,
                            "_is_home": is_home,
                        }
                    )

            logger.info(
                f"[FILTER] {len(team_matches)} partidas disputadas do time {team_id[:8]}..."
            )

            # Ordena por data (mais recentes primeiro)
            team_matches.sort(key=lambda m: m.get("localDate", ""), reverse=True)

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

            # Extrai IDs, datas e calcula W/D/L das ultimas N
            match_ids = []
            match_dates = []  # Para Time-Weighting
            recent_form = []

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
                match_date = match.get("localDate", "")
                if match_id:
                    match_ids.append(match_id)
                    match_dates.append(match_date)

                # Calcula W/D/L a partir dos scores
                # Tenta diferentes formatos possíveis
                home_score = match.get("homeScore")
                away_score = match.get("awayScore")

                # Se não encontrou, tenta formato alternativo
                if home_score is None:
                    home_score = (
                        match.get("home", {}).get("score")
                        if isinstance(match.get("home"), dict)
                        else None
                    )
                if away_score is None:
                    away_score = (
                        match.get("away", {}).get("score")
                        if isinstance(match.get("away"), dict)
                        else None
                    )

                is_home = match.get("_is_home", False)

                if home_score is not None and away_score is not None:
                    team_goals = home_score if is_home else away_score
                    opp_goals = away_score if is_home else home_score

                    if team_goals > opp_goals:
                        recent_form.append("W")
                    elif team_goals < opp_goals:
                        recent_form.append("L")
                    else:
                        recent_form.append("D")

            logger.info(
                f"[FORM] Time {team_id[:8]}: {recent_form[:10]} (total: {len(recent_form)})"
            )

            # Log de datas para verificar Time-Weighting
            if match_dates:
                logger.info(
                    f"[TIME-WEIGHT] Datas: {match_dates[:3]}... (total: {len(match_dates)})"
                )

            return {
                "match_ids": match_ids,
                "match_dates": match_dates,
                "recent_form": recent_form,
            }

        except Exception as e:
            logger.error(f"Erro ao buscar partidas recentes: {e}")
            return {"match_ids": [], "match_dates": [], "recent_form": []}

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

        async def fetch_one(match_id: str) -> Optional[dict]:
            try:
                # Usa /get-match-stats conforme documentação (PROJETO_SISTEMA_ANALISE.md)
                # Estrutura: liveData.lineUp[].stat[]
                stats = await self.vstats.fetch_match_stats(match_id)
                return self._extract_team_match_stats(stats, team_id, periodo)
            except Exception as e:
                logger.debug(f"Erro ao buscar stats da partida {match_id}: {e}")
                return None

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

                # Gols: homeScore/awayScore sao sempre full-time
                # Para 1T/2T, tentamos extrair do array "goals" se existir
                if is_home:
                    goals_ft = match_data.get("homeScore") or 0
                    goals_conceded_ft = match_data.get("awayScore") or 0
                else:
                    goals_ft = match_data.get("awayScore") or 0
                    goals_conceded_ft = match_data.get("homeScore") or 0

                def get_stat_value(
                    name: str, index: int, default: float = 0.0
                ) -> float:
                    values = stats_block.get(name) or []
                    if len(values) > index:
                        try:
                            return float(values[index])
                        except (TypeError, ValueError):
                            return default
                    # Fallback: se array menor que esperado (ex: sem dados por tempo)
                    return default

                # Stats com dados por periodo (6 elementos)
                total_scoring_att = get_stat_value("attempts", idx)
                total_scoring_att_conceded = get_stat_value("attempts", opp_idx)
                on_target = get_stat_value("attemptsOnGoal", idx)
                on_target_conceded = get_stat_value("attemptsOnGoal", opp_idx)
                won_corners = get_stat_value("corners", idx)
                lost_corners = get_stat_value("corners", opp_idx)
                yellow_cards = get_stat_value("yellowCards", idx)
                fouls = get_stat_value("fouls", idx)
                saves = get_stat_value("saves", idx)

                # Gols por periodo (se disponivel no array "goals")
                goals_array = stats_block.get("goals") or []
                if len(goals_array) > max(idx, opp_idx):
                    goals = get_stat_value("goals", idx)
                    goals_conceded = get_stat_value("goals", opp_idx)
                else:
                    # Fallback para full-time se nao tem por periodo
                    goals = float(goals_ft)
                    goals_conceded = float(goals_conceded_ft)

                return {
                    "wonCorners": won_corners,
                    "lostCorners": lost_corners,
                    "goals": goals,
                    "goalsConceded": goals_conceded,
                    "totalScoringAtt": total_scoring_att,
                    "totalShotsConceded": total_scoring_att_conceded,
                    "ontargetScoringAtt": on_target,
                    "ontargetScoringAttConceded": on_target_conceded,
                    "totalYellowCard": yellow_cards,
                    "totalRedCard": get_stat_value("redCards", idx),
                    "fkFoulLost": fouls,
                    "saves": saves,
                }

            lineup = match_data.get("liveData", {}).get("lineUp", [])

            for team in lineup:
                if team.get("contestantId") == team_id:
                    stats = {
                        s.get("type"): float(s.get("value", 0))
                        for s in team.get("stat", [])
                    }
                    return {
                        "wonCorners": stats.get("wonCorners", 0),
                        "lostCorners": stats.get("lostCorners", 0),
                        "goals": stats.get("goals", 0),
                        "goalsConceded": stats.get("goalsConceded", 0),
                        "totalScoringAtt": stats.get("totalScoringAtt", 0),
                        "totalShotsConceded": stats.get("totalShotsConceded", 0),
                        "ontargetScoringAtt": stats.get("ontargetScoringAtt", 0),
                        "ontargetScoringAttConceded": stats.get(
                            "ontargetScoringAttConceded", 0
                        ),
                        "totalYellowCard": stats.get("totalYellowCard", 0),
                        "totalRedCard": stats.get("totalRedCard", 0),
                        "fkFoulLost": stats.get("fkFoulLost", 0),
                        "saves": stats.get("saves", 0),
                    }
            return None
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
                # Menos de 2 valores - usa media simples sem CV
                media = sum(values) / len(values) if values else 0
                return EstatisticaMetrica(
                    media=round(media, 2),
                    cv=0.0,
                    classificacao="Muito Estável",
                    estabilidade=100,
                )

            # Calcula media ponderada
            wmean = self._weighted_mean(values, weights)

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
            "data": local_date or "",
            "horario": local_time or "00:00:00",
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
            if not nome:
                first_name = main_referee.get("firstName", "")
                last_name = main_referee.get("lastName", "")
                nome = f"{first_name} {last_name}".strip()

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
