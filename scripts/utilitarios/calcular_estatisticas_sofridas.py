"""
Calcular Estatisticas Sofridas/Defensivas - VStats API
========================================================

Este script demonstra como obter estatisticas "sofridas" de um time,
combinando dados do seasonstats (agregados) e get-match-stats (por partida).

DESCOBERTAS PRINCIPAIS:
- Alguns campos "sofridos" existem APENAS no get-match-stats (por partida)
- Outros existem APENAS no seasonstats (agregados)
- Para analise completa, e necessario usar AMBOS os endpoints

CAMPOS EXCLUSIVOS DO get-match-stats:
- lostCorners (corners sofridos)
- penaltyConceded (penaltis cometidos)
- penaltyFaced (penaltis enfrentados)
- penGoalsConceded (gols de penalti sofridos)
- totalRedCard (cartoes vermelhos)
- secondYellow (segundo amarelo)
- saves (defesas do goleiro)

CAMPOS EXCLUSIVOS DO seasonstats:
- Goals Conceded (gols sofridos - agregado)
- Total Shots Conceded (chutes sofridos - agregado)
- Duels lost (duelos perdidos - agregado)
- Tackles Lost (desarmes perdidos - agregado)
"""

import requests
from typing import Dict, List, Optional
from dataclasses import dataclass

BASE_URL = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"


@dataclass
class TeamDefensiveStats:
    """Estatisticas defensivas/sofridas de um time"""
    team_id: str
    team_name: str
    matches_analyzed: int

    # Corners
    corners_won_total: int = 0
    corners_won_avg: float = 0.0
    corners_lost_total: int = 0
    corners_lost_avg: float = 0.0

    # Gols
    goals_scored_total: int = 0
    goals_scored_avg: float = 0.0
    goals_conceded_total: int = 0
    goals_conceded_avg: float = 0.0
    goals_conceded_inside_box: int = 0
    goals_conceded_outside_box: int = 0

    # Finalizacoes
    shots_total: int = 0
    shots_avg: float = 0.0
    shots_conceded_total: int = 0
    shots_conceded_avg: float = 0.0
    shots_on_conceded_inside_box: int = 0
    shots_on_conceded_inside_box_avg: float = 0.0
    shots_on_conceded_outside_box: int = 0
    shots_on_conceded_outside_box_avg: float = 0.0

    # Faltas
    fouls_won_total: int = 0
    fouls_won_avg: float = 0.0
    fouls_conceded_total: int = 0
    fouls_conceded_avg: float = 0.0

    # Cartoes
    yellow_cards_total: int = 0
    yellow_cards_avg: float = 0.0
    red_cards_total: int = 0
    red_cards_avg: float = 0.0

    # Penaltis
    penalties_won_total: int = 0
    penalties_conceded_total: int = 0
    penalties_faced_total: int = 0
    penalty_goals_conceded_total: int = 0

    # Defesa
    saves_total: int = 0
    saves_avg: float = 0.0
    clearances_total: int = 0
    clearances_avg: float = 0.0
    clean_sheets_total: int = 0


def get_seasonstats(team_id: str, tmcl_id: str) -> Dict:
    """Obtem estatisticas agregadas da temporada"""
    url = f"{BASE_URL}/stats/seasonstats/v1/team"
    params = {"ctst": team_id, "tmcl": tmcl_id, "detailed": "yes"}

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {}

    data = response.json()
    stats = {}
    for s in data.get('stat', []):
        stats[s['name']] = {
            'value': s['value'],
            'average': s.get('average', 0)
        }

    return stats


def get_match_stats(match_id: str, team_id: str) -> Optional[Dict]:
    """Obtem estatisticas de um time em uma partida"""
    url = f"{BASE_URL}/stats/matchstats/v1/get-match-stats?Fx={match_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()
    lineup = data.get('liveData', {}).get('lineUp', [])

    for team in lineup:
        if team.get('contestantId') == team_id:
            return {s.get('type'): s.get('value') for s in team.get('stat', [])}

    return None


def get_previous_match_ids(match_id: str, limit: int = 20) -> List[str]:
    """Obtem IDs de partidas anteriores"""
    url = f"{BASE_URL}/stats/matchpreview/v1/get-match-preview?Fx={match_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()
    ids_str = data.get('previousMeetingsAnyComp', {}).get('ids', '')

    if ids_str:
        return ids_str.split(',')[:limit]
    return []


def calculate_defensive_stats(team_id: str, tmcl_id: str, match_id_reference: str) -> TeamDefensiveStats:
    """
    Calcula todas as estatisticas defensivas/sofridas de um time.
    Combina dados do seasonstats (agregados) e get-match-stats (por partida).
    """
    # 1. Obter estatisticas agregadas via seasonstats
    season = get_seasonstats(team_id, tmcl_id)

    # 2. Obter partidas anteriores e calcular estatisticas por partida
    match_ids = get_previous_match_ids(match_id_reference, limit=10)

    # Acumuladores para estatisticas por partida
    corners_lost = []
    penalties_conceded = []
    penalties_faced = []
    penalty_goals_conceded = []
    red_cards = []
    saves = []

    for match_id in match_ids:
        stats = get_match_stats(match_id, team_id)
        if not stats:
            continue

        if 'lostCorners' in stats:
            corners_lost.append(int(stats['lostCorners']))
        if 'penaltyConceded' in stats:
            penalties_conceded.append(int(stats['penaltyConceded']))
        if 'penaltyFaced' in stats:
            penalties_faced.append(int(stats['penaltyFaced']))
        if 'penGoalsConceded' in stats:
            penalty_goals_conceded.append(int(stats['penGoalsConceded']))
        if 'totalRedCard' in stats:
            red_cards.append(int(stats['totalRedCard']))
        if 'saves' in stats:
            saves.append(int(stats['saves']))

    matches_analyzed = len(corners_lost) if corners_lost else 0

    # 3. Construir objeto de resultado
    result = TeamDefensiveStats(
        team_id=team_id,
        team_name=season.get('name', team_id),
        matches_analyzed=matches_analyzed,

        # Corners (seasonstats + get-match-stats)
        corners_won_total=int(season.get('Corners Won', {}).get('value', 0)),
        corners_won_avg=float(season.get('Corners Won', {}).get('average', 0)),
        corners_lost_total=sum(corners_lost),
        corners_lost_avg=sum(corners_lost) / len(corners_lost) if corners_lost else 0,

        # Gols (seasonstats)
        goals_scored_total=int(season.get('Goals', {}).get('value', 0)),
        goals_scored_avg=float(season.get('Goals', {}).get('average', 0)),
        goals_conceded_total=int(season.get('Goals Conceded', {}).get('value', 0)),
        goals_conceded_avg=float(season.get('Goals Conceded', {}).get('average', 0)),
        goals_conceded_inside_box=int(season.get('Goals Conceded Inside Box', {}).get('value', 0)),
        goals_conceded_outside_box=int(season.get('Goals Conceded Outside Box', {}).get('value', 0)),

        # Finalizacoes (seasonstats)
        shots_total=int(season.get('Total Shots', {}).get('value', 0)),
        shots_avg=float(season.get('Total Shots', {}).get('average', 0)),
        shots_conceded_total=int(season.get('Total Shots Conceded', {}).get('value', 0)),
        shots_conceded_avg=float(season.get('Total Shots Conceded', {}).get('average', 0)),
        shots_on_conceded_inside_box=int(season.get('Shots On Conceded Inside Box', {}).get('value', 0)),
        shots_on_conceded_inside_box_avg=float(season.get('Shots On Conceded Inside Box', {}).get('average', 0)),
        shots_on_conceded_outside_box=int(season.get('Shots On Conceded Outside Box', {}).get('value', 0)),
        shots_on_conceded_outside_box_avg=float(season.get('Shots On Conceded Outside Box', {}).get('average', 0)),

        # Faltas (seasonstats)
        fouls_won_total=int(season.get('Total Fouls Won', {}).get('value', 0)),
        fouls_won_avg=float(season.get('Total Fouls Won', {}).get('average', 0)),
        fouls_conceded_total=int(season.get('Total Fouls Conceded', {}).get('value', 0)),
        fouls_conceded_avg=float(season.get('Total Fouls Conceded', {}).get('average', 0)),

        # Cartoes (seasonstats + get-match-stats)
        yellow_cards_total=int(season.get('Yellow Cards', {}).get('value', 0)),
        yellow_cards_avg=float(season.get('Yellow Cards', {}).get('average', 0)),
        red_cards_total=sum(red_cards),
        red_cards_avg=sum(red_cards) / len(red_cards) if red_cards else 0,

        # Penaltis (get-match-stats apenas)
        penalties_conceded_total=sum(penalties_conceded),
        penalties_faced_total=sum(penalties_faced),
        penalty_goals_conceded_total=sum(penalty_goals_conceded),

        # Defesa (seasonstats + get-match-stats)
        saves_total=sum(saves),
        saves_avg=sum(saves) / len(saves) if saves else 0,
        clearances_total=int(season.get('Total Clearances', {}).get('value', 0)),
        clearances_avg=float(season.get('Total Clearances', {}).get('average', 0)),
        clean_sheets_total=int(season.get('Clean Sheets', {}).get('value', 0)),
    )

    return result


def print_defensive_stats(stats: TeamDefensiveStats):
    """Imprime as estatisticas defensivas formatadas"""
    print("=" * 70)
    print(f"ESTATISTICAS DEFENSIVAS/SOFRIDAS")
    print(f"Time: {stats.team_name} ({stats.team_id})")
    print(f"Partidas analisadas (get-match-stats): {stats.matches_analyzed}")
    print("=" * 70)

    print("\n--- CORNERS ---")
    print(f"  Corners Ganhos (Feitos):  {stats.corners_won_total} (media: {stats.corners_won_avg:.2f}) [seasonstats]")
    print(f"  Corners Sofridos (Lost):  {stats.corners_lost_total} (media: {stats.corners_lost_avg:.2f}) [get-match-stats]")

    print("\n--- GOLS ---")
    print(f"  Gols Marcados:            {stats.goals_scored_total} (media: {stats.goals_scored_avg:.2f}) [seasonstats]")
    print(f"  Gols Sofridos:            {stats.goals_conceded_total} (media: {stats.goals_conceded_avg:.2f}) [seasonstats]")
    print(f"    - Dentro da Area:       {stats.goals_conceded_inside_box} [seasonstats]")
    print(f"    - Fora da Area:         {stats.goals_conceded_outside_box} [seasonstats]")

    print("\n--- FINALIZACOES ---")
    print(f"  Finalizacoes Feitas:      {stats.shots_total} (media: {stats.shots_avg:.2f}) [seasonstats]")
    print(f"  Finalizacoes Sofridas:    {stats.shots_conceded_total} (media: {stats.shots_conceded_avg:.2f}) [seasonstats]")
    print(f"  Chutes no Gol Sofridos:")
    print(f"    - Dentro Area:          {stats.shots_on_conceded_inside_box} (media: {stats.shots_on_conceded_inside_box_avg:.2f}) [seasonstats]")
    print(f"    - Fora Area:            {stats.shots_on_conceded_outside_box} (media: {stats.shots_on_conceded_outside_box_avg:.2f}) [seasonstats]")

    print("\n--- FALTAS ---")
    print(f"  Faltas Sofridas (ganhas): {stats.fouls_won_total} (media: {stats.fouls_won_avg:.2f}) [seasonstats]")
    print(f"  Faltas Cometidas:         {stats.fouls_conceded_total} (media: {stats.fouls_conceded_avg:.2f}) [seasonstats]")

    print("\n--- CARTOES ---")
    print(f"  Cartoes Amarelos:         {stats.yellow_cards_total} (media: {stats.yellow_cards_avg:.2f}) [seasonstats]")
    print(f"  Cartoes Vermelhos:        {stats.red_cards_total} (media: {stats.red_cards_avg:.2f}) [get-match-stats]")

    print("\n--- PENALTIS ---")
    print(f"  Penaltis Cometidos:       {stats.penalties_conceded_total} [get-match-stats]")
    print(f"  Penaltis Enfrentados:     {stats.penalties_faced_total} [get-match-stats]")
    print(f"  Gols Penalti Sofridos:    {stats.penalty_goals_conceded_total} [get-match-stats]")

    print("\n--- DEFESA ---")
    print(f"  Defesas Goleiro:          {stats.saves_total} (media: {stats.saves_avg:.2f}) [get-match-stats]")
    print(f"  Cortes/Afastamentos:      {stats.clearances_total} (media: {stats.clearances_avg:.2f}) [seasonstats]")
    print(f"  Clean Sheets:             {stats.clean_sheets_total} [seasonstats]")

    print("\n" + "=" * 70)


def main():
    # Exemplo: Arsenal na Premier League 2025/2026
    ARSENAL_ID = "4dsgumo7d4zupm2ugsvm4zm4d"
    PREMIER_LEAGUE_2025_26 = "51r6ph2woavlbbpk8f29nynf8"
    MATCH_ID_REFERENCE = "2wehv0cptselv086q8jud4hec"  # Arsenal vs Brighton

    print("\nCalculando estatisticas defensivas do Arsenal...")
    print("Isso pode levar alguns segundos...\n")

    stats = calculate_defensive_stats(ARSENAL_ID, PREMIER_LEAGUE_2025_26, MATCH_ID_REFERENCE)
    print_defensive_stats(stats)

    print("\nLEGENDA:")
    print("  [seasonstats]     = Estatistica agregada da temporada (endpoint seasonstats/v1/team)")
    print("  [get-match-stats] = Estatistica calculada de partidas individuais (endpoint matchstats/v1/get-match-stats)")


if __name__ == "__main__":
    main()
