"""
Calcular Coeficiente de Variacao (CV) - VStats API
===================================================

O Coeficiente de Variacao mede a estabilidade/consistencia de uma estatistica.
Quanto mais proximo de 0, mais estavel. Quanto mais proximo de 1+, mais instavel.

Formula: CV = Desvio Padrao / Media

ESCALA DE INTERPRETACAO:
  0.00 - 0.15: Muito Estavel (time muito consistente)
  0.15 - 0.30: Estavel (time consistente)
  0.30 - 0.50: Moderado (variacao normal)
  0.50 - 0.75: Instavel (time inconsistente)
  0.75+      : Muito Instavel (resultados imprevisiveis)

ESTATISTICAS ANALISADAS (FEITOS e SOFRIDOS):
+------------------+------------------------+------------------------+
| Categoria        | FEITOS                 | SOFRIDOS               |
+------------------+------------------------+------------------------+
| Corners          | wonCorners             | lostCorners            |
| Gols             | goals                  | goalsConceded          |
| Finalizacoes     | totalScoringAtt        | (via adversario)       |
| Finalizacoes Gol | ontargetScoringAtt     | (via adversario)       |
| Cartoes Amarelos | totalYellowCard        | (adversario)           |
| Cartoes Vermelhos| totalRedCard           | (adversario)           |
| Faltas           | fkFoulLost (cometidas) | fkFoulWon (sofridas)   |
| Penaltis         | (a favor)              | penaltyConceded        |
| Defesas          | saves                  | -                      |
+------------------+------------------------+------------------------+

USO PARA APOSTAS:
  - Times com CV baixo sao mais previsiveis
  - Times com CV alto podem surpreender (positiva ou negativamente)
  - Comparar CV entre times pode indicar qual e mais confiavel
  - CV de gols sofridos alto = defesa inconsistente
  - CV de gols feitos alto = ataque inconsistente
"""

import requests
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

BASE_URL = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"


@dataclass
class StatisticCV:
    """Resultado do calculo de CV para uma estatistica"""
    name: str
    values: List[int]
    mean: float
    std_dev: float
    cv: float
    classification: str
    matches_analyzed: int


@dataclass
class TeamVariabilityReport:
    """Relatorio completo de variabilidade de um time"""
    team_id: str
    team_name: str
    matches_analyzed: int
    statistics: Dict[str, StatisticCV] = field(default_factory=dict)


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


def calculate_cv(values: List[int], name: str) -> Optional[StatisticCV]:
    """Calcula o Coeficiente de Variacao para uma lista de valores"""
    if len(values) < 2:
        return None

    mean = statistics.mean(values)
    std_dev = statistics.stdev(values)
    cv = std_dev / mean if mean > 0 else 0

    return StatisticCV(
        name=name,
        values=values,
        mean=mean,
        std_dev=std_dev,
        cv=cv,
        classification=classify_cv(cv),
        matches_analyzed=len(values)
    )


def get_match_ids_from_schedule(team_id: str, tournament_id: str, limit: int = 20) -> List[str]:
    """
    Obtem IDs de partidas de um time via schedule.
    Busca os ultimos meses para encontrar partidas ja realizadas.
    """
    match_ids = []
    months_to_check = [
        (12, 2025), (11, 2025), (10, 2025), (9, 2025), (8, 2025)
    ]

    for month, year in months_to_check:
        if len(match_ids) >= limit:
            break

        url = f"{BASE_URL}/stats/tournament/v1/schedule/month"
        params = {"Tmcl": tournament_id, "month": month, "year": year}

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                continue

            data = response.json()
            for date_obj in data.get('matchDate', []):
                for match in date_obj.get('match', []):
                    # Verificar se o time esta na partida
                    if team_id in [match.get('homeContestantId'), match.get('awayContestantId')]:
                        # Verificar se a partida ja foi realizada (tem score)
                        if match.get('homeScore') is not None:
                            match_ids.append(match.get('id'))
        except:
            continue

    return match_ids[:limit]


def get_match_ids_from_preview(match_id: str, limit: int = 20) -> List[str]:
    """
    Obtem IDs de partidas anteriores via match-preview.
    Usa o campo previousMeetingsAnyComp.
    """
    url = f"{BASE_URL}/stats/matchpreview/v1/get-match-preview"
    params = {"Fx": match_id}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []

        data = response.json()
        ids_str = data.get('previousMeetingsAnyComp', {}).get('ids', '')

        if ids_str:
            return ids_str.split(',')[:limit]
    except:
        pass

    return []


def get_team_stats_from_match(match_id: str, team_id: str) -> Optional[Dict[str, int]]:
    """Obtem estatisticas de um time em uma partida especifica"""
    url = f"{BASE_URL}/stats/matchstats/v1/get-match-stats"
    params = {"Fx": match_id}

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            return None

        data = response.json()
        lineup = data.get('liveData', {}).get('lineUp', [])

        for team in lineup:
            if team.get('contestantId') == team_id:
                stats = {}
                for s in team.get('stat', []):
                    try:
                        stats[s.get('type')] = int(float(s.get('value', 0)))
                    except:
                        pass
                return stats
    except:
        pass

    return None


def calculate_team_variability(
    team_id: str,
    team_name: str,
    match_ids: List[str],
    stats_to_analyze: List[str] = None
) -> TeamVariabilityReport:
    """
    Calcula o CV para todas as estatisticas de um time.

    Args:
        team_id: ID do time (contestantId)
        team_name: Nome do time
        match_ids: Lista de IDs de partidas para analisar
        stats_to_analyze: Lista de estatisticas a analisar (None = todas)

    Returns:
        TeamVariabilityReport com CV de cada estatistica
    """
    # Estatisticas padrao para analisar (FEITOS e SOFRIDOS)
    if stats_to_analyze is None:
        stats_to_analyze = [
            # === CORNERS ===
            'wonCorners',       # Escanteios FEITOS
            'lostCorners',      # Escanteios SOFRIDOS

            # === GOLS ===
            'goals',            # Gols FEITOS
            'goalsConceded',    # Gols SOFRIDOS

            # === FINALIZACOES ===
            'totalScoringAtt',      # Finalizacoes FEITAS
            'ontargetScoringAtt',   # Finalizacoes no gol FEITAS
            # (sofridas: calcular via seasonstats ou adversario)

            # === DEFESA ===
            'saves',            # Defesas do goleiro
            'totalClearance',   # Cortes/Afastamentos

            # === CARTOES ===
            'totalYellowCard',  # Cartoes amarelos RECEBIDOS
            'totalRedCard',     # Cartoes vermelhos RECEBIDOS

            # === FALTAS ===
            'fkFoulWon',        # Faltas SOFRIDAS (a favor)
            'fkFoulLost',       # Faltas COMETIDAS (contra)

            # === PENALTIS ===
            'penaltyConceded',  # Penaltis COMETIDOS
            'penaltyFaced',     # Penaltis ENFRENTADOS (goleiro)
            'penGoalsConceded', # Gols de penalti SOFRIDOS

            # === PASSES ===
            'totalPass',        # Passes totais
            'accuratePass',     # Passes certos
        ]

    # Coletar dados de cada partida
    all_stats: Dict[str, List[int]] = {stat: [] for stat in stats_to_analyze}
    matches_with_data = 0

    print(f"Analisando {len(match_ids)} partidas de {team_name}...")

    for i, match_id in enumerate(match_ids):
        stats = get_team_stats_from_match(match_id, team_id)
        if stats:
            matches_with_data += 1
            for stat_name in stats_to_analyze:
                if stat_name in stats:
                    all_stats[stat_name].append(stats[stat_name])
            print(f"  [{i+1}/{len(match_ids)}] {match_id[:12]}... OK")
        else:
            print(f"  [{i+1}/{len(match_ids)}] {match_id[:12]}... sem dados")

    # Calcular CV para cada estatistica
    report = TeamVariabilityReport(
        team_id=team_id,
        team_name=team_name,
        matches_analyzed=matches_with_data
    )

    for stat_name, values in all_stats.items():
        if len(values) >= 2:
            cv_result = calculate_cv(values, stat_name)
            if cv_result:
                report.statistics[stat_name] = cv_result

    return report


def print_variability_report(report: TeamVariabilityReport):
    """Imprime o relatorio de variabilidade formatado"""
    print("\n" + "=" * 70)
    print(f"RELATORIO DE VARIABILIDADE - {report.team_name}")
    print(f"Partidas analisadas: {report.matches_analyzed}")
    print("=" * 70)

    print("\n{:<25} {:>8} {:>8} {:>8} {:>15}".format(
        "Estatistica", "Media", "Desvio", "CV", "Classificacao"
    ))
    print("-" * 70)

    # Ordenar por CV (do mais estavel ao mais instavel)
    sorted_stats = sorted(
        report.statistics.values(),
        key=lambda x: x.cv
    )

    for stat in sorted_stats:
        print("{:<25} {:>8.2f} {:>8.2f} {:>8.3f} {:>15}".format(
            stat.name,
            stat.mean,
            stat.std_dev,
            stat.cv,
            stat.classification
        ))

    print("\n" + "-" * 70)
    print("LEGENDA:")
    print("  CV < 0.15: Muito Estavel | 0.15-0.30: Estavel | 0.30-0.50: Moderado")
    print("  CV 0.50-0.75: Instavel | CV > 0.75: Muito Instavel")
    print("=" * 70)

    # Resumo
    if report.statistics:
        avg_cv = statistics.mean([s.cv for s in report.statistics.values()])
        most_stable = min(report.statistics.values(), key=lambda x: x.cv)
        least_stable = max(report.statistics.values(), key=lambda x: x.cv)

        print(f"\nRESUMO:")
        print(f"  CV Medio do Time: {avg_cv:.3f} ({classify_cv(avg_cv)})")
        print(f"  Mais Estavel: {most_stable.name} (CV={most_stable.cv:.3f})")
        print(f"  Menos Estavel: {least_stable.name} (CV={least_stable.cv:.3f})")


def compare_teams_variability(
    reports: List[TeamVariabilityReport],
    stat_name: str
) -> None:
    """Compara a variabilidade de uma estatistica entre times"""
    print(f"\n{'='*60}")
    print(f"COMPARATIVO: {stat_name}")
    print(f"{'='*60}\n")

    comparisons = []
    for report in reports:
        if stat_name in report.statistics:
            stat = report.statistics[stat_name]
            comparisons.append((report.team_name, stat))

    # Ordenar por CV
    comparisons.sort(key=lambda x: x[1].cv)

    print("{:<20} {:>8} {:>8} {:>8} {:>15}".format(
        "Time", "Media", "Desvio", "CV", "Classificacao"
    ))
    print("-" * 60)

    for team_name, stat in comparisons:
        print("{:<20} {:>8.2f} {:>8.2f} {:>8.3f} {:>15}".format(
            team_name,
            stat.mean,
            stat.std_dev,
            stat.cv,
            stat.classification
        ))


def main():
    """Exemplo de uso: Calcular variabilidade do Arsenal"""

    # IDs de referencia
    ARSENAL_ID = "4dsgumo7d4zupm2ugsvm4zm4d"
    PREMIER_LEAGUE_2025_26 = "51r6ph2woavlbbpk8f29nynf8"

    # IDs de partidas conhecidas do Arsenal (para teste)
    # Em producao, usar get_match_ids_from_schedule ou get_match_ids_from_preview
    arsenal_match_ids = [
        "adxx1ue4e7h0i93pwl7xucr2s",  # Arsenal vs Everton
        "c3azlvd97gyv7x0unm43czw9g",  # Outra partida
        "a5sr0ba7amh9cuylpfu6pev4k",  # Outra partida
    ]

    print("=" * 70)
    print("CALCULO DE COEFICIENTE DE VARIACAO (CV)")
    print("VStats API - Analise de Estabilidade de Times")
    print("=" * 70)

    # Calcular variabilidade
    report = calculate_team_variability(
        team_id=ARSENAL_ID,
        team_name="Arsenal",
        match_ids=arsenal_match_ids
    )

    # Imprimir relatorio
    print_variability_report(report)

    # Exportar dados para uso externo
    print("\n\nDADOS PARA EXPORTACAO (JSON-like):")
    print("-" * 40)
    for name, stat in report.statistics.items():
        print(f'"{name}": {{"mean": {stat.mean:.2f}, "cv": {stat.cv:.3f}, "class": "{stat.classification}"}}')


if __name__ == "__main__":
    main()
