"""
Partidas Service
================

Logica de negocio para busca e listagem de partidas.
"""

import asyncio
import logging
from datetime import date, datetime
from typing import List, Optional, Tuple

from ..config import settings

logger = logging.getLogger(__name__)
from ..models import PartidaResumo, PartidaListResponse, TimeInfo
from ..repositories import VStatsRepository
from .cache_service import CacheService


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

        # Busca lista de competicoes dinamicamente via /calendar
        try:
            competitions = await self.vstats.fetch_calendar()
            logger.info(f"[CALENDAR] Encontradas {len(competitions)} competicoes no calendario")
        except Exception as e:
            logger.error(f"[ERROR] Erro ao buscar calendario: {str(e)}")
            competitions = []

        # Busca partidas de todas as competicoes EM PARALELO
        logger.info(f"[SEARCH] Buscando partidas para {target_date.isoformat()} em {len(competitions)} competicoes...")

        # Cria tasks para buscar todas as competicoes em paralelo
        async def fetch_safe(comp: dict) -> Tuple[str, List[PartidaResumo]]:
            """Wrapper seguro que retorna lista vazia em caso de erro."""
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

        # Executa todas as buscas em paralelo
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
        """Busca partidas de uma competicao especifica."""
        # Busca calendario do mes
        # Nota: parametros month/year sao IGNORADOS pela API VStats
        schedule_data = await self.vstats.fetch_schedule_month(tournament_id)

        # Estrutura da resposta: {"matches": [...]}
        # Cada match tem campo "localDate" no formato "YYYY-MM-DD"
        all_matches = schedule_data.get("matches", [])
        target_str = target_date.isoformat()

        # Filtra partidas pela data alvo
        filtered = [m for m in all_matches if m.get("localDate") == target_str]

        # Converte para modelos
        partidas = []
        for match in filtered:
            try:
                partida = self._convert_match(match, competition_name, tournament_id)
                partidas.append(partida)
            except Exception:
                continue

        return partidas

    def _convert_match(self, match: dict, competition: str, tournament_id: str) -> PartidaResumo:
        """Converte dados brutos da VStats para PartidaResumo."""
        # Extrai horario
        local_time = match.get("localTime", "00:00:00")
        if isinstance(local_time, str):
            time_obj = datetime.strptime(local_time[:8], "%H:%M:%S").time()
        else:
            time_obj = local_time

        # Extrai data
        local_date = match.get("localDate")
        if isinstance(local_date, str):
            date_obj = datetime.strptime(local_date, "%Y-%m-%d").date()
        else:
            date_obj = local_date

        return PartidaResumo(
            id=match.get("id"),
            tournament_id=tournament_id,
            data=date_obj,
            horario=time_obj,
            competicao=self._format_competition_name(competition),
            estadio=match.get("venue", {}).get("name"),
            mandante=TimeInfo(
                id=match.get("homeContestantId"),
                nome=match.get("homeContestantClubName", match.get("homeContestantName", "")),
                codigo=match.get("homeContestantCode", "---")[:3].upper(),
                escudo=None,
            ),
            visitante=TimeInfo(
                id=match.get("awayContestantId"),
                nome=match.get("awayContestantClubName", match.get("awayContestantName", "")),
                codigo=match.get("awayContestantCode", "---")[:3].upper(),
                escudo=None,
            ),
        )

    def _format_competition_name(self, name: str) -> str:
        """Formata nome da competicao para exibicao."""
        # Remove ano/temporada do nome se presente (ex: "Premier League 2025/2026" -> "Premier League")
        if "/" in name and name[-4:].isdigit():
            # Remove " 2025/2026" do final
            parts = name.rsplit(" ", 1)
            if len(parts) == 2 and "/" in parts[1]:
                return parts[0]
        return name
