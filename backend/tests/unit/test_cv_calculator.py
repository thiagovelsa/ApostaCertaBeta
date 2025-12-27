"""
Testes do Calculador de CV
==========================

Testes para thresholds calibrados por tipo de estatistica e estabilidade.
"""

import pytest
from app.utils.cv_calculator import (
    calculate_cv,
    classify_cv,
    calculate_estabilidade,
    calculate_cv_from_matches,
)


class TestClassifyCV:
    """Testes para funcao classify_cv com thresholds genericos (fallback)"""

    def test_muito_estavel(self):
        """CV < 0.15 deve ser Muito Estavel (threshold generico)"""
        assert classify_cv(0.0) == "Muito Estável"
        assert classify_cv(0.10) == "Muito Estável"
        assert classify_cv(0.14) == "Muito Estável"

    def test_estavel(self):
        """CV entre 0.15 e 0.30 deve ser Estavel (threshold generico)"""
        assert classify_cv(0.15) == "Estável"
        assert classify_cv(0.20) == "Estável"
        assert classify_cv(0.29) == "Estável"

    def test_moderado(self):
        """CV entre 0.30 e 0.50 deve ser Moderado (threshold generico)"""
        assert classify_cv(0.30) == "Moderado"
        assert classify_cv(0.40) == "Moderado"
        assert classify_cv(0.49) == "Moderado"

    def test_instavel(self):
        """CV entre 0.50 e 0.75 deve ser Instavel (threshold generico)"""
        assert classify_cv(0.50) == "Instável"
        assert classify_cv(0.60) == "Instável"
        assert classify_cv(0.74) == "Instável"

    def test_muito_instavel(self):
        """CV >= 0.75 deve ser Muito Instavel (threshold generico)"""
        assert classify_cv(0.75) == "Muito Instável"
        assert classify_cv(1.0) == "Muito Instável"
        assert classify_cv(1.5) == "Muito Instável"


class TestClassifyCVCalibrado:
    """Testes para classify_cv com thresholds calibrados por estatistica"""

    def test_gols_thresholds_calibrados(self):
        """Gols tem thresholds maiores (Poisson, media baixa)"""
        # Gols: muito_estavel < 0.50, estavel < 0.70, moderado < 0.90, instavel < 1.10
        assert classify_cv(0.40, "gols") == "Muito Estável"
        assert classify_cv(0.60, "gols") == "Estável"
        assert classify_cv(0.80, "gols") == "Moderado"
        assert classify_cv(1.00, "gols") == "Instável"
        assert classify_cv(1.20, "gols") == "Muito Instável"

    def test_escanteios_thresholds_calibrados(self):
        """Escanteios tem thresholds intermediarios"""
        # Escanteios: muito_estavel < 0.25, estavel < 0.40, moderado < 0.55, instavel < 0.75
        assert classify_cv(0.20, "escanteios") == "Muito Estável"
        assert classify_cv(0.35, "escanteios") == "Estável"
        assert classify_cv(0.50, "escanteios") == "Moderado"
        assert classify_cv(0.70, "escanteios") == "Instável"
        assert classify_cv(0.80, "escanteios") == "Muito Instável"

    def test_finalizacoes_thresholds_calibrados(self):
        """Finalizacoes tem thresholds mais baixos (alta frequencia)"""
        # Finalizacoes: muito_estavel < 0.15, estavel < 0.25, moderado < 0.40, instavel < 0.55
        assert classify_cv(0.10, "finalizacoes") == "Muito Estável"
        assert classify_cv(0.20, "finalizacoes") == "Estável"
        assert classify_cv(0.35, "finalizacoes") == "Moderado"
        assert classify_cv(0.50, "finalizacoes") == "Instável"
        assert classify_cv(0.60, "finalizacoes") == "Muito Instável"

    def test_finalizacoes_gol_thresholds_calibrados(self):
        """Finalizacoes no gol tem thresholds intermediarios"""
        # finalizacoes_gol: muito_estavel < 0.30, estavel < 0.45, moderado < 0.60, instavel < 0.80
        assert classify_cv(0.25, "finalizacoes_gol") == "Muito Estável"
        assert classify_cv(0.40, "finalizacoes_gol") == "Estável"
        assert classify_cv(0.55, "finalizacoes_gol") == "Moderado"
        assert classify_cv(0.75, "finalizacoes_gol") == "Instável"
        assert classify_cv(0.85, "finalizacoes_gol") == "Muito Instável"

    def test_cartoes_amarelos_thresholds_calibrados(self):
        """Cartoes amarelos tem thresholds similares a gols"""
        # cartoes_amarelos: muito_estavel < 0.45, estavel < 0.65, moderado < 0.85, instavel < 1.05
        assert classify_cv(0.40, "cartoes_amarelos") == "Muito Estável"
        assert classify_cv(0.60, "cartoes_amarelos") == "Estável"
        assert classify_cv(0.80, "cartoes_amarelos") == "Moderado"
        assert classify_cv(1.00, "cartoes_amarelos") == "Instável"
        assert classify_cv(1.10, "cartoes_amarelos") == "Muito Instável"

    def test_faltas_thresholds_calibrados(self):
        """Faltas tem thresholds baixos (alta frequencia)"""
        # faltas: muito_estavel < 0.15, estavel < 0.25, moderado < 0.40, instavel < 0.55
        assert classify_cv(0.10, "faltas") == "Muito Estável"
        assert classify_cv(0.20, "faltas") == "Estável"
        assert classify_cv(0.35, "faltas") == "Moderado"
        assert classify_cv(0.50, "faltas") == "Instável"
        assert classify_cv(0.60, "faltas") == "Muito Instável"

    def test_cartoes_vermelhos_retorna_na(self):
        """Cartoes vermelhos nao tem CV calculavel - retorna N/A"""
        assert classify_cv(0.0, "cartoes_vermelhos") == "N/A"
        assert classify_cv(0.5, "cartoes_vermelhos") == "N/A"
        assert classify_cv(3.0, "cartoes_vermelhos") == "N/A"

    def test_stat_type_desconhecido_usa_fallback(self):
        """Tipo desconhecido usa thresholds genericos"""
        assert classify_cv(0.10, "estatistica_inexistente") == "Muito Estável"
        assert classify_cv(0.50, "estatistica_inexistente") == "Instável"


class TestCalculateEstabilidade:
    """Testes para funcao calculate_estabilidade"""

    def test_cv_zero_estabilidade_100(self):
        """CV = 0 deve dar estabilidade 100%"""
        assert calculate_estabilidade(0.0) == 100

    def test_cv_maximo_estabilidade_zero(self):
        """CV >= threshold instavel deve dar estabilidade 0%"""
        # Threshold generico instavel = 0.75
        assert calculate_estabilidade(0.75) == 0
        assert calculate_estabilidade(1.0) == 0

    def test_cv_intermediario(self):
        """CV intermediario deve dar estabilidade proporcional"""
        # CV = 0.375 (metade de 0.75) -> 50%
        assert calculate_estabilidade(0.375) == 50

    def test_estabilidade_com_stat_type_gols(self):
        """Estabilidade para gols usa threshold calibrado (instavel=1.10)"""
        # CV = 0 -> 100%
        assert calculate_estabilidade(0.0, "gols") == 100
        # CV = 1.10 (instavel para gols) -> 0%
        assert calculate_estabilidade(1.10, "gols") == 0
        # CV = 0.55 (metade) -> 50%
        assert calculate_estabilidade(0.55, "gols") == 50

    def test_estabilidade_com_stat_type_escanteios(self):
        """Estabilidade para escanteios usa threshold calibrado (instavel=0.75)"""
        assert calculate_estabilidade(0.0, "escanteios") == 100
        assert calculate_estabilidade(0.75, "escanteios") == 0
        # CV = 0.375 (metade) -> 50%
        assert calculate_estabilidade(0.375, "escanteios") == 50

    def test_estabilidade_sempre_entre_0_e_100(self):
        """Estabilidade nunca pode ser < 0 ou > 100"""
        assert calculate_estabilidade(0.0) == 100
        assert calculate_estabilidade(-0.1) == 100  # Negativo trata como 100
        assert calculate_estabilidade(2.0) == 0  # CV alto trata como 0


class TestCalculateCV:
    """Testes para funcao calculate_cv"""

    def test_valores_iguais_cv_zero(self):
        """Valores iguais devem ter CV = 0 e estabilidade = 100"""
        result = calculate_cv([2.0, 2.0, 2.0, 2.0])
        assert result is not None
        mean, cv, classification, estabilidade = result
        assert mean == 2.0
        assert cv == 0.0
        assert classification == "Muito Estável"
        assert estabilidade == 100

    def test_valores_variados(self):
        """Valores variados devem ter CV e estabilidade calculados"""
        result = calculate_cv([1.0, 2.0, 3.0, 4.0, 5.0])
        assert result is not None
        mean, cv, classification, estabilidade = result
        assert mean == 3.0
        assert 0.4 < cv < 0.6  # CV moderado
        assert 0 <= estabilidade <= 100

    def test_lista_vazia_retorna_none(self):
        """Lista vazia deve retornar None"""
        assert calculate_cv([]) is None

    def test_um_valor_retorna_none(self):
        """Lista com 1 valor deve retornar None"""
        assert calculate_cv([5.0]) is None

    def test_dois_valores_funciona(self):
        """Lista com 2 valores deve funcionar"""
        result = calculate_cv([1.0, 3.0])
        assert result is not None
        mean, cv, classification, estabilidade = result
        assert mean == 2.0
        assert cv > 0
        assert 0 <= estabilidade <= 100

    def test_valores_com_none_filtrados(self):
        """Valores None devem ser filtrados"""
        result = calculate_cv([1.0, None, 3.0, None, 5.0])
        assert result is not None
        mean, cv, classification, estabilidade = result
        assert mean == 3.0

    def test_media_zero_cv_zero(self):
        """Se media for zero, CV deve ser zero"""
        result = calculate_cv([0.0, 0.0, 0.0])
        assert result is not None
        mean, cv, classification, estabilidade = result
        assert mean == 0.0
        assert cv == 0.0
        assert estabilidade == 100

    def test_calculate_cv_com_stat_type(self):
        """calculate_cv com stat_type usa thresholds calibrados"""
        # Valores com CV ~0.60 seriam Instavel no generico, mas Estavel para gols
        result = calculate_cv([1.0, 2.0, 1.0, 2.0], "gols")
        assert result is not None
        mean, cv, classification, estabilidade = result
        assert mean == 1.5
        # CV para esses valores eh ~0.47, que para gols eh "Muito Estavel" (< 0.50)
        assert classification == "Muito Estável"


class TestCalculateCVFromMatches:
    """Testes para funcao calculate_cv_from_matches"""

    def test_extrai_valores_de_matches(self):
        """Deve extrair valores de lista de dicionarios"""
        matches = [
            {"goals": 2, "corners": 5},
            {"goals": 1, "corners": 6},
            {"goals": 3, "corners": 4},
        ]
        result = calculate_cv_from_matches(matches, "goals", "gols")
        assert result is not None
        mean, cv, classification, estabilidade = result
        assert mean == 2.0
        assert 0 <= estabilidade <= 100

    def test_matches_vazios_retorna_none(self):
        """Lista vazia deve retornar None"""
        assert calculate_cv_from_matches([], "goals") is None

    def test_chave_inexistente_retorna_none(self):
        """Chave que nao existe nos dicts deve retornar None"""
        matches = [{"goals": 2}, {"goals": 1}]
        result = calculate_cv_from_matches(matches, "corners")
        assert result is None

    def test_valores_invalidos_ignorados(self):
        """Valores nao numericos devem ser ignorados"""
        matches = [
            {"goals": 2},
            {"goals": "invalid"},
            {"goals": 3},
        ]
        result = calculate_cv_from_matches(matches, "goals")
        assert result is not None
        mean, _, _, _ = result
        assert mean == 2.5  # (2 + 3) / 2


class TestDiferencaThresholds:
    """Testes que demonstram a diferenca entre thresholds calibrados"""

    def test_mesmo_cv_classificacao_diferente_por_tipo(self):
        """Mesmo CV pode ter classificacao diferente dependendo do tipo"""
        cv = 0.50

        # Generico: CV 0.50 = Instavel
        assert classify_cv(cv) == "Instável"

        # Gols: CV 0.50 = Muito Estavel (threshold muito_estavel = 0.50)
        # Na verdade, 0.50 == threshold, entao vai para o proximo
        assert classify_cv(cv, "gols") == "Estável"

        # Finalizacoes: CV 0.50 = Instavel (threshold instavel = 0.55)
        assert classify_cv(cv, "finalizacoes") == "Instável"

    def test_cv_alto_gols_vs_escanteios(self):
        """CV 0.85 e instavel para gols mas muito instavel para escanteios"""
        cv = 0.85

        # Gols: moderado < 0.90, entao 0.85 = Moderado
        assert classify_cv(cv, "gols") == "Moderado"

        # Escanteios: instavel < 0.75, entao 0.85 = Muito Instavel
        assert classify_cv(cv, "escanteios") == "Muito Instável"
