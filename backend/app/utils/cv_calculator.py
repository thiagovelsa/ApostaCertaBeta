"""
Calculador de Coeficiente de Variacao (CV)
==========================================

O Coeficiente de Variacao mede a estabilidade/consistencia de uma estatistica.
Quanto mais proximo de 0, mais estavel. Quanto mais proximo de 1+, mais instavel.

Formula: CV = Desvio Padrao / Media

ESCALA DE INTERPRETACAO:
  0.00 - 0.15: Muito Estavel (time muito consistente)
  0.15 - 0.30: Estavel (time consistente)
  0.30 - 0.50: Moderado (variacao normal)
  0.50 - 0.75: Instavel (time inconsistente)
  0.75+      : Muito Instavel (resultados imprevisiveis)
"""

import statistics
from typing import List, Optional, Tuple

from .constants import CV_THRESHOLDS


def classify_cv(cv: float) -> str:
    """
    Classifica o CV em categorias de estabilidade.

    Args:
        cv: Coeficiente de Variacao calculado

    Returns:
        String com a classificacao (Muito Estavel, Estavel, etc.)
    """
    if cv < CV_THRESHOLDS["muito_estavel"]:
        return "Muito Estável"
    elif cv < CV_THRESHOLDS["estavel"]:
        return "Estável"
    elif cv < CV_THRESHOLDS["moderado"]:
        return "Moderado"
    elif cv < CV_THRESHOLDS["instavel"]:
        return "Instável"
    else:
        return "Muito Instável"


def calculate_cv(values: List[float]) -> Optional[Tuple[float, float, str]]:
    """
    Calcula o Coeficiente de Variacao para uma lista de valores.

    Args:
        values: Lista de valores numericos (ex: gols por partida)

    Returns:
        Tuple (media, cv, classificacao) ou None se menos de 2 valores

    Example:
        >>> calculate_cv([2, 1, 3, 2, 1])
        (1.8, 0.44, "Moderado")
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

    classification = classify_cv(cv)

    return (round(mean, 2), round(cv, 2), classification)


def calculate_cv_from_matches(
    matches_data: List[dict],
    stat_key: str,
) -> Optional[Tuple[float, float, str]]:
    """
    Calcula CV a partir de dados de partidas.

    Args:
        matches_data: Lista de dicionarios com dados das partidas
        stat_key: Chave da estatistica a calcular (ex: 'goals', 'wonCorners')

    Returns:
        Tuple (media, cv, classificacao) ou None
    """
    values = []

    for match in matches_data:
        value = match.get(stat_key)
        if value is not None:
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                continue

    return calculate_cv(values)
