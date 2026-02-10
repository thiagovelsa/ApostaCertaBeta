from datetime import date, time

from app.services.partidas_service import PartidasService


def test_convert_match_does_not_double_convert_schedule_localtime() -> None:
    """
    Regressao: PartidasService aplicava conversao de timezone em cima do schedule,
    mas a VStats ja retorna localDate/localTime no horario do Brasil.
    """
    svc = PartidasService(vstats_repo=object(), cache=object())  # type: ignore[arg-type]

    match = {
        "id": "match1",
        "localDate": "2026-02-07",
        "localTime": "10:00:00",
        "homeContestantId": "home",
        "homeContestantName": "Home",
        "homeContestantCode": "HOM",
        "awayContestantId": "away",
        "awayContestantName": "Away",
        "awayContestantCode": "AWY",
    }

    partida = svc._convert_match(match, "La Liga", "t1")  # noqa: SLF001 (unit test)

    assert partida.data == date(2026, 2, 7)
    assert partida.horario == time(10, 0, 0)


def test_convert_match_parses_hhmm_time() -> None:
    svc = PartidasService(vstats_repo=object(), cache=object())  # type: ignore[arg-type]

    match = {
        "id": "match2",
        "localDate": "2026-02-07T00:00:00+00:00",
        "localTime": "10:00",
        "homeContestantId": "home",
        "homeContestantName": "Home",
        "homeContestantCode": "HOM",
        "awayContestantId": "away",
        "awayContestantName": "Away",
        "awayContestantCode": "AWY",
    }

    partida = svc._convert_match(match, "La Liga", "t1")  # noqa: SLF001 (unit test)

    assert partida.data == date(2026, 2, 7)
    assert partida.horario == time(10, 0, 0)

