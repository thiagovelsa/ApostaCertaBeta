"""
Exemplo: Calcular Media de Corners Feitos e Sofridos
API VStats / Opta Stats Perform

DESCOBERTA v5.3:
- O campo `lostCorners` EXISTE no endpoint get-match-stats!
- Localizacao: liveData.lineUp[].stat[] onde type = "lostCorners"
- NAO precisa inferir do adversario - campo e direto!
"""

import requests
from typing import List, Dict, Optional

BASE_URL = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"


def get_corners_feitos_agregado(contestant_id: str, tournament_calendar_id: str) -> tuple:
    """
    Obtem corners feitos (Corners Won) via seasonstats - AGREGADO na temporada.
    Retorna: (total, media)
    """
    url = f"{BASE_URL}/stats/seasonstats/v1/team"
    params = {
        "ctst": contestant_id,
        "tmcl": tournament_calendar_id,
        "detailed": "yes"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return 0, 0.0

    data = response.json()

    for stat in data.get('stat', []):
        if stat['name'] == 'Corners Won':
            return int(stat['value']), float(stat['average'])

    return 0, 0.0


def get_team_match_stats(match_id: str, team_id: str) -> Optional[Dict]:
    """
    Obtem estatisticas de um time em uma partida via get-match-stats.
    INCLUI lostCorners, wonCorners, goals, etc.
    """
    url = f"{BASE_URL}/stats/matchstats/v1/get-match-stats?Fx={match_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()
    lineup = data.get('liveData', {}).get('lineUp', [])

    for team in lineup:
        if team.get('contestantId') == team_id:
            # Converter lista de stats para dicionario
            stats = {s.get('type'): s.get('value') for s in team.get('stat', [])}
            return stats

    return None


def get_previous_match_ids(match_id: str, limit: int = 10) -> List[str]:
    """
    Obtem IDs de partidas anteriores via match-preview.
    """
    url = f"{BASE_URL}/stats/matchpreview/v1/get-match-preview"
    params = {"Fx": match_id}

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    data = response.json()

    ids_str = data.get('previousMeetingsAnyComp', {}).get('ids', '')
    if ids_str:
        return ids_str.split(',')[:limit]
    return []


def calcular_corners_usando_lostCorners(team_id: str, match_ids: List[str]) -> Optional[Dict]:
    """
    Calcula corners FEITOS (wonCorners) e SOFRIDOS (lostCorners) de um time.
    USA O CAMPO lostCorners DIRETO - metodo recomendado!
    """
    won_total = 0
    lost_total = 0
    matches_count = 0

    print(f"\n{'='*60}")
    print("USANDO CAMPO lostCorners (metodo recomendado)")
    print(f"{'='*60}\n")

    for match_id in match_ids:
        stats = get_team_match_stats(match_id, team_id)
        if not stats:
            continue

        won = int(stats.get('wonCorners', 0))
        lost = int(stats.get('lostCorners', 0))  # CAMPO DIRETO!

        won_total += won
        lost_total += lost
        matches_count += 1

        print(f"Partida {matches_count}: wonCorners={won}, lostCorners={lost}")

    if matches_count > 0:
        return {
            'corners_won_total': won_total,
            'corners_won_avg': won_total / matches_count,
            'corners_lost_total': lost_total,
            'corners_lost_avg': lost_total / matches_count,
            'matches_analyzed': matches_count
        }

    return None


def main():
    # Exemplo: Arsenal na Premier League 2025/2026
    ARSENAL_ID = "4dsgumo7d4zupm2ugsvm4zm4d"
    PREMIER_LEAGUE_2025_26 = "51r6ph2woavlbbpk8f29nynf8"
    MATCH_ID_FUTURO = "2wehv0cptselv086q8jud4hec"  # Arsenal vs Brighton (27/12/2025)

    print("=" * 60)
    print("CALCULO DE CORNERS FEITOS E SOFRIDOS - ARSENAL")
    print("=" * 60)

    # 1. Corners FEITOS via seasonstats (agregado na temporada)
    total_feitos, media_feitos = get_corners_feitos_agregado(ARSENAL_ID, PREMIER_LEAGUE_2025_26)
    print(f"\n[VIA SEASONSTATS - AGREGADO] Corners Feitos:")
    print(f"  Total na temporada: {total_feitos}")
    print(f"  Media por jogo: {media_feitos:.2f}")

    # 2. Buscar partidas anteriores
    print(f"\nBuscando partidas anteriores...")
    match_ids = get_previous_match_ids(MATCH_ID_FUTURO, limit=10)
    print(f"Encontradas {len(match_ids)} partidas anteriores")

    # 3. Corners FEITOS e SOFRIDOS via get-match-stats (usando lostCorners!)
    if match_ids:
        result = calcular_corners_usando_lostCorners(ARSENAL_ID, match_ids)

        if result:
            print(f"\n{'='*60}")
            print(f"TOTAIS Arsenal ({result['matches_analyzed']} partidas analisadas)")
            print(f"{'='*60}")
            print(f"  Corners Ganhos (wonCorners): {result['corners_won_total']} (media: {result['corners_won_avg']:.2f})")
            print(f"  Corners Sofridos (lostCorners): {result['corners_lost_total']} (media: {result['corners_lost_avg']:.2f})")

    print(f"\n{'='*60}")
    print("CONCLUSAO:")
    print("  - Corners Won (feitos): disponivel AGREGADO via seasonstats")
    print("  - Corners Lost (sofridos): disponivel POR PARTIDA via get-match-stats")
    print("  - Campo lostCorners existe em: liveData.lineUp[].stat[]")
    print("  - NAO precisa calcular usando corners do adversario!")
    print("=" * 60)


if __name__ == "__main__":
    main()
