"""
Testes do Calculador de CV
==========================
"""

import pytest
from app.utils.cv_calculator import calculate_cv, classify_cv


class TestClassifyCV:
    """Testes para funcao classify_cv"""

    def test_muito_estavel(self):
        """CV < 0.15 deve ser Muito Estavel"""
        assert classify_cv(0.0) == "Muito Estável"
        assert classify_cv(0.10) == "Muito Estável"
        assert classify_cv(0.14) == "Muito Estável"

    def test_estavel(self):
        """CV entre 0.15 e 0.30 deve ser Estavel"""
        assert classify_cv(0.15) == "Estável"
        assert classify_cv(0.20) == "Estável"
        assert classify_cv(0.29) == "Estável"

    def test_moderado(self):
        """CV entre 0.30 e 0.50 deve ser Moderado"""
        assert classify_cv(0.30) == "Moderado"
        assert classify_cv(0.40) == "Moderado"
        assert classify_cv(0.49) == "Moderado"

    def test_instavel(self):
        """CV entre 0.50 e 0.75 deve ser Instavel"""
        assert classify_cv(0.50) == "Instável"
        assert classify_cv(0.60) == "Instável"
        assert classify_cv(0.74) == "Instável"

    def test_muito_instavel(self):
        """CV >= 0.75 deve ser Muito Instavel"""
        assert classify_cv(0.75) == "Muito Instável"
        assert classify_cv(1.0) == "Muito Instável"
        assert classify_cv(1.5) == "Muito Instável"


class TestCalculateCV:
    """Testes para funcao calculate_cv"""

    def test_valores_iguais_cv_zero(self):
        """Valores iguais devem ter CV = 0"""
        result = calculate_cv([2.0, 2.0, 2.0, 2.0])
        assert result is not None
        mean, cv, classification = result
        assert mean == 2.0
        assert cv == 0.0
        assert classification == "Muito Estável"

    def test_valores_variados(self):
        """Valores variados devem ter CV calculado"""
        result = calculate_cv([1.0, 2.0, 3.0, 4.0, 5.0])
        assert result is not None
        mean, cv, classification = result
        assert mean == 3.0
        assert 0.4 < cv < 0.6  # CV moderado

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
        mean, cv, _ = result
        assert mean == 2.0
        assert cv > 0

    def test_valores_com_none_filtrados(self):
        """Valores None devem ser filtrados"""
        result = calculate_cv([1.0, None, 3.0, None, 5.0])
        assert result is not None
        mean, _, _ = result
        assert mean == 3.0

    def test_media_zero_cv_zero(self):
        """Se media for zero, CV deve ser zero"""
        result = calculate_cv([0.0, 0.0, 0.0])
        assert result is not None
        mean, cv, _ = result
        assert mean == 0.0
        assert cv == 0.0
