from datetime import date, timedelta

import pytest

from app.services.stats_service import StatsService


@pytest.mark.asyncio
async def test_recent_matches_filtering_requires_valid_date_and_score() -> None:
    team_id = "T1"
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    three_days_ago = (date.today() - timedelta(days=3)).isoformat()

    schedule = {
        "matches": [
            # Included (today, has score)
            {
                "id": "M_TODAY_HOME",
                "localDate": today,
                "homeContestantId": team_id,
                "awayContestantId": "X",
                "homeScore": 2,
                "awayScore": 2,
            },
            # Included (yesterday, has score)
            {
                "id": "M_YEST_HOME",
                "localDate": yesterday,
                "homeContestantId": team_id,
                "awayContestantId": "X",
                "homeScore": 1,
                "awayScore": 0,
            },
            # Excluded (past date, but missing score => postponed/unknown)
            {
                "id": "M_NO_SCORE",
                "localDate": yesterday,
                "homeContestantId": "X",
                "awayContestantId": team_id,
            },
            # Included (away, has score)
            {
                "id": "M_AWAY",
                "localDate": three_days_ago,
                "homeContestantId": "X",
                "awayContestantId": team_id,
                "homeScore": 1,
                "awayScore": 3,
            },
            # Excluded (invalid date)
            {
                "id": "M_BAD_DATE",
                "localDate": "",
                "homeContestantId": team_id,
                "awayContestantId": "X",
                "homeScore": 9,
                "awayScore": 9,
            },
            # Excluded (other team)
            {
                "id": "M_OTHER_TEAM",
                "localDate": yesterday,
                "homeContestantId": "A",
                "awayContestantId": "B",
                "homeScore": 1,
                "awayScore": 1,
            },
        ]
    }

    service = StatsService.__new__(StatsService)

    out = await StatsService._get_recent_matches_with_form(  # type: ignore[misc]
        service,
        tournament_id="T",
        team_id=team_id,
        limit=10,
        mando=None,
        schedule=schedule,
    )
    assert out["match_ids"] == ["M_TODAY_HOME", "M_YEST_HOME", "M_AWAY"]

    out_home = await StatsService._get_recent_matches_with_form(  # type: ignore[misc]
        service,
        tournament_id="T",
        team_id=team_id,
        limit=10,
        mando="casa",
        schedule=schedule,
    )
    assert out_home["match_ids"] == ["M_TODAY_HOME", "M_YEST_HOME"]

    out_away = await StatsService._get_recent_matches_with_form(  # type: ignore[misc]
        service,
        tournament_id="T",
        team_id=team_id,
        limit=10,
        mando="fora",
        schedule=schedule,
    )
    assert out_away["match_ids"] == ["M_AWAY"]
