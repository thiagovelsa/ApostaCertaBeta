"""
Calculador de Coeficiente de Variacao (CV)
==========================================

O Coeficiente de Variacao mede a estabilidade/consistencia de uma estatistica.
Quanto mais proximo de 0, mais estavel. Quanto mais proximo de 1+, mais instavel.

Formula: CV = Desvio Padrao / Media

ESCALA CALIBRADA POR ESTATISTICA:
  Cada tipo de estatistica tem thresholds proprios baseados na sua
  distribuicao natural (Poisson para eventos discretos, Normal para contagens).

  Exemplo para GOLS (media ~1.5, Poisson):
    CV < 0.50: Muito Estavel
    CV < 0.70: Estavel
    CV < 0.90: Moderado
    CV < 1.10: Instavel
    CV >= 1.10: Muito Instavel

ESTABILIDADE:
  Visualizacao invertida: Estabilidade = 100 - (CV * 100)
  Onde 100% = muito estavel, 0% = muito instavel
"""

import statistics
from typing import List, Optional, Tuple

from .constants import CV_THRESHOLDS, CV_THRESHOLDS_BY_STAT


def classify_cv(cv: float, stat_type: Optional[str] = None) -> str:
    """
    Classifica o CV em categorias de estabilidade.

    Args:
        cv: Coeficiente de Variacao calculado
        stat_type: Tipo da estatistica para usar thresholds calibrados
                   (gols, escanteios, finalizacoes, etc.)

    Returns:
        String com a classificacao (Muito Estavel, Estavel, etc.)
        Retorna "N/A" se stat_type nao tiver thresholds (ex: cartoes_vermelhos)
    """
    # Busca thresholds especificos ou usa fallback
    thresholds = CV_THRESHOLDS
    if stat_type:
        specific = CV_THRESHOLDS_BY_STAT.get(stat_type)
        if specific is None and stat_type in CV_THRESHOLDS_BY_STAT:
            # Estatistica sem CV (ex: cartoes_vermelhos)
            return "N/A"
        if specific:
            thresholds = specific

    if cv < thresholds["muito_estavel"]:
        return "Muito Estável"
    elif cv < thresholds["estavel"]:
        return "Estável"
    elif cv < thresholds["moderado"]:
        return "Moderado"
    elif cv < thresholds["instavel"]:
        return "Instável"
    else:
        return "Muito Instável"


def calculate_estabilidade(cv: float, stat_type: Optional[str] = None) -> int:
    """
    Calcula a estabilidade em porcentagem (0-100%).

    Estabilidade e a visualizacao invertida do CV:
    - 100% = muito estavel (CV baixo)
    - 0% = muito instavel (CV alto)

    Args:
        cv: Coeficiente de Variacao calculado
        stat_type: Tipo da estatistica para normalizar

    Returns:
        Estabilidade em porcentagem (0-100)
    """
    # Normaliza baseado no threshold de instavel (100% = 0, 0% = instavel)
    thresholds = CV_THRESHOLDS
    if stat_type:
        specific = CV_THRESHOLDS_BY_STAT.get(stat_type)
        if specific:
            thresholds = specific

    # Escala: CV=0 -> 100%, CV=instavel -> 0%
    max_cv = thresholds.get("instavel", 0.75)
    estabilidade = max(0, min(100, int(100 * (1 - cv / max_cv))))
    return estabilidade


def calculate_cv(
    values: List[float],
    stat_type: Optional[str] = None,
) -> Optional[Tuple[float, float, str, int]]:
    """
    Calcula o Coeficiente de Variacao para uma lista de valores.

    Args:
        values: Lista de valores numericos (ex: gols por partida)
        stat_type: Tipo da estatistica para thresholds calibrados

    Returns:
        Tuple (media, cv, classificacao, estabilidade) ou None se menos de 2 valores

    Example:
        >>> calculate_cv([2, 1, 3, 2, 1], "gols")
        (1.8, 0.44, "Muito Estável", 60)
    """
    if len(values) < 2:
        return None

    # Filtra valores None ou negativos
    clean_values = [v for v in values if v is not None and v >= 0]

    if len(clean_values) < 2:
        return None

    mean = statistics.mean(clean_values)
    std_dev = statistics.stdev(clean_values)

    # CV = Desvio Padrao / Media (evita divisao por zero)
    cv = std_dev / mean if mean > 0 else 0.0

    classification = classify_cv(cv, stat_type)
    estabilidade = calculate_estabilidade(cv, stat_type)

    return (round(mean, 2), round(cv, 2), classification, estabilidade)


def calculate_cv_from_matches(
    matches_data: List[dict],
    stat_key: str,
    stat_type: Optional[str] = None,
) -> Optional[Tuple[float, float, str, int]]:
    """
    Calcula CV a partir de dados de partidas.

    Args:
        matches_data: Lista de dicionarios com dados das partidas
        stat_key: Chave da estatistica a calcular (ex: 'goals', 'wonCorners')
        stat_type: Tipo da estatistica para thresholds calibrados

    Returns:
        Tuple (media, cv, classificacao, estabilidade) ou None
    """
    values = []

    for match in matches_data:
        value = match.get(stat_key)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                continue

    return calculate_cv(values, stat_type)
