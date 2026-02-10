from datetime import date, time

from app.models import (
    EstatisticaFeitos,
    EstatisticaMetrica,
    EstatisticasTime,
    PartidaResumo,
    StatsResponse,
    TimeComEstatisticas,
    TimeInfo,
)
from app.services.analysis_service import AnalysisService


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


def _mk_stats_response(n: int) -> StatsResponse:
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

    return StatsResponse(
        partida=partida,
        filtro_aplicado="5",
        partidas_analisadas=n,
        mandante=TimeComEstatisticas(
            id="home",
            nome="Home",
            escudo=None,
            estatisticas=stats_time,
            recent_form=["W"],
        ),
        visitante=TimeComEstatisticas(
            id="away",
            nome="Away",
            escudo=None,
            estatisticas=stats_time,
            recent_form=["D"],
        ),
        arbitro=None,
    )


def test_over_under_interval_grows_when_sample_is_smaller() -> None:
    svc = AnalysisService()

    stats_small = _mk_stats_response(1)
    previsoes_small = svc.build_previsoes(stats_small, None, None)
    ou_small = svc.build_over_under(stats_small, previsoes_small, None, None)

    stats_big = _mk_stats_response(10)
    previsoes_big = svc.build_previsoes(stats_big, None, None)
    ou_big = svc.build_over_under(stats_big, previsoes_big, None, None)

    width_small = ou_small.gols.predMax - ou_small.gols.predMin
    width_big = ou_big.gols.predMax - ou_big.gols.predMin

    assert width_small > width_big

