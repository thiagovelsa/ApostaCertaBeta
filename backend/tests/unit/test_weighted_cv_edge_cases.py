from app.services.stats_service import StatsService


def test_cv_all_zeros_is_na_not_confident() -> None:
    matches = [
        {
            "wonCorners": 0,
            "lostCorners": 0,
            "goals": 0,
            "goalsConceded": 0,
            "totalScoringAtt": 0,
            "totalShotsConceded": 0,
            "ontargetScoringAtt": 0,
            "ontargetScoringAttConceded": 0,
            "totalYellowCard": 0,
            "fkFoulLost": 0,
        }
        for _ in range(3)
    ]

    service = StatsService.__new__(StatsService)
    stats = StatsService._calculate_metrics_from_matches(service, matches, [1.0, 1.0, 1.0])  # type: ignore[misc]

    assert stats.gols.feitos.classificacao == "N/A"
    assert stats.gols.feitos.cv == 1.0
    assert stats.gols.feitos.estabilidade == 0


def test_cv_non_zero_mean_is_computed() -> None:
    matches = [
        {
            "wonCorners": 0,
            "lostCorners": 0,
            "goals": 1,
            "goalsConceded": 0,
            "totalScoringAtt": 0,
            "totalShotsConceded": 0,
            "ontargetScoringAtt": 0,
            "ontargetScoringAttConceded": 0,
            "totalYellowCard": 0,
            "fkFoulLost": 0,
        },
        {
            "wonCorners": 0,
            "lostCorners": 0,
            "goals": 2,
            "goalsConceded": 0,
            "totalScoringAtt": 0,
            "totalShotsConceded": 0,
            "ontargetScoringAtt": 0,
            "ontargetScoringAttConceded": 0,
            "totalYellowCard": 0,
            "fkFoulLost": 0,
        },
        {
            "wonCorners": 0,
            "lostCorners": 0,
            "goals": 3,
            "goalsConceded": 0,
            "totalScoringAtt": 0,
            "totalShotsConceded": 0,
            "ontargetScoringAtt": 0,
            "ontargetScoringAttConceded": 0,
            "totalYellowCard": 0,
            "fkFoulLost": 0,
        },
    ]

    service = StatsService.__new__(StatsService)
    stats = StatsService._calculate_metrics_from_matches(service, matches, [1.0, 1.0, 1.0])  # type: ignore[misc]

    assert stats.gols.feitos.classificacao != "N/A"
    assert stats.gols.feitos.cv > 0

