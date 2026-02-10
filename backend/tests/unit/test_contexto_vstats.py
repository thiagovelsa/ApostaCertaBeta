from datetime import date

from app.utils.contexto_vstats import (
    compute_rest_context,
    extract_h2h_any_comp,
    extract_ranking_list,
    extract_team_table_entry,
)


def test_extract_ranking_list_handles_totalcup_format() -> None:
    standings = {
        "totalCup": [
            {
                "ranking": [
                    {"contestantId": "t1", "rank": 1, "points": 10, "matchesPlayed": 5},
                    {"contestantId": "t2", "rank": 2, "points": 8, "matchesPlayed": 5},
                ]
            }
        ]
    }

    ranking = extract_ranking_list(standings)
    assert len(ranking) == 2
    assert extract_team_table_entry(ranking, "t2")["rank"] == 2


def test_extract_h2h_any_comp_from_preview() -> None:
    preview = {
        "previousMeetingsAnyComp": {
            "homeContestantWins": 3,
            "awayContestantWins": 2,
            "draws": 1,
            "homeContestantGoals": 10,
            "awayContestantGoals": 8,
        }
    }

    h2h = extract_h2h_any_comp(preview)
    assert h2h is not None
    assert h2h.total_matches == 6
    assert abs(h2h.avg_goals_per_match - (18 / 6)) < 1e-9


def test_compute_rest_context_counts_windows_and_rest_days() -> None:
    match_date = date(2026, 2, 10)
    schedule = [
        {"id": "m1", "localDate": "2026-02-01", "homeContestantId": "A", "awayContestantId": "B", "homeScore": 1, "awayScore": 0},
        {"id": "m2", "localDate": "2026-02-04", "homeContestantId": "C", "awayContestantId": "A", "homeScore": 0, "awayScore": 0},
        {"id": "m3", "localDate": "2026-02-08", "homeContestantId": "A", "awayContestantId": "D", "homeScore": 2, "awayScore": 2},
        {"id": "m4", "localDate": "2026-02-12", "homeContestantId": "A", "awayContestantId": "E", "homeScore": None, "awayScore": None},
    ]

    dias, jogos_7d, jogos_14d = compute_rest_context(schedule, "A", match_date)
    assert dias == 2  # 2026-02-10 - 2026-02-08
    assert jogos_7d == 2  # 02-04 and 02-08
    assert jogos_14d == 3  # 02-01, 02-04, 02-08

