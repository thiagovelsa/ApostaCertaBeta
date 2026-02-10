"""Parâmetros calibrados por competição.

Centraliza valores que hoje existem no frontend (e em partes do backend) para:
- priors (regressão à média)
- rho do Dixon-Coles
- vantagem de mando

Os valores são heurísticos/fallbacks e devem ser refinados com backtesting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class LeagueParams:
    goals_mean_total: float
    corners_mean_total: float
    cards_mean_total: float
    dixon_coles_rho: float
    home_advantage_factor: float
    poisson_normal_threshold: float
    teams_count: int


DEFAULT_PARAMS = LeagueParams(
    goals_mean_total=2.7,
    corners_mean_total=9.5,
    cards_mean_total=4.2,
    dixon_coles_rho=-0.13,
    home_advantage_factor=1.08,
    poisson_normal_threshold=7.0,
    teams_count=20,
)


LEAGUE_PARAMS: Dict[str, LeagueParams] = {
    "Premier League": LeagueParams(
        goals_mean_total=2.65,
        corners_mean_total=9.8,
        cards_mean_total=3.8,
        dixon_coles_rho=-0.12,
        home_advantage_factor=1.07,
        poisson_normal_threshold=7.0,
        teams_count=20,
    ),
    "La Liga": LeagueParams(
        goals_mean_total=2.48,
        corners_mean_total=8.9,
        cards_mean_total=4.5,
        dixon_coles_rho=-0.14,
        home_advantage_factor=1.06,
        poisson_normal_threshold=7.0,
        teams_count=20,
    ),
    "Serie A": LeagueParams(
        goals_mean_total=2.72,
        corners_mean_total=9.2,
        cards_mean_total=4.8,
        dixon_coles_rho=-0.11,
        home_advantage_factor=1.08,
        poisson_normal_threshold=7.0,
        teams_count=20,
    ),
    "Bundesliga": LeagueParams(
        goals_mean_total=2.95,
        corners_mean_total=10.1,
        cards_mean_total=4.0,
        dixon_coles_rho=-0.10,
        home_advantage_factor=1.09,
        poisson_normal_threshold=7.0,
        teams_count=18,
    ),
    "Ligue 1": LeagueParams(
        goals_mean_total=2.58,
        corners_mean_total=9.0,
        cards_mean_total=4.2,
        dixon_coles_rho=-0.13,
        home_advantage_factor=1.07,
        poisson_normal_threshold=7.0,
        teams_count=18,
    ),
    "Brasileirão": LeagueParams(
        goals_mean_total=2.35,
        corners_mean_total=10.5,
        cards_mean_total=5.2,
        dixon_coles_rho=-0.15,
        home_advantage_factor=1.10,
        poisson_normal_threshold=7.0,
        teams_count=20,
    ),
}


def get_league_params(competition_name: Optional[str]) -> LeagueParams:
    if not competition_name:
        return DEFAULT_PARAMS

    comp = competition_name.lower()
    for key, params in LEAGUE_PARAMS.items():
        if key.lower() in comp:
            return params

    return DEFAULT_PARAMS
