from __future__ import annotations

from datetime import date, time

import pytest

from app.api.routes.stats import get_analysis
from app.models.analysis import (
    OverUnderLine,
    OverUnderPartida,
    OverUnderStat,
    PrevisaoEstatistica,
    PrevisaoPartida,
    PrevisaoValor,
)
from app.models.estatisticas import (
    EstatisticaFeitos,
    EstatisticaMetrica,
    EstatisticasTime,
    StatsResponse,
    TimeComEstatisticas,
)
from app.models.partida import PartidaResumo, TimeInfo
from app.services.analysis_service import AnalysisService


def _m() -> EstatisticaMetrica:
    return EstatisticaMetrica(
        media=1.0,
        cv=0.25,
        classificacao="Estável",
        estabilidade=70,
    )


def _fs() -> EstatisticaFeitos:
    return EstatisticaFeitos(feitos=_m(), sofridos=_m())


def _time_stats() -> EstatisticasTime:
    return EstatisticasTime(
        escanteios=_fs(),
        gols=_fs(),
        finalizacoes=_fs(),
        finalizacoes_gol=_fs(),
        cartoes_amarelos=_m(),
        faltas=_m(),
    )


def _stats_response() -> StatsResponse:
    partida = PartidaResumo(
        id="match_test",
        tournament_id="t1",
        data=date(2026, 2, 8),
        horario=time(20, 0, 0),
        competicao="Liga Teste",
        estadio="Estadio Teste",
        mandante=TimeInfo(id="home", nome="Home FC", codigo="HOM"),
        visitante=TimeInfo(id="away", nome="Away FC", codigo="AWY"),
    )

    mandante = TimeComEstatisticas(
        id="home",
        nome="Home FC",
        escudo=None,
        estatisticas=_time_stats(),
        recent_form=["W", "D", "L", "W", "W"],
    )
    visitante = TimeComEstatisticas(
        id="away",
        nome="Away FC",
        escudo=None,
        estatisticas=_time_stats(),
        recent_form=["D", "L", "W", "D", "L"],
    )

    return StatsResponse(
        partida=partida,
        filtro_aplicado="10",
        partidas_analisadas=10,
        partidas_analisadas_mandante=10,
        partidas_analisadas_visitante=10,
        mandante=mandante,
        visitante=visitante,
        arbitro=None,
        contexto=None,
        h2h_all_comps=None,
    )


def _pvalor() -> PrevisaoValor:
    return PrevisaoValor(valor=1.0, confianca=0.6, confiancaLabel="Média")


def _pstat() -> PrevisaoEstatistica:
    v = _pvalor()
    return PrevisaoEstatistica(home=v, away=v, total=v)


def _previsoes() -> PrevisaoPartida:
    s = _pstat()
    return PrevisaoPartida(
        gols=s,
        escanteios=s,
        finalizacoes=s,
        finalizacoes_gol=s,
        cartoes_amarelos=s,
        faltas=s,
    )


def _oust(label: str, icon: str) -> OverUnderStat:
    return OverUnderStat(
        label=label,
        icon=icon,
        lambda_=2.0,
        lambdaHome=1.0,
        lambdaAway=1.0,
        predMin=1.0,
        predMax=3.0,
        distribution="poisson",
        lines=[OverUnderLine(line=2.5, over=0.5, under=0.5)],
        confidence=0.6,
        confidenceLabel="Média",
    )


def _over_under() -> OverUnderPartida:
    return OverUnderPartida(
        gols=_oust("Gols", "ball"),
        escanteios=_oust("Escanteios", "corner"),
        finalizacoes=_oust("Chutes", "zap"),
        finalizacoes_gol=_oust("Chutes ao Gol", "target"),
        cartoes_amarelos=_oust("Cartões Amarelos", "card"),
        faltas=_oust("Faltas", "whistle"),
    )


class _FakeStatsService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str, str | None, str | None]] = []

    async def calcular_stats(
        self,
        match_id: str,
        filtro: str,
        periodo: str,
        home_mando: str | None,
        away_mando: str | None,
    ) -> StatsResponse:
        self.calls.append((match_id, filtro, periodo, home_mando, away_mando))
        return _stats_response()


@pytest.mark.asyncio
async def test_analysis_omitting_mando_params_passes_none_none(monkeypatch: pytest.MonkeyPatch) -> None:
    svc = _FakeStatsService()

    monkeypatch.setattr(AnalysisService, "build_previsoes", lambda self, stats, home, away: _previsoes())
    monkeypatch.setattr(AnalysisService, "build_over_under", lambda self, stats, prev, home, away: _over_under())

    # When calling the route handler directly (unit test), explicitly pass None to avoid FastAPI's Query(...) defaults.
    await get_analysis(
        match_id="match_test",
        filtro="10",
        periodo="integral",
        home_mando=None,
        away_mando=None,
        service=svc,
    )

    assert len(svc.calls) == 1
    _, _, _, home_mando, away_mando = svc.calls[0]
    assert home_mando is None
    assert away_mando is None


@pytest.mark.asyncio
async def test_analysis_with_same_mando_params_single_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    svc = _FakeStatsService()

    monkeypatch.setattr(AnalysisService, "build_previsoes", lambda self, stats, home, away: _previsoes())
    monkeypatch.setattr(AnalysisService, "build_over_under", lambda self, stats, prev, home, away: _over_under())

    await get_analysis(
        match_id="match_test",
        filtro="10",
        periodo="integral",
        home_mando="casa",
        away_mando="casa",
        service=svc,
    )

    assert len(svc.calls) == 1
    _, _, _, home_mando, away_mando = svc.calls[0]
    assert home_mando == "casa"
    assert away_mando == "casa"


@pytest.mark.asyncio
async def test_analysis_with_split_mando_fetches_sides_separately(monkeypatch: pytest.MonkeyPatch) -> None:
    svc = _FakeStatsService()

    monkeypatch.setattr(AnalysisService, "build_previsoes", lambda self, stats, home, away: _previsoes())
    monkeypatch.setattr(AnalysisService, "build_over_under", lambda self, stats, prev, home, away: _over_under())

    await get_analysis(
        match_id="match_test",
        filtro="10",
        periodo="integral",
        home_mando="fora",
        away_mando="casa",
        service=svc,
    )

    assert len(svc.calls) == 2
    assert svc.calls[0][3:] == ("fora", None)
    assert svc.calls[1][3:] == (None, "casa")
