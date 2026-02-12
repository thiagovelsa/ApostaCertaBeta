"""Tests for amostra_suficiente computed field and confidence rounding."""

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


def _build_stats(n: int, nh: int | None = None, na: int | None = None) -> StatsResponse:
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
        data=date(2026, 2, 11),
        horario=time(21, 30, 0),
        competicao="Brazilian Serie A",
        estadio=None,
        mandante=TimeInfo(id="home", nome="Home", codigo="HOM", escudo=None),
        visitante=TimeInfo(id="away", nome="Away", codigo="AWY", escudo=None),
    )

    return StatsResponse(
        partida=partida,
        filtro_aplicado="geral",
        partidas_analisadas=n,
        partidas_analisadas_mandante=nh,
        partidas_analisadas_visitante=na,
        mandante=TimeComEstatisticas(
            id="home",
            nome="Home",
            escudo=None,
            estatisticas=stats_time,
            recent_form=["W", "D"],
        ),
        visitante=TimeComEstatisticas(
            id="away",
            nome="Away",
            escudo=None,
            estatisticas=stats_time,
            recent_form=["D", "L"],
        ),
        arbitro=None,
    )


# --- Fix 2: amostra_suficiente ---

def test_amostra_suficiente_false_when_n_equals_1() -> None:
    stats = _build_stats(n=1, nh=1, na=1)
    assert stats.amostra_suficiente is False


def test_amostra_suficiente_false_when_n_equals_2() -> None:
    stats = _build_stats(n=2, nh=2, na=2)
    assert stats.amostra_suficiente is False


def test_amostra_suficiente_true_when_n_equals_3() -> None:
    stats = _build_stats(n=3, nh=3, na=3)
    assert stats.amostra_suficiente is True


def test_amostra_suficiente_true_when_n_equals_10() -> None:
    stats = _build_stats(n=10, nh=10, na=10)
    assert stats.amostra_suficiente is True


def test_amostra_suficiente_uses_min_of_sides() -> None:
    """If one side has 1 match and another has 10, it should be False."""
    stats = _build_stats(n=5, nh=1, na=10)
    assert stats.amostra_suficiente is False


def test_amostra_suficiente_falls_back_to_partidas_analisadas() -> None:
    """When per-side counts are None, uses partidas_analisadas."""
    stats = _build_stats(n=5, nh=None, na=None)
    assert stats.amostra_suficiente is True


def test_amostra_suficiente_serialized_in_json() -> None:
    stats = _build_stats(n=1, nh=1, na=1)
    payload = stats.model_dump()
    assert "amostra_suficiente" in payload
    assert payload["amostra_suficiente"] is False


# --- Fix 1: confidence rounding ---

def _count_decimal_places(value: float) -> int:
    s = f"{value:.15g}"
    if "." not in s:
        return 0
    return len(s.split(".")[1])


def test_confidence_has_max_3_decimal_places() -> None:
    """Confidence values must not have floating-point artifacts."""
    stats = _build_stats(n=5, nh=5, na=5)
    svc = AnalysisService()
    previsoes = svc.build_previsoes(stats, None, None)

    for stat_name in ("gols", "escanteios", "finalizacoes", "finalizacoes_gol", "cartoes_amarelos", "faltas"):
        prev = getattr(previsoes, stat_name)
        for side in (prev.home, prev.away, prev.total):
            assert _count_decimal_places(side.confianca) <= 3, (
                f"{stat_name}.{side}: confianca={side.confianca} has more than 3 decimal places"
            )
