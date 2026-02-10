from datetime import date, timedelta

import pytest

from app.services.stats_service import StatsService


@pytest.mark.asyncio
async def test_recent_matches_filtering_falls_back_to_date_when_schedule_has_no_scores() -> None:
    team_id = "T1"
    today = date.today()
    tomorrow = (today + timedelta(days=1)).isoformat()
    yesterday = (today - timedelta(days=1)).isoformat()
    three_days_ago = (today - timedelta(days=3)).isoformat()

    schedule = {
        "matches": [
            # Excluded (future date)
            {
                "id": "M_FUTURE",
                "localDate": tomorrow,
                "homeContestantId": team_id,
                "awayContestantId": "X",
            },
            # Included (yesterday, no scores)
            {
                "id": "M_YEST_HOME",
                "localDate": yesterday,
                "homeContestantId": team_id,
                "awayContestantId": "X",
            },
            # Included (three days ago, no scores, away)
            {
                "id": "M_AWAY",
                "localDate": three_days_ago,
                "homeContestantId": "X",
                "awayContestantId": team_id,
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
    assert out["match_ids"] == ["M_YEST_HOME", "M_AWAY"]

    out_home = await StatsService._get_recent_matches_with_form(  # type: ignore[misc]
        service,
        tournament_id="T",
        team_id=team_id,
        limit=10,
        mando="casa",
        schedule=schedule,
    )
    assert out_home["match_ids"] == ["M_YEST_HOME"]

    out_away = await StatsService._get_recent_matches_with_form(  # type: ignore[misc]
        service,
        tournament_id="T",
        team_id=team_id,
        limit=10,
        mando="fora",
        schedule=schedule,
    )
    assert out_away["match_ids"] == ["M_AWAY"]

