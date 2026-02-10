from app.services.stats_service import StatsService


def _extract_for_period(periodo: str) -> dict:
    # Minimal VStats payload shape for matchstats/get-match-stats:
    # liveData.lineUp[].stat[] includes value + halves fh/sh.
    match_data = {
        "matchInfo": {},
        "liveData": {
            "lineUp": [
                {
                    "contestantId": "HOME",
                    "stat": [
                        {"type": "goals", "value": "3", "fh": "1", "sh": "2"},
                        {"type": "wonCorners", "value": "10", "fh": "4", "sh": "6"},
                        {"type": "totalScoringAtt", "value": "20", "fh": "7", "sh": "13"},
                    ],
                },
                {
                    "contestantId": "AWAY",
                    "stat": [
                        {"type": "goals", "value": "1", "fh": "0", "sh": "1"},
                        {"type": "totalScoringAtt", "value": "5", "fh": "2", "sh": "3"},
                    ],
                },
            ]
        },
    }

    # Bypass __init__ (avoids wiring vstats/cache dependencies); we only need the pure extractor.
    service = StatsService.__new__(StatsService)
    out = StatsService._extract_team_match_stats(service, match_data, "HOME", periodo)  # type: ignore[misc]
    assert out is not None
    return out


def test_periodo_integral_uses_full_value() -> None:
    out = _extract_for_period("integral")
    assert out["goals"] == 3.0
    assert out["wonCorners"] == 10.0
    assert out["totalScoringAtt"] == 20.0


def test_periodo_1t_uses_fh() -> None:
    out = _extract_for_period("1T")
    assert out["goals"] == 1.0
    assert out["wonCorners"] == 4.0
    assert out["totalScoringAtt"] == 7.0


def test_periodo_2t_uses_sh() -> None:
    out = _extract_for_period("2T")
    assert out["goals"] == 2.0
    assert out["wonCorners"] == 6.0
    assert out["totalScoringAtt"] == 13.0
