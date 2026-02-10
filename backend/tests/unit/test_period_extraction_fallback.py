from app.services.stats_service import StatsService


def test_periodo_arrays_missing_fallbacks_to_integral_and_marks_flag() -> None:
    match_data = {
        "stats": {
            # Only full-time values (2 slots), no halves.
            "attempts": [10, 8],
            "attemptsOnGoal": [4, 3],
            "corners": [6, 5],
            "yellowCards": [2, 1],
            "redCards": [0, 0],
            "fouls": [12, 14],
            "saves": [3, 2],
            "goals": [2, 1],
        },
        "homeId": "HOME",
        "awayId": "AWAY",
        "homeScore": 2,
        "awayScore": 1,
    }

    service = StatsService.__new__(StatsService)
    out = StatsService._extract_team_match_stats(service, match_data, "HOME", "1T")  # type: ignore[misc]
    assert out is not None

    # Should not drop to zeros just because 1T indices are missing.
    assert out["totalScoringAtt"] == 10.0
    assert out["totalShotsConceded"] == 8.0
    assert out["wonCorners"] == 6.0
    assert out["lostCorners"] == 5.0
    assert out.get("_period_fallback") is True

