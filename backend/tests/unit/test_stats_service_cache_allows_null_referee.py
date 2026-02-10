from datetime import date, time

import pytest

from app.models import (
    EstatisticaFeitos,
    EstatisticaMetrica,
    EstatisticasTime,
    PartidaResumo,
    StatsResponse,
    TimeComEstatisticas,
    TimeInfo,
)
from app.services.stats_service import StatsService


class DummyVStatsRepo:
    async def fetch_match_stats(self, match_id: str) -> dict:  # pragma: no cover
        raise AssertionError("VStats should not be called when cache hits")


class DummyCache:
    def __init__(self, expected_key: str, payload: dict):
        self.expected_key = expected_key
        self.payload = payload
        self.deleted = False

    def build_key(self, prefix: str, *args) -> str:
        return f"{prefix}|{'|'.join(str(a) for a in args)}"

    async def get(self, key: str):  # noqa: ANN201 (compat with CacheService)
        if key == self.expected_key:
            return self.payload
        return None

    async def set(self, key: str, value, ttl: int = 3600) -> bool:  # noqa: ANN001, ANN201
        raise AssertionError("Cache set should not be called when cache hits")

    async def delete(self, key: str) -> bool:
        self.deleted = True
        return True


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


@pytest.mark.asyncio
async def test_stats_cache_accepts_null_referee() -> None:
    stats_time = EstatisticasTime(
        escanteios=_mk_feitos_sofridos(5.0, 0.25, 4.5, 0.30),
        gols=_mk_feitos_sofridos(1.6, 0.35, 1.2, 0.40),
        finalizacoes=_mk_feitos_sofridos(12.0, 0.20, 11.0, 0.22),
        finalizacoes_gol=_mk_feitos_sofridos(4.2, 0.30, 4.0, 0.33),
        cartoes_amarelos=_mk_metric(2.2, 0.28),
        faltas=_mk_metric(13.0, 0.18),
    )

    partida = PartidaResumo(
        id="match1",
        tournament_id="tourn1",
        data=date(2026, 2, 6),
        horario=time(14, 0, 0),
        competicao="Premier League",
        estadio="X",
        mandante=TimeInfo(id="home", nome="Home", codigo="HOM", escudo=None),
        visitante=TimeInfo(id="away", nome="Away", codigo="AWY", escudo=None),
    )

    stats = StatsResponse(
        partida=partida,
        filtro_aplicado="5",
        partidas_analisadas=5,
        mandante=TimeComEstatisticas(
            id="home",
            nome="Home",
            escudo=None,
            estatisticas=stats_time,
            recent_form=["W", "D", "L", "W", "D"],
        ),
        visitante=TimeComEstatisticas(
            id="away",
            nome="Away",
            escudo=None,
            estatisticas=stats_time,
            recent_form=["D", "L", "W", "D", "L"],
        ),
        arbitro=None,
    )

    cache_payload = stats.model_dump(mode="json")
    cache = DummyCache(
        expected_key="stats|match1|5|integral|all|all",
        payload=cache_payload,
    )

    svc = StatsService(vstats_repo=DummyVStatsRepo(), cache=cache)  # type: ignore[arg-type]
    res = await svc.calcular_stats("match1", "5", "integral", None, None)

    assert res.partida.id == "match1"
    assert res.arbitro is None
    assert cache.deleted is False

