"""Helpers para normalizar payloads VStats em features de contexto (pre-jogo).

Mantemos aqui funcoes puras (sem dependencias de FastAPI/Repos) para facilitar testes unitarios.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional, Tuple


def _parse_date(value: Any) -> Optional[date]:
    if not value:
        return None
    raw = str(value).strip()
    if "T" in raw:
        raw = raw.split("T", 1)[0]
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def extract_ranking_list(standings_data: Any) -> List[Dict[str, Any]]:
    """Extrai uma lista de entradas de ranking de diferentes formatos de standings.

    Formatos observados:
    - {"total": {"ranking": [...]}, ...}
    - {"totalCup": [{"ranking": [...]}], ...}
    - Outros formatos: fazemos busca recursiva por primeira lista "ranking" nao vazia.
    """
    if not isinstance(standings_data, dict):
        return []

    # Formato simples: total.ranking
    total = standings_data.get("total")
    if isinstance(total, dict):
        ranking = total.get("ranking")
        if isinstance(ranking, list) and ranking:
            return [x for x in ranking if isinstance(x, dict)]

    # Formato "Cup": totalCup[0].ranking
    for key in ("totalCup", "homeCup", "awayCup", "firstHalfTotalCup", "firstHalfHomeCup", "fistHalfAwayCup"):
        section = standings_data.get(key)
        if isinstance(section, list) and section:
            first = section[0]
            if isinstance(first, dict):
                ranking = first.get("ranking")
                if isinstance(ranking, list) and ranking:
                    return [x for x in ranking if isinstance(x, dict)]

    # Busca recursiva por qualquer "ranking" nao vazio
    def find(obj: Any) -> Optional[List[Dict[str, Any]]]:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "ranking" and isinstance(v, list) and v:
                    return [x for x in v if isinstance(x, dict)]
                got = find(v)
                if got:
                    return got
        elif isinstance(obj, list):
            for v in obj[:10]:
                got = find(v)
                if got:
                    return got
        return None

    return find(standings_data) or []


def extract_team_table_entry(
    ranking_list: List[Dict[str, Any]],
    team_id: str,
) -> Optional[Dict[str, Any]]:
    if not team_id:
        return None
    for row in ranking_list:
        if row.get("contestantId") == team_id:
            return row
    return None


def extract_stage_name(match_preview: Any) -> Optional[str]:
    if not isinstance(match_preview, dict):
        return None
    match_info = match_preview.get("matchInfo")
    if not isinstance(match_info, dict):
        return None
    stage = match_info.get("stageName")
    if isinstance(stage, str) and stage.strip():
        return stage.strip()
    return None


@dataclass(frozen=True)
class H2HAnyComp:
    total_matches: int
    avg_goals_per_match: float
    home_wins: int
    away_wins: int
    draws: int


def extract_h2h_any_comp(match_preview: Any) -> Optional[H2HAnyComp]:
    if not isinstance(match_preview, dict):
        return None
    pm = match_preview.get("previousMeetingsAnyComp")
    if not isinstance(pm, dict):
        return None

    def _to_int(v: Any) -> int:
        try:
            return int(v)
        except Exception:
            return 0

    home_wins = _to_int(pm.get("homeContestantWins"))
    away_wins = _to_int(pm.get("awayContestantWins"))
    draws = _to_int(pm.get("draws"))
    hg = _to_int(pm.get("homeContestantGoals"))
    ag = _to_int(pm.get("awayContestantGoals"))
    total = max(0, home_wins + away_wins + draws)
    if total <= 0:
        return None
    avg = (hg + ag) / total
    return H2HAnyComp(
        total_matches=total,
        avg_goals_per_match=avg,
        home_wins=home_wins,
        away_wins=away_wins,
        draws=draws,
    )


def compute_rest_context(
    schedule_matches: List[Dict[str, Any]],
    team_id: str,
    match_date: date,
) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """Computa dias de descanso e congestionamento antes de uma partida.

    - dias_descanso: diferenca em dias entre match_date e ultimo jogo "disputado" antes de match_date
    - jogos_7d / jogos_14d: contagem de jogos disputados nos ultimos 7/14 dias antes de match_date
    """
    if not team_id or not schedule_matches or not match_date:
        return (None, None, None)

    played_dates: List[date] = []
    for m in schedule_matches:
        if not isinstance(m, dict):
            continue
        if m.get("homeContestantId") != team_id and m.get("awayContestantId") != team_id:
            continue
        d = _parse_date(m.get("localDate") or m.get("date"))
        if not d or d >= match_date:
            continue

        # "played": preferimos score presente; se score ausente, ainda assim pode ser jogo antigo em algumas ligas.
        hs = m.get("homeScore")
        aas = m.get("awayScore")
        if hs is not None and aas is not None:
            played_dates.append(d)
        else:
            # best-effort: se esta no passado relativo ao match_date, considera.
            played_dates.append(d)

    if not played_dates:
        return (None, None, None)

    played_dates.sort(reverse=True)
    last = played_dates[0]
    dias_descanso = max(0, (match_date - last).days)

    def count_window(days: int) -> int:
        start = match_date.toordinal() - days
        return sum(1 for d in played_dates if start <= d.toordinal() < match_date.toordinal())

    jogos_7d = count_window(7)
    jogos_14d = count_window(14)
    return (dias_descanso, jogos_7d, jogos_14d)

