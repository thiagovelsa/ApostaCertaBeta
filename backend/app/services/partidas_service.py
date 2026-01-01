"""
Partidas Service
================

Logica de negocio para busca e listagem de partidas.
"""

import asyncio
import logging
from datetime import date, datetime
from typing import List, Tuple
from zoneinfo import ZoneInfo

from ..config import settings
from ..models import PartidaResumo, PartidaListResponse, TimeInfo
from ..repositories import VStatsRepository
from .cache_service import CacheService

logger = logging.getLogger(__name__)


class PartidasService:
    """Servico para operacoes com partidas."""

    def __init__(
        self,
        vstats_repo: VStatsRepository,
        cache: CacheService,
    ):
        self.vstats = vstats_repo
        self.cache = cache

    async def get_partidas_por_data(
        self,
        target_date: date,
    ) -> PartidaListResponse:
        """
        Busca todas as partidas para uma data especifica.

        Args:
            target_date: Data das partidas

        Returns:
            PartidaListResponse com lista de partidas
        """
        # Tenta cache primeiro
        cache_key = self.cache.build_key("partidas", target_date.isoformat())
        cached = await self.cache.get(cache_key)
        if cached:
            return PartidaListResponse(**cached)

        # Busca lista de competicoes com cache de 24h
        calendar_cache_key = self.cache.build_key("calendar", "all")
        competitions = await self.cache.get(calendar_cache_key)
        
        if competitions:
            logger.info(f"[CALENDAR] Cache HIT - {len(competitions)} competicoes")
        else:
            # Busca dinamicamente via /calendar
            try:
                competitions = await self.vstats.fetch_calendar()
                logger.info(
                    f"[CALENDAR] API - Encontradas {len(competitions)} competicoes"
                )
                # Cacheia por 24 horas
                await self.cache.set(calendar_cache_key, competitions, ttl=86400)
            except Exception as e:
                logger.warning(f"[CALENDAR] Erro na API: {str(e)}")
                # Fallback para competicoes conhecidas
                from ..known_competitions import get_fallback_competitions
                competitions = get_fallback_competitions()
                logger.info(
                    f"[CALENDAR] FALLBACK - Usando {len(competitions)} competicoes conhecidas"
                )

        # Busca partidas de todas as competicoes EM PARALELO (com limite de concorrência)
        logger.info(
            f"[SEARCH] Buscando partidas para {target_date.isoformat()} em {len(competitions)} competicoes..."
        )

        # Limita concorrência para não sobrecarregar a API VStats
        semaphore = asyncio.Semaphore(10)

        async def fetch_safe(comp: dict) -> Tuple[str, List[PartidaResumo]]:
            """Wrapper seguro que retorna lista vazia em caso de erro."""
            async with semaphore:
                tournament_id = comp.get("id")
                comp_name = comp.get("name", "Desconhecida")

                if not tournament_id:
                    return comp_name, []

                try:
                    matches = await self._fetch_competition_matches(
                        tournament_id,
                        target_date,
                        comp_name,
                    )
                    return comp_name, matches
                except Exception as e:
                    logger.debug(f"  [WARN] {comp_name}: {str(e)[:50]}")
                    return comp_name, []

        # Executa todas as buscas em paralelo (max 10 simultâneas)
        results = await asyncio.gather(*[fetch_safe(comp) for comp in competitions])

        # Consolida resultados
        all_matches = []
        for comp_name, matches in results:
            if matches:
                logger.info(f"  [COMP] {comp_name}: {len(matches)} partidas")
                all_matches.extend(matches)

        logger.info(f"[DONE] Total: {len(all_matches)} partidas encontradas")

        # Ordena por horario
        all_matches.sort(key=lambda m: m.horario)

        # Cacheia metadados de cada partida para uso no stats_service
        for partida in all_matches:
            match_meta_key = self.cache.build_key("match_meta", partida.id)
            await self.cache.set(
                match_meta_key,
                {
                    "tournament_id": partida.tournament_id,
                    "home_id": partida.mandante.id,
                    "home_name": partida.mandante.nome,
                    "away_id": partida.visitante.id,
                    "away_name": partida.visitante.nome,
                    "competicao": partida.competicao,
                    "data": partida.data.isoformat(),
                    "horario": partida.horario.isoformat(),
                },
                ttl=86400,  # 24 horas
            )

        response = PartidaListResponse(
            data=target_date,
            total_partidas=len(all_matches),
            partidas=all_matches,
        )

        # Salva no cache
        await self.cache.set(
            cache_key,
            response.model_dump(mode="json"),
            settings.cache_ttl_schedule,
        )

        return response

    async def _fetch_competition_matches(
        self,
        tournament_id: str,
        target_date: date,
        competition_name: str,
    ) -> List[PartidaResumo]:
        """
        Busca partidas de uma competicao especifica.
        
        Estratégia otimizada:
        1. Tenta /schedule/week primeiro (~20 partidas, muito rápido)
        2. Se data não estiver na semana, usa /schedule completo (cache 1h)
        """
        target_str = target_date.isoformat()
        
        # Tenta cache primeiro (pode ser de week ou full)
        schedule_cache_key = self.cache.build_key("schedule_week", tournament_id)
        schedule_data = await self.cache.get(schedule_cache_key)
        
        if schedule_data:
            # Cache hit - verifica se a data está nos dados
            all_matches = schedule_data.get("matches", [])
            filtered = [m for m in all_matches if m.get("localDate") == target_str]
            if filtered:
                return self._convert_matches(filtered, competition_name, tournament_id)
        
        # Tenta /schedule/week primeiro (muito mais rápido)
        try:
            week_data = await self.vstats.fetch_schedule_week(tournament_id)
            all_matches = week_data.get("matches", [])
            # Cache week por 1h
            await self.cache.set(schedule_cache_key, week_data, ttl=3600)
            
            filtered = [m for m in all_matches if m.get("localDate") == target_str]
            if filtered:
                return self._convert_matches(filtered, competition_name, tournament_id)
        except Exception:
            pass  # Fallback para schedule completo
        
        # Se não encontrou na semana, usa schedule completo (cache separado)
        full_cache_key = self.cache.build_key("schedule_full", tournament_id)
        full_data = await self.cache.get(full_cache_key)
        
        if not full_data:
            full_data = await self.vstats.fetch_schedule_full(tournament_id)
            await self.cache.set(full_cache_key, full_data, ttl=3600)
        
        all_matches = full_data.get("matches", [])
        filtered = [m for m in all_matches if m.get("localDate") == target_str]
        return self._convert_matches(filtered, competition_name, tournament_id)

    def _convert_matches(
        self, matches: List[dict], competition_name: str, tournament_id: str
    ) -> List[PartidaResumo]:
        """Converte lista de partidas para modelos."""
        partidas = []
        for match in matches:
            try:
                partida = self._convert_match(match, competition_name, tournament_id)
                partidas.append(partida)
            except Exception:
                continue
        return partidas

    def _convert_match(
        self, match: dict, competition: str, tournament_id: str
    ) -> PartidaResumo:
        """Converte dados brutos da VStats para PartidaResumo."""
        # Extrai data e horario brutos
        local_time_str = match.get("localTime", "00:00:00")
        local_date_str = match.get("localDate", "2000-01-01")
        
        try:
            # Converte para datetime ingênuo (assumido como local da competição)
            dt_nave = datetime.strptime(f"{local_date_str} {local_time_str[:8]}", "%Y-%m-%d %H:%M:%S")
        except Exception:
            # Fallback seguro
            dt_nave = datetime.combine(date.today(), datetime.min.time())

        # Converte para o fuso horário do Brasil
        dt_brazil = self._apply_timezone_conversion(dt_nave, competition)
        
        date_obj = dt_brazil.date()
        time_obj = dt_brazil.time()

        return PartidaResumo(
            id=match.get("id"),
            tournament_id=tournament_id,
            data=date_obj,
            horario=time_obj,
            competicao=self._format_competition_name(competition),
            estadio=match.get("venue", {}).get("name"),
            mandante=TimeInfo(
                id=match.get("homeContestantId"),
                nome=match.get(
                    "homeContestantClubName", match.get("homeContestantName", "")
                ),
                codigo=match.get("homeContestantCode", "---")[:3].upper(),
                escudo=None,
            ),
            visitante=TimeInfo(
                id=match.get("awayContestantId"),
                nome=match.get(
                    "awayContestantClubName", match.get("awayContestantName", "")
                ),
                codigo=match.get("awayContestantCode", "---")[:3].upper(),
                escudo=None,
            ),
        )

    def _apply_timezone_conversion(self, dt: datetime, competition: str) -> datetime:
        """Converte um datetime do fuso local da competição para o fuso brasileiro."""
        # Mapeamento de regiões para fusos horários
        # Default: Europe/London (Premier League, Championship, cups)
        tz_map = {
            "Premier League": "Europe/London",
            "Championship": "Europe/London",
            "League Cup": "Europe/London",
            "FA Cup": "Europe/London",
            "La Liga": "Europe/Madrid",
            "Serie A": "Europe/Rome",
            "Bundesliga": "Europe/Berlin",
            "Ligue 1": "Europe/Paris",
            "Eredivisie": "Europe/Amsterdam",
            "Primeira Liga": "Europe/Lisbon",
            "Brasileirão": "America/Sao_Paulo",
            "Copa do Brasil": "America/Sao_Paulo",
            "Libertadores": "America/Asuncion", # Fallback para CONMEBOL
            "Sudamericana": "America/Asuncion",
        }

        # Tenta encontrar o fuso pelo nome da competição
        source_tz_name = "Europe/London"  # Default seguro para maioria das ligas monitoradas
        for key, tz in tz_map.items():
            if key.lower() in competition.lower():
                source_tz_name = tz
                break
        
        try:
            # Atribui o fuso de origem
            dt_source = dt.replace(tzinfo=ZoneInfo(source_tz_name))
            # Converte para o fuso alvo (Brasil)
            return dt_source.astimezone(ZoneInfo(settings.target_timezone))
        except Exception as e:
            logger.warning(f"Erro na conversão de timezone ({competition}): {str(e)}")
            return dt

    def _format_competition_name(self, name: str) -> str:
        """Formata nome da competicao para exibicao."""
        # Remove ano/temporada do nome se presente (ex: "Premier League 2025/2026" -> "Premier League")
        if "/" in name and name[-4:].isdigit():
            # Remove " 2025/2026" do final
            parts = name.rsplit(" ", 1)
            if len(parts) == 2 and "/" in parts[1]:
                return parts[0]
        return name
