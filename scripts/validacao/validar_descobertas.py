"""
Validação de Descobertas - VStats API
======================================
Script para testar todas as descobertas e confirmar que não são falsos positivos.
"""

import requests
import json
from typing import Dict, List, Any

BASE_URL = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"

# IDs de Referência
ARSENAL_ID = "4dsgumo7d4zupm2ugsvm4zm4d"
PREMIER_LEAGUE_2025_26 = "51r6ph2woavlbbpk8f29nynf8"
MATCH_ID = "adxx1ue4e7h0i93pwl7xucr2s"  # Arsenal vs Everton


def test_seasonstats():
    """Testa endpoint seasonstats e verifica campos 'sofridos'"""
    print("\n" + "=" * 70)
    print("TESTE 1: SEASONSTATS - Campos Agregados")
    print("=" * 70)

    url = f"{BASE_URL}/stats/seasonstats/v1/team"
    params = {"ctst": ARSENAL_ID, "tmcl": PREMIER_LEAGUE_2025_26, "detailed": "yes"}

    response = requests.get(url, params=params)
    print(f"\nStatus: {response.status_code}")

    if response.status_code != 200:
        print("FALHA: Endpoint não respondeu")
        return False

    data = response.json()
    stats = {s['name']: {'value': s['value'], 'average': s.get('average', 0)} for s in data.get('stat', [])}

    print(f"Total de campos retornados: {len(stats)}")

    # Campos "sofridos" a verificar
    campos_sofridos = [
        "Total Shots Conceded",
        "Shots On Conceded Inside Box",
        "Shots On Conceded Outside Box",
        "Goals Conceded",
        "Goals Conceded Inside Box",
        "Goals Conceded Outside Box",
        "Ground Duels lost",
        "Aerial Duels lost",
        "Handballs conceded",
        "Total Fouls Conceded",
        "Clean Sheets",
        "Total Clearances",
        "Tackles Lost"
    ]

    print("\n--- CAMPOS SOFRIDOS/DEFENSIVOS ---")
    confirmados = 0
    for campo in campos_sofridos:
        if campo in stats:
            valor = stats[campo]['value']
            media = stats[campo]['average']
            print(f"  [OK] {campo}: {valor} (avg: {media}) - CONFIRMADO")
            confirmados += 1
        else:
            print(f"  [--] {campo} - NAO ENCONTRADO")

    print(f"\nResumo: {confirmados}/{len(campos_sofridos)} campos confirmados")
    return confirmados > 0


def test_get_match_stats():
    """Testa endpoint get-match-stats e verifica campos 'sofridos'"""
    print("\n" + "=" * 70)
    print("TESTE 2: GET-MATCH-STATS - Campos por Partida")
    print("=" * 70)

    url = f"{BASE_URL}/stats/matchstats/v1/get-match-stats?Fx={MATCH_ID}"
    response = requests.get(url)
    print(f"\nStatus: {response.status_code}")

    if response.status_code != 200:
        print("FALHA: Endpoint não respondeu")
        return False

    data = response.json()
    lineup = data.get('liveData', {}).get('lineUp', [])

    # Encontrar Arsenal
    arsenal_stats = None
    for team in lineup:
        if team.get('contestantId') == ARSENAL_ID:
            arsenal_stats = {s.get('type'): s.get('value') for s in team.get('stat', [])}
            break

    if not arsenal_stats:
        print("FALHA: Estatísticas do Arsenal não encontradas")
        return False

    print(f"Total de campos retornados: {len(arsenal_stats)}")

    # Campos "sofridos" a verificar
    campos_sofridos = [
        "lostCorners",
        "wonCorners",
        "penaltyConceded",
        "penaltyFaced",
        "penGoalsConceded",
        "totalRedCard",
        "secondYellow",
        "saves",
        "goalsConceded",
        "totalYellowCard",
        "goals"
    ]

    print("\n--- CAMPOS SOFRIDOS/DEFENSIVOS ---")
    confirmados = 0
    for campo in campos_sofridos:
        if campo in arsenal_stats:
            valor = arsenal_stats[campo]
            print(f"  [OK] {campo}: {valor} - CONFIRMADO")
            confirmados += 1
        else:
            print(f"  [--] {campo} - NAO ENCONTRADO")

    print(f"\nResumo: {confirmados}/{len(campos_sofridos)} campos confirmados")

    # Listar todos os campos disponíveis
    print("\n--- TODOS OS CAMPOS DISPONÍVEIS ---")
    for k, v in sorted(arsenal_stats.items()):
        print(f"  {k}: {v}")

    return confirmados > 0


def test_multiple_matches():
    """Testa multiplas partidas para validar campos que podem nao aparecer em uma partida especifica"""
    print("\n" + "=" * 70)
    print("TESTE 2B: MULTIPLAS PARTIDAS - Campos Condicionais")
    print("=" * 70)
    print("\n(Campos como totalYellowCard, totalRedCard so aparecem se houver)")

    # IDs de partidas da Premier League 2025/26
    match_ids = [
        "adxx1ue4e7h0i93pwl7xucr2s",  # Arsenal vs Everton
        "ax6pxq8xhseo5x2x0cpdddqz4",  # Brighton vs Arsenal
        "2wehv0cptselv086q8jud4hec",  # Arsenal vs Brighton (future)
    ]

    campos_condicionais = [
        "totalYellowCard",
        "totalRedCard",
        "secondYellow",
        "penaltyConceded",
        "penaltyFaced",
        "penGoalsConceded",
        "goalsConceded"
    ]

    campos_encontrados = set()

    for match_id in match_ids:
        url = f"{BASE_URL}/stats/matchstats/v1/get-match-stats?Fx={match_id}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue

            data = response.json()
            lineup = data.get('liveData', {}).get('lineUp', [])

            for team in lineup:
                stats = {s.get('type'): s.get('value') for s in team.get('stat', [])}
                for campo in campos_condicionais:
                    if campo in stats and stats[campo]:
                        campos_encontrados.add(campo)
                        print(f"  [OK] {campo}: {stats[campo]} (match: {match_id[:8]}...)")
        except:
            continue

    print(f"\nCampos condicionais encontrados: {len(campos_encontrados)}/{len(campos_condicionais)}")
    print(f"Campos: {list(campos_encontrados)}")
    print("\nNOTA: Campos como penaltyConceded so aparecem em partidas com penaltis")

    return len(campos_encontrados) > 0


def test_standings():
    """Testa endpoint standings"""
    print("\n" + "=" * 70)
    print("TESTE 3: STANDINGS")
    print("=" * 70)

    url = f"{BASE_URL}/stats/standings/v1/standings"
    params = {"tmcl": PREMIER_LEAGUE_2025_26, "detailed": "false"}

    response = requests.get(url, params=params)
    print(f"\nStatus: {response.status_code}")

    if response.status_code != 200:
        print("FALHA: Endpoint não respondeu")
        return False

    data = response.json()
    # Estrutura: data.total.ranking[]
    rankings = data.get('total', {}).get('ranking', [])

    print(f"Times na tabela: {len(rankings)}")

    if rankings:
        # Mostrar top 5
        print("\n--- TOP 5 ---")
        for team in rankings[:5]:
            nome = team.get('contestantShortName', 'N/A')
            pts = team.get('points', 0)
            pos = team.get('rank', 0)
            print(f"  {pos}. {nome} - {pts} pts")

        # Verificar campos disponíveis
        if rankings[0]:
            print(f"\nCampos disponíveis: {list(rankings[0].keys())}")

        return True
    return False


def test_tournament_calendar():
    """Testa endpoint tournament calendar"""
    print("\n" + "=" * 70)
    print("TESTE 4: TOURNAMENT CALENDAR")
    print("=" * 70)

    url = f"{BASE_URL}/stats/tournament/v1/calendar"
    params = {"Comp": "2kwbbcootiqqgmrzs6o5inle5"}  # Premier League

    response = requests.get(url, params=params)
    print(f"\nStatus: {response.status_code}")

    if response.status_code != 200:
        print("FALHA: Endpoint não respondeu")
        return False

    data = response.json()
    # API retorna lista direta
    calendars = data if isinstance(data, list) else data.get('tournamentCalendar', [])

    print(f"Temporadas disponíveis: {len(calendars)}")

    if calendars:
        print("\n--- ÚLTIMAS 3 TEMPORADAS ---")
        for cal in calendars[:3]:
            nome = cal.get('name', 'N/A')
            cal_id = cal.get('id', 'N/A')
            print(f"  {nome} - ID: {cal_id}")
        return True
    return False


def main():
    print("=" * 70)
    print("VALIDAÇÃO DE DESCOBERTAS - VStats API")
    print("=" * 70)
    print(f"\nIDs de referência:")
    print(f"  Arsenal: {ARSENAL_ID}")
    print(f"  Premier League 2025/26: {PREMIER_LEAGUE_2025_26}")
    print(f"  Match ID: {MATCH_ID}")

    resultados = []

    # Teste 1: Seasonstats
    resultados.append(("Seasonstats", test_seasonstats()))

    # Teste 2: Get Match Stats
    resultados.append(("Get Match Stats", test_get_match_stats()))

    # Teste 2B: Multiplas partidas
    resultados.append(("Campos Condicionais", test_multiple_matches()))

    # Teste 3: Standings
    resultados.append(("Standings", test_standings()))

    # Teste 4: Tournament Calendar
    resultados.append(("Tournament Calendar", test_tournament_calendar()))

    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)

    for nome, sucesso in resultados:
        status = "[OK] CONFIRMADO" if sucesso else "[--] FALSO POSITIVO"
        print(f"  {nome}: {status}")

    confirmados = sum(1 for _, s in resultados if s)
    print(f"\nTotal: {confirmados}/{len(resultados)} endpoints confirmados")


if __name__ == "__main__":
    main()
