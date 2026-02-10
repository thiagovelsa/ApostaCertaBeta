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


def test_build_previsoes_does_not_require_h2h_all_comps() -> None:
    """
    Regressao: /analysis explodia com AttributeError porque StatsResponse
    nao tem campo h2h_all_comps, mas o AnalysisService acessava direto.
    """

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

    svc = AnalysisService()
    previsoes = svc.build_previsoes(stats, None, None)

    assert previsoes.gols.total.valor > 0

