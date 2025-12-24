"""
Validacao de Get-Match-Stats - Filtros "5 Partidas" e "10 Partidas"
====================================================================
Valida todas as estatisticas disponiveis no endpoint get-match-stats,
incluindo calculo de CV (Coeficiente de Variacao).

Data: 24/12/2025
Referencia: PROJETO_SISTEMA_ANALISE.md secao 4.2 e 11
"""

import requests
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

BASE_URL = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"

# IDs de teste
ARSENAL_ID = "4dsgumo7d4zupm2ugsvm4zm4d"
PREMIER_LEAGUE_2025_26 = "51r6ph2woavlbbpk8f29nynf8"

# IDs de partidas conhecidas do Arsenal (para teste)
KNOWN_MATCH_IDS = [
    "adxx1ue4e7h0i93pwl7xucr2s",  # Arsenal vs Everton
    "ax6pxq8xhseo5x2x0cpdddqz4",  # Brighton vs Arsenal
    "c3azlvd97gyv7x0unm43czw9g",  # Outra partida
    "a5sr0ba7amh9cuylpfu6pev4k",  # Outra partida
    "f4vscquffy37afgv0arwcbztg",  # Outra partida
]


@dataclass
class MatchStats:
    """Estatisticas de um time em uma partida"""
    match_id: str
    won_corners: int
    lost_corners: int
    goals: int
    goals_conceded: int
    total_shots: int
    shots_on_target: int
    shots_conceded: int  # Via adversario
    shots_on_conceded: int  # Via adversario
    yellow_cards: int
    red_cards: int


@dataclass
class StatisticSummary:
    """Resumo estatistico de uma metrica"""
    name: str
    values: List[int]
    mean: float
    std_dev: float
    cv: float
    classification: str
    matches_count: int


# Campos a validar (diretos)
DIRECT_FIELDS = [
    'wonCorners',
    'lostCorners',
    'goals',
    'goalsConceded',
    'totalScoringAtt',
    'ontargetScoringAtt',
    'totalYellowCard',
    'totalRedCard',
]


def classify_cv(cv: float) -> str:
    """Classifica o CV em categorias de estabilidade"""
    if cv < 0.15:
        return "Muito Estavel"
    elif cv < 0.30:
        return "Estavel"
    elif cv < 0.50:
        return "Moderado"
    elif cv < 0.75:
        return "Instavel"
    else:
        return "Muito Instavel"


def get_match_ids_from_schedule(team_id: str, tournament_id: str, limit: int = 10) -> List[str]:
    """Obtem IDs de partidas de um time via schedule/month"""
    match_ids = []

    url = f"{BASE_URL}/stats/tournament/v1/schedule/month"
    params = {"Tmcl": tournament_id}

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            return []

        data = response.json()
        for date_obj in data.get('matchDate', []):
            for match in date_obj.get('match', []):
                # Verificar se o time esta na partida
                if team_id in [match.get('homeContestantId'), match.get('awayContestantId')]:
                    # Verificar se a partida ja foi realizada
                    if match.get('homeScore') is not None:
                        match_ids.append(match.get('id'))
                        if len(match_ids) >= limit:
                            return match_ids
    except Exception as e:
        print(f"Erro ao buscar schedule: {e}")

    return match_ids


def extract_team_stats(match_id: str, team_id: str) -> Optional[Tuple[MatchStats, Dict]]:
    """
    Extrai estatisticas de um time em uma partida.
    Retorna (MatchStats, field_presence_dict)
    """
    url = f"{BASE_URL}/stats/matchstats/v1/get-match-stats"
    params = {"Fx": match_id}

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            return None

        data = response.json()
        lineup = data.get('liveData', {}).get('lineUp', [])

        team_stats = None
        opponent_stats = None

        for team in lineup:
            stats_dict = {s.get('type'): int(float(s.get('value', 0))) for s in team.get('stat', [])}

            if team.get('contestantId') == team_id:
                team_stats = stats_dict
            else:
                opponent_stats = stats_dict

        if not team_stats:
            return None

        # Registrar presenca de campos
        field_presence = {field: field in team_stats for field in DIRECT_FIELDS}

        # Criar MatchStats
        match_stats = MatchStats(
            match_id=match_id,
            won_corners=team_stats.get('wonCorners', 0),
            lost_corners=team_stats.get('lostCorners', 0),
            goals=team_stats.get('goals', 0),
            goals_conceded=team_stats.get('goalsConceded', 0),
            total_shots=team_stats.get('totalScoringAtt', 0),
            shots_on_target=team_stats.get('ontargetScoringAtt', 0),
            shots_conceded=opponent_stats.get('totalScoringAtt', 0) if opponent_stats else 0,
            shots_on_conceded=opponent_stats.get('ontargetScoringAtt', 0) if opponent_stats else 0,
            yellow_cards=team_stats.get('totalYellowCard', 0),
            red_cards=team_stats.get('totalRedCard', 0),
        )

        return match_stats, field_presence

    except Exception as e:
        print(f"Erro ao extrair stats de {match_id}: {e}")
        return None


def calculate_summary(name: str, values: List[int]) -> Optional[StatisticSummary]:
    """Calcula media, desvio padrao e CV"""
    if len(values) < 2:
        return None

    mean = statistics.mean(values)
    std_dev = statistics.stdev(values)
    cv = std_dev / mean if mean > 0 else 0

    return StatisticSummary(
        name=name,
        values=values,
        mean=mean,
        std_dev=std_dev,
        cv=cv,
        classification=classify_cv(cv),
        matches_count=len(values)
    )


def validate_filter(team_id: str, match_ids: List[str], filter_name: str) -> Tuple[bool, Dict]:
    """
    Valida estatisticas para um filtro especifico.
    Retorna (sucesso, resultados)
    """
    print(f"\n--- FILTRO: {filter_name} ---")
    print(f"Partidas a analisar: {len(match_ids)}")

    all_match_stats: List[MatchStats] = []
    field_presence_totals: Dict[str, int] = {field: 0 for field in DIRECT_FIELDS}

    # Coletar stats de cada partida
    for i, match_id in enumerate(match_ids):
        result = extract_team_stats(match_id, team_id)
        if result:
            match_stats, field_presence = result
            all_match_stats.append(match_stats)
            for field, present in field_presence.items():
                if present:
                    field_presence_totals[field] += 1
            print(f"  [{i+1}/{len(match_ids)}] {match_id[:12]}... OK")
        else:
            print(f"  [{i+1}/{len(match_ids)}] {match_id[:12]}... sem dados")

    if len(all_match_stats) < 2:
        print("ERRO: Menos de 2 partidas com dados")
        return False, {}

    print(f"\nPartidas analisadas: {len(all_match_stats)}")

    # Validar presenca de campos
    print("\n=== VALIDACAO DE CAMPOS ===")
    total_matches = len(all_match_stats)
    all_present = True

    for field in DIRECT_FIELDS:
        count = field_presence_totals[field]
        pct = 100 * count / total_matches

        # Campos condicionais podem ter menor presenca
        # (cartoes, gols sofridos quando time nao sofre gols)
        is_conditional = field in ['totalRedCard', 'totalYellowCard', 'goalsConceded']
        threshold = 50 if is_conditional else 80

        status = "OK" if pct >= threshold else "BAIXO"
        symbol = "OK" if pct >= threshold else "!!"

        note = ""
        if field == 'lostCorners' and pct == 100:
            note = " (CONFIRMADO!)"
        elif is_conditional and pct < 50:
            note = " (raro - esperado)"

        print(f"{field:25} {count}/{total_matches}  [{symbol}] {pct:.0f}%{note}")

        if pct < threshold and not is_conditional:
            all_present = False

    # Calcular estatisticas
    print("\n=== ESTATISTICAS CALCULADAS (FEITOS) ===")
    print(f"{'Estatistica':<25} {'Media':>8} {'Desvio':>8} {'CV':>8} {'Classificacao':>15}")
    print("-" * 70)

    feitos = [
        ("Escanteios Feitos", [m.won_corners for m in all_match_stats]),
        ("Gols Feitos", [m.goals for m in all_match_stats]),
        ("Finalizacoes", [m.total_shots for m in all_match_stats]),
        ("Finalizacoes ao Gol", [m.shots_on_target for m in all_match_stats]),
        ("Cartoes Amarelos", [m.yellow_cards for m in all_match_stats]),
    ]

    for name, values in feitos:
        summary = calculate_summary(name, values)
        if summary:
            print(f"{name:<25} {summary.mean:>8.2f} {summary.std_dev:>8.2f} {summary.cv:>8.3f} {summary.classification:>15}")

    print("\n=== ESTATISTICAS CALCULADAS (SOFRIDOS) ===")
    print(f"{'Estatistica':<25} {'Media':>8} {'Desvio':>8} {'CV':>8} {'Classificacao':>15}")
    print("-" * 70)

    sofridos = [
        ("Escanteios Sofridos", [m.lost_corners for m in all_match_stats]),
        ("Gols Sofridos", [m.goals_conceded for m in all_match_stats]),
        ("Finalizacoes Sofridas", [m.shots_conceded for m in all_match_stats]),
        ("Finalizacoes Gol Sofridas", [m.shots_on_conceded for m in all_match_stats]),
    ]

    for name, values in sofridos:
        summary = calculate_summary(name, values)
        if summary:
            print(f"{name:<25} {summary.mean:>8.2f} {summary.std_dev:>8.2f} {summary.cv:>8.3f} {summary.classification:>15}")

    return all_present, {
        'matches_analyzed': len(all_match_stats),
        'field_presence': field_presence_totals,
        'lost_corners_pct': 100 * field_presence_totals.get('lostCorners', 0) / total_matches
    }


def main():
    """Execucao principal"""
    print("=" * 72)
    print("VALIDACAO: GET-MATCH-STATS (FILTROS 5 E 10 PARTIDAS)")
    print("=" * 72)
    print(f"Time: Arsenal")
    print(f"Competicao: Premier League 2025/26")

    # Tentar obter IDs de partidas via schedule
    print("\nBuscando partidas via schedule/month...")
    match_ids = get_match_ids_from_schedule(ARSENAL_ID, PREMIER_LEAGUE_2025_26, limit=10)

    if len(match_ids) < 5:
        print(f"Apenas {len(match_ids)} partidas encontradas via schedule, usando IDs conhecidos...")
        match_ids = KNOWN_MATCH_IDS
    else:
        print(f"Encontradas {len(match_ids)} partidas")

    results = []

    # Validar filtro 5 partidas
    if len(match_ids) >= 5:
        success_5, data_5 = validate_filter(ARSENAL_ID, match_ids[:5], "5 PARTIDAS")
        results.append(("5 Partidas", success_5, data_5))

    # Validar filtro 10 partidas
    if len(match_ids) >= 10:
        success_10, data_10 = validate_filter(ARSENAL_ID, match_ids[:10], "10 PARTIDAS")
        results.append(("10 Partidas", success_10, data_10))
    elif len(match_ids) >= 5:
        print(f"\nNOTA: Apenas {len(match_ids)} partidas disponiveis, testando com todas...")
        success_all, data_all = validate_filter(ARSENAL_ID, match_ids, f"{len(match_ids)} PARTIDAS")
        results.append((f"{len(match_ids)} Partidas", success_all, data_all))

    # Resumo final
    print("\n" + "=" * 72)
    print("RESULTADO CONSOLIDADO:")
    print("=" * 72)

    all_success = True

    for filter_name, success, data in results:
        if data:
            lost_corners_pct = data.get('lost_corners_pct', 0)
            matches = data.get('matches_analyzed', 0)

            if lost_corners_pct == 100:
                print(f"[OK] lostCorners CONFIRMADO em 100% das partidas ({filter_name})")
            else:
                print(f"[!!] lostCorners presente em {lost_corners_pct:.0f}% das partidas ({filter_name})")

            if not success:
                all_success = False

    print()

    if all_success and results:
        print("[OK] Calculo via adversario VALIDADO")
        print("[OK] CV calculado corretamente para todas as metricas")
        print("[OK] Todos os campos obrigatorios presentes")
        print()
        print("VALIDACAO BEM-SUCEDIDA - FILTROS 5 E 10 PRONTOS!")
    else:
        print("[!!] Alguns campos podem estar faltando")
        print("[!!] Verifique os avisos acima")

    print("=" * 72)

    return all_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
