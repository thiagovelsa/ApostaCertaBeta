import pytest

from app.models import (
    ContextoPartida,
    ContextoTime,
    EstatisticaFeitos,
    EstatisticaMetrica,
    EstatisticasTime,
)
from app.services.stats_service import StatsService


class DummyCache:
    def __init__(self):
        self.store: dict[str, object] = {}

    def build_key(self, prefix: str, *args) -> str:
        return f"{prefix}|{'|'.join(str(a) for a in args)}"

    async def get(self, key: str):  # noqa: ANN201 (compat with CacheService)
        return self.store.get(key)

    async def set(self, key: str, value, ttl: int = 3600) -> bool:  # noqa: ANN001, ANN201
        self.store[key] = value
        return True

    async def delete(self, key: str) -> bool:
        self.store.pop(key, None)
        return True


class DummyVStatsRepo:  # pragma: no cover
    pass


def _mk_metric(media: float, cv: float) -> EstatisticaMetrica:
    return EstatisticaMetrica(
        media=media,
        cv=cv,
        classificacao="Estável",
        estabilidade=70,
    )


def _mk_feitos_sofridos(
    feitos_media: float,
    feitos_cv: float,
    sofridos_media: float,
    sofridos_cv: float,
) -> EstatisticaFeitos:
    return EstatisticaFeitos(
        feitos=_mk_metric(feitos_media, feitos_cv),
        sofridos=_mk_metric(sofridos_media, sofridos_cv),
    )


class DummyStatsService(StatsService):
    async def _fetch_tournament_schedule(self, tournament_id: str) -> dict:  # noqa: SLF001
        return {}

    async def _get_referee_info(self, match_id: str, referee_id=None):  # noqa: ANN001, SLF001
        return None

    async def _fetch_match_preview_cached(self, match_id: str):  # noqa: SLF001, ANN201
        return None

    async def _fetch_standings_cached(self, tournament_id: str):  # noqa: SLF001, ANN201
        return None

    def _build_contexto(self, **kwargs):  # noqa: ANN003, SLF001, ANN201
        return ContextoPartida(mandante=ContextoTime(), visitante=ContextoTime())

    async def _get_recent_matches_with_form(  # noqa: SLF001
        self,
        tournament_id: str,
        team_id: str,
        limit: int,
        mando,
        schedule,
    ) -> dict:
        # Força fallback: sem partidas individuais
        return {"match_ids": [], "match_dates": []}

    async def _get_season_stats(self, tournament_id: str, team_id: str) -> dict:  # noqa: SLF001
        stats_time = EstatisticasTime(
            escanteios=_mk_feitos_sofridos(5.0, 0.25, 4.5, 0.30),
            gols=_mk_feitos_sofridos(1.6, 0.35, 1.2, 0.40),
            finalizacoes=_mk_feitos_sofridos(12.0, 0.20, 11.0, 0.22),
            finalizacoes_gol=_mk_feitos_sofridos(4.2, 0.30, 4.0, 0.33),
            cartoes_amarelos=_mk_metric(2.2, 0.28),
            faltas=_mk_metric(13.0, 0.18),
        )
        return {
            "estatisticas": stats_time,
            "matches": 20,
            "_seasonstats_fallback": True,
        }


@pytest.mark.asyncio
async def test_seasonstats_fallback_adds_context_flag() -> None:
    cache = DummyCache()
    match_id = "match1"

    # match_meta para evitar chamadas externas
    cache.store[cache.build_key("match_meta", match_id)] = {
        "tournament_id": "t1",
        "home_id": "home",
        "home_name": "Home FC",
        "away_id": "away",
        "away_name": "Away FC",
        "competicao": "La Liga",
        "data": "2026-02-07",
        "horario": "10:00:00",
        "referee_id": None,
    }

    svc = DummyStatsService(vstats_repo=DummyVStatsRepo(), cache=cache)  # type: ignore[arg-type]
    res = await svc.calcular_stats(match_id, "5", "integral", None, None)

    assert res.contexto is not None
    assert "seasonstats_fallback" in res.contexto.ajustes_aplicados

