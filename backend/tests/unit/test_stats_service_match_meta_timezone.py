import pytest

from app.services.stats_service import StatsService


class DummyVStatsRepo:
    async def fetch_match_stats(self, match_id: str) -> dict:
        return {
            "matchInfo": {
                "id": match_id,
                "tournamentCalendar": {"id": "t1"},
                "contestant": [
                    {"position": "home", "id": "home", "officialName": "Home FC"},
                    {"position": "away", "id": "away", "officialName": "Away FC"},
                ],
                "competition": {"knownName": "La Liga"},
                # UTC fields (source of truth for conversion to America/Sao_Paulo)
                "date": "2026-02-07T00:00:00Z",
                "time": "13:00:00Z",
                # Local fields may be in competition timezone; should not be used as source of truth here.
                "localDate": "2026-02-07T00:00:00",
                "localTime": "14:00:00",
            },
            "liveData": {"matchDetailExtra": {"matchOfficials": []}},
        }


@pytest.mark.asyncio
async def test_fetch_match_meta_converts_utc_to_brazil_time() -> None:
    svc = StatsService(vstats_repo=DummyVStatsRepo(), cache=object())  # type: ignore[arg-type]

    meta = await svc._fetch_match_meta("match1")  # noqa: SLF001 (unit test)
    assert meta is not None
    assert meta["data"] == "2026-02-07"
    assert meta["horario"] == "10:00:00"

