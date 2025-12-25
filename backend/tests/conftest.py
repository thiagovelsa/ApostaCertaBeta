"""
Pytest Configuration and Fixtures
==================================

Fixtures compartilhadas para todos os testes.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_match_data():
    """Dados de partida para testes"""
    return {
        "id": "f4vscquffy37afgv0arwcbztg",
        "localDate": "2025-12-27",
        "localTime": "17:00:00",
        "homeContestantId": "4dsgumo7d4zupm2ugsvm4zm4d",
        "homeContestantName": "Arsenal",
        "awayContestantId": "1c8m2ko0wxq1asfkuykurdr0y",
        "awayContestantName": "Crystal Palace",
    }


@pytest.fixture
def sample_stats_values():
    """Valores para teste de CV"""
    return {
        "stable": [2, 2, 2, 2, 2],  # CV = 0
        "moderate": [1, 2, 3, 2, 1],  # CV moderado
        "unstable": [0, 5, 1, 4, 0],  # CV alto
    }


@pytest.fixture
def vstats_schedule_response():
    """Resposta simulada do endpoint schedule/month"""
    return {
        "data": {
            "matches": [
                {
                    "id": "f4vscquffy37afgv0arwcbztg",
                    "date": "2025-12-27T17:00:00Z",
                    "localDate": "2025-12-27",
                    "localTime": "17:00:00",
                    "homeContestantId": "4dsgumo7d4zupm2ugsvm4zm4d",
                    "homeContestantClubName": "Arsenal",
                    "awayContestantId": "1c8m2ko0wxq1asfkuykurdr0y",
                    "awayContestantClubName": "Crystal Palace",
                    "status": {"name": "Fixture"},
                }
            ]
        }
    }


@pytest.fixture
def vstats_seasonstats_response():
    """Resposta simulada do endpoint seasonstats"""
    return {
        "data": {
            "team": {
                "id": "4dsgumo7d4zupm2ugsvm4zm4d",
                "name": "Arsenal",
            },
            "statistics": {
                "goals": 45,
                "goalsConceded": 20,
                "wonCorners": 120,
                "lostCorners": 80,
                "totalScoringAtt": 280,
                "ontargetScoringAtt": 140,
                "totalYellowCard": 35,
                "totalRedCard": 2,
            },
            "matchesPlayed": 20,
        }
    }
