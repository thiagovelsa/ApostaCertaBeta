"""
VStats Repository
=================

Cliente para a API VStats (estatisticas de futebol).
"""

import logging
from datetime import date
from typing import Any, Dict, List, Optional

import httpx

from ..config import settings

# Configura logger
logger = logging.getLogger(__name__)


class VStatsAPIError(Exception):
    """Erro ao comunicar com a API VStats."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class VStatsRepository:
    """Cliente HTTP para a API VStats."""

    def __init__(self):
        self.base_url = settings.vstats_api_url
        self.timeout = settings.vstats_api_timeout
        # Cliente compartilhado para connection pooling (lazy initialization)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Retorna cliente HTTP compartilhado (lazy init com connection pooling)."""
        if self._client is None or self._client.is_closed:
            # Configura limits para requests paralelos (20 conexões simultâneas)
            limits = httpx.Limits(
                max_connections=20,
                max_keepalive_connections=10,
                keepalive_expiry=30.0,
            )
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=limits,
                http2=True,  # HTTP/2 para multiplexação de requests
            )
        return self._client

    async def close(self) -> None:
        """Fecha o cliente HTTP (chamar ao encerrar aplicação)."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """
        Faz requisicao GET para a API VStats.

        Args:
            endpoint: Caminho do endpoint (ex: /stats/tournament/v1/schedule/month)
            params: Parametros da query string

        Returns:
            Resposta JSON parseada

        Raises:
            VStatsAPIError: Se a requisicao falhar
        """
        url = f"{self.base_url}{endpoint}"

        # Log da requisicao
        logger.info(f"[VSTATS] GET {endpoint} | params={params}")

        client = await self._get_client()
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            logger.info(f"[VSTATS OK] {response.status_code}")
            return data
        except httpx.TimeoutException:
            logger.error(f"[VSTATS TIMEOUT] {endpoint}")
            raise VStatsAPIError("Timeout ao conectar com VStats API")
        except httpx.HTTPStatusError as e:
            logger.error(f"[VSTATS HTTP] {e.response.status_code} em {endpoint}")
            raise VStatsAPIError(
                f"Erro HTTP {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            logger.error(f"[VSTATS ERROR] Erro de conexao em {endpoint}: {str(e)}")
            raise VStatsAPIError(f"Erro de conexao: {str(e)}")

    async def fetch_calendar(self) -> List[Dict]:
        """
        Busca TODAS as competicoes disponiveis na API.

        Este endpoint retorna dinamicamente todos os torneios ativos
        com seus IDs atualizados (nao precisa hardcodar IDs).

        Returns:
            Lista de competicoes com estrutura normalizada:
            [
                {
                    "id": "51r6ph2woavlbbpk8f29nynf8",
                    "name": "Premier League",
                    "country": "England"
                },
                ...
            ]
        """
        data = await self._get("/stats/tournament/v1/calendar")

        # Normaliza a estrutura para uso consistente
        competitions = []
        raw_list = data if isinstance(data, list) else data.get("tournaments", [])

        for comp in raw_list:
            competitions.append(
                {
                    "id": comp.get("tournamentCalendarId"),
                    "name": comp.get("knownName")
                    or comp.get("translatedName")
                    or comp.get("name"),
                    "country": comp.get("country"),
                }
            )

        # Log detalhado para debug
        logger.info(f"[CALENDAR] Normalizadas {len(competitions)} competicoes da API")
        for comp in competitions[:5]:  # Log primeiras 5
            logger.debug(f"  - {comp['id'][:12]}... | {comp['name']} ({comp.get('country', 'N/A')})")

        return competitions

    async def fetch_schedule_day(self, tournament_id: str, target_date: str) -> Dict:
        """
        Busca partidas de uma data especifica.

        Este e o endpoint CORRETO para buscar partidas por data.
        Conforme documentacao: /schedule/day?tmcl={id}&date={YYYY-MM-DD}

        Args:
            tournament_id: ID da competicao
            target_date: Data no formato YYYY-MM-DD

        Returns:
            Dados com partidas da data:
            {
                "matches": [
                    {
                        "id": "...",
                        "localDate": "YYYY-MM-DD",
                        ...
                    }
                ]
            }
        """
        params = {"tmcl": tournament_id, "date": target_date}
        return await self._get("/stats/tournament/v1/schedule/day", params)

    async def fetch_schedule_month(self, tournament_id: str) -> Dict:
        """
        Busca calendario de partidas do mes ATUAL.

        ATENCAO: A API VStats IGNORA parametros month/year.
        O endpoint sempre retorna o mes atual.
        Para datas especificas, filtre client-side.

        Args:
            tournament_id: ID da competicao

        Returns:
            Dados do calendario com estrutura:
            {
                "matchDate": [
                    {
                        "date": "YYYY-MM-DD",
                        "match": [...]
                    }
                ]
            }
        """
        # Nota: parametro é Tmcl (T maiusculo) para schedule/month!
        params = {"Tmcl": tournament_id}
        return await self._get("/stats/tournament/v1/schedule/month", params)

    async def fetch_schedule_week(self, tournament_id: str) -> Dict:
        """
        Busca calendario de partidas da SEMANA ATUAL.

        Retorna apenas ~20-30 partidas (muito mais eficiente que /schedule).
        Ideal para buscar partidas do dia atual ou próximos dias.

        Args:
            tournament_id: ID da competicao

        Returns:
            Dados do calendario: {"matches": [...]}
        """
        params = {"tmcl": tournament_id}
        return await self._get("/stats/tournament/v1/schedule/week", params)

    async def fetch_schedule_full(self, tournament_id: str) -> Dict:
        """
        Busca calendario COMPLETO da temporada (todas as partidas).

        DESCOBERTA (25/12/2025): O endpoint /schedule SEM sufixo
        retorna TODA a temporada (~380 jogos), diferente de /schedule/month
        que retorna apenas o mes atual (~16 jogos).

        Args:
            tournament_id: ID da competicao

        Returns:
            Dados do calendario com todas as partidas:
            {
                "matches": [
                    {
                        "id": "...",
                        "localDate": "YYYY-MM-DD",
                        "homeContestantId": "...",
                        "awayContestantId": "...",
                        "homeScore": 2,  # null se nao realizada
                        "awayScore": 1,
                        ...
                    }
                ]
            }
        """
        # Nota: parametro é tmcl (minusculo) para /schedule!
        params = {"tmcl": tournament_id}
        return await self._get("/stats/tournament/v1/schedule", params)

    async def fetch_seasonstats(
        self,
        tournament_id: str,
        team_id: str,
        detailed: bool = True,
    ) -> Dict:
        """
        Busca estatisticas agregadas da temporada para um time.

        Args:
            tournament_id: ID da competicao
            team_id: ID do time
            detailed: Se True, retorna estatisticas detalhadas

        Returns:
            Estatisticas da temporada
        """
        params = {
            "tmcl": tournament_id,
            "ctst": team_id,
            "detailed": "yes" if detailed else "no",
        }

        return await self._get("/stats/seasonstats/v1/team", params)

    async def fetch_match_stats(self, match_id: str) -> Dict:
        """
        Busca estatisticas detalhadas de uma partida especifica.

        Args:
            match_id: ID da partida

        Returns:
            Estatisticas da partida
        """
        params = {"Fx": match_id}
        return await self._get("/stats/matchstats/v1/get-match-stats", params)

    async def fetch_game_played_stats(self, match_id: str) -> Dict:
        """
        Busca estatisticas detalhadas de uma partida JA REALIZADA (por time).

        Args:
            match_id: ID da partida

        Returns:
            Estatisticas agregadas por time da partida
        """
        params = {"Fx": match_id}
        return await self._get("/stats/matchstats/v1/get-game-played-stats", params)

    async def fetch_match_preview(self, match_id: str) -> Dict:
        """
        Busca preview de uma partida (head-to-head, forma recente).

        Args:
            match_id: ID da partida

        Returns:
            Dados do preview
        """
        # Validado em runtime (Fase 0 - 2026-02-07): este endpoint retorna 200 para partidas futuras.
        # O endpoint alternativo /stats/matchstats/v1/match-preview retornou 404.
        params = {"Fx": match_id}
        return await self._get("/stats/matchpreview/v1/get-match-preview", params)

    async def fetch_standings(self, tournament_id: str, detailed: bool = False) -> Dict:
        """
        Busca classificacao (standings) da competicao.

        Args:
            tournament_id: ID da competicao (tournamentCalendarId)
            detailed: Se True, tenta incluir campos extras (quando suportado)

        Returns:
            JSON com standings (formatos variam por competicao: total, totalCup, etc.)
        """
        params = {
            "tmcl": tournament_id,
            "detailed": "true" if detailed else "false",
        }
        return await self._get("/stats/standings/v1/standings", params)

    async def fetch_referee_stats(self, referee_id: str) -> Dict:
        """
        Busca estatisticas de um arbitro especifico.

        Args:
            referee_id: ID do arbitro (Person ID)

        Returns:
            Estatisticas do arbitro incluindo media de cartoes
        """
        params = {"Prsn": referee_id}
        return await self._get("/stats/referees/v1/get-by-prsn", params)

    def filter_matches_by_date(
        self,
        matches: List[Dict],
        target_date: date,
    ) -> List[Dict]:
        """
        Filtra partidas por data especifica.

        A API VStats nao suporta filtro por data diretamente,
        entao filtramos no lado do cliente.

        Args:
            matches: Lista de partidas do calendario
            target_date: Data alvo

        Returns:
            Partidas da data especificada
        """
        target_str = target_date.isoformat()

        return [match for match in matches if match.get("localDate") == target_str]

    def extract_team_stats(
        self,
        seasonstats_data: Dict,
    ) -> Dict[str, float]:
        """
        Extrai estatisticas relevantes do seasonstats.

        Args:
            seasonstats_data: Resposta do endpoint seasonstats

        Returns:
            Dicionario com estatisticas
        """
        stats = seasonstats_data.get("data", {}).get("statistics")
        if stats:
            return {
                "goals": stats.get("goals", 0),
                "goalsConceded": stats.get("goalsConceded", 0),
                "wonCorners": stats.get("wonCorners", 0),
                "lostCorners": stats.get("lostCorners", 0),
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
                "matchesPlayed": seasonstats_data.get("data", {}).get(
                    "matchesPlayed", 0
                ),
            }

        stat_list = seasonstats_data.get("stat", [])
        stats_by_name = {
            stat.get("name"): stat
            for stat in stat_list
            if isinstance(stat, dict) and stat.get("name")
        }

        def get_value(names, default=0.0) -> float:
            for name in names:
                stat = stats_by_name.get(name)
                if not stat:
                    continue
                raw_value = stat.get("value")
                try:
                    return float(raw_value)
                except (TypeError, ValueError):
                    continue
            return default

        def get_average(names, default=0.0) -> float:
            for name in names:
                stat = stats_by_name.get(name)
                if not stat:
                    continue
                raw_value = stat.get("average")
                try:
                    return float(raw_value)
                except (TypeError, ValueError):
                    continue
            return default

        def sum_values(names) -> float:
            return sum(get_value([name], 0.0) for name in names)

        total_red_cards = get_value(["Red Cards", "Total Red Cards"], 0.0)
        if total_red_cards == 0.0:
            total_red_cards = sum_values(
                ["Straight Red Cards", "Red Card - 2nd Yellow"]
            )

        matches_played = seasonstats_data.get("data", {}).get("matchesPlayed")
        if not matches_played:
            for name in ["Goals", "Total Shots", "Yellow Cards"]:
                total = get_value([name], 0.0)
                avg = get_average([name], 0.0)
                if avg:
                    matches_played = round(total / avg)
                    break
        if not matches_played:
            matches_played = 0

        return {
            "goals": get_value(["Goals"], 0),
            "goalsConceded": get_value(["Goals Conceded"], 0),
            "wonCorners": get_value(
                ["Corners Won", "Corners Taken (incl short corners)"],
                0,
            ),
            "lostCorners": 0,
            "totalScoringAtt": get_value(["Total Shots"], 0),
            "totalShotsConceded": get_value(["Total Shots Conceded"], 0),
            "ontargetScoringAtt": get_value(
                ["Shots On Target ( inc goals )", "Shots On Target"],
                0,
            ),
            "ontargetScoringAttConceded": sum_values(
                ["Shots On Conceded Inside Box", "Shots On Conceded Outside Box"]
            ),
            "totalYellowCard": get_value(["Yellow Cards"], 0),
            "totalRedCard": total_red_cards,
            "fkFoulLost": get_value(["Total Fouls Conceded"], 0),
            "saves": get_value(["Saves"], 0),
            "matchesPlayed": matches_played,
        }
