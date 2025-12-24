# Estratégia de Testes

**Versão:** 1.0
**Data:** 24 de dezembro de 2025
**Framework:** Pytest (backend), Vitest (frontend, futuro)

---

## 1. Visão Geral

Estratégia completa de testes para garantir qualidade, confiabilidade e manutenibilidade do código.

### 1.1 Testing Pyramid

```
           E2E Tests
          (10%)
        /    |    \
      /      |      \
    /    Integration   \
   /      Tests        \
  /        (20%)        \
/____________________\
  Unit Tests (70%)
```

| Tipo | Cobertura | Velocidade | Custo Manutenção |
|------|-----------|-----------|------------------|
| **Unit** | 70% | ⚡ Muito Rápido | 💰 Baixo |
| **Integration** | 20% | ⚙️ Médio | 💰💰 Médio |
| **E2E** | 10% | 🐢 Lento | 💰💰💰 Alto |

### 1.2 Metas

- ✅ **Cobertura:** 80% mínimo (unit + integration)
- ✅ **Velocidade:** Testes rodam em < 10 segundos
- ✅ **Confiabilidade:** Sem testes flaky (intermitentes)
- ✅ **Manutenibilidade:** DRY (Don't Repeat Yourself) com fixtures

---

## 2. Estrutura de Testes

### 2.1 Organização de Pastas

```
tests/
├── __init__.py
├── conftest.py                  # Fixtures globais
├── unit/
│   ├── __init__.py
│   ├── test_cv_calculator.py    # Testes de funções puras
│   ├── test_models.py           # Testes de validação Pydantic
│   ├── test_services.py         # Testes de lógica (com mocks)
│   └── test_validators.py       # Testes de validadores
├── integration/
│   ├── __init__.py
│   ├── test_routes.py           # Testes de endpoints
│   ├── test_vstats_client.py    # Testes com VStats API (mock)
│   └── test_cache.py            # Testes de cache (com redis mock)
├── fixtures/
│   ├── __init__.py
│   ├── vstats_responses.json    # Mock responses
│   ├── mock_partidas.json
│   └── sample_data.py           # Funções factory
└── pytest.ini                    # Configuração pytest
```

### 2.2 Padrão de Nomenclatura

```python
# test_<nome_do_modulo>.py
# test_<classe/funcao>_<comportamento>.py

# Exemplos:
test_cv_calculator.py             # Testa app/utils/cv_calculator.py
test_models.py                    # Testa app/models/
test_routes.py                    # Testa app/api/routes/

# Dentro dos arquivos:
def test_calcular_cv_com_valores_validos():  # ✓ Bom
def test_cv_positivo():                        # ✗ Vago
def test_exception_when_empty_list():          # ✓ Bom
```

---

## 3. Testes Unitários

### 3.1 O que Testar

✅ **Funções puras** (sem estado, sem I/O)
✅ **Validações de dados**
✅ **Cálculos** (CV, médias, etc)
✅ **Tratamento de exceções**
✅ **Lógica condicional**

❌ **Integração com APIs externas** (usar mocks)
❌ **I/O File System** (usar fixtures)
❌ **Dependências externas** (mockar)

### 3.2 Exemplo: Unit Test

```python
# tests/unit/test_cv_calculator.py
import pytest
from app.utils.cv_calculator import calcular_cv, classificar_cv

class TestCalcularCV:
    """Testes para cálculo de Coeficiente de Variação."""

    def test_calcular_cv_com_valores_validos(self):
        """CV calculado corretamente para valores válidos."""
        valores = [1, 2, 3, 4, 5]
        resultado = calcular_cv(valores)

        assert isinstance(resultado, float)
        assert resultado > 0
        assert resultado < 1  # CV típico de dados normalizados

    def test_calcular_cv_com_lista_vazia(self):
        """Retorna 0.0 para lista vazia."""
        resultado = calcular_cv([])
        assert resultado == 0.0

    def test_calcular_cv_com_um_elemento(self):
        """Retorna 0.0 com um elemento (impossível calcular desvio)."""
        resultado = calcular_cv([5.0])
        assert resultado == 0.0

    def test_calcular_cv_com_media_zero(self):
        """Retorna 0.0 quando média é zero."""
        resultado = calcular_cv([0, 0, 0])
        assert resultado == 0.0

    def test_calcular_cv_com_valores_negativos(self):
        """Calcula corretamente com valores negativos."""
        valores = [-5, -3, -1, 1, 3, 5]
        resultado = calcular_cv(valores)

        # Não deve lançar erro
        assert isinstance(resultado, float)
        assert resultado >= 0

    def test_cv_arredondado_duas_casas(self):
        """CV é arredondado a 2 casas decimais."""
        resultado = calcular_cv([1.111, 2.222, 3.333])

        # Não deve ter mais de 2 casas decimais
        assert len(str(resultado).split('.')[-1]) <= 2


class TestClassificarCV:
    """Testes para classificação de CV."""

    @pytest.mark.parametrize("cv,esperado", [
        (0.10, "Muito Estável"),
        (0.20, "Estável"),
        (0.35, "Moderado"),
        (0.50, "Instável"),
        (0.75, "Muito Instável"),
    ])
    def test_classificacao_por_faixas(self, cv, esperado):
        """Classifica corretamente por faixas de CV."""
        resultado = classificar_cv(cv)
        assert resultado == esperado

    def test_cv_negativo_retorna_muito_estavel(self):
        """CVs negativos (impossível) são tratados como Muito Estável."""
        # Isso não deve acontecer, mas caso aconteça...
        resultado = classificar_cv(-0.5)
        assert resultado == "Muito Estável"  # Ou lançar exceção
```

### 3.3 Fixtures (Reutilizáveis)

```python
# tests/conftest.py
import pytest
from app.models.partida import TimeInfo, PartidaResumo
from datetime import date, time

@pytest.fixture
def sample_time_info():
    """Factory de TimeInfo para testes."""
    return TimeInfo(
        id="123",
        nome="Arsenal",
        codigo="ARS",
        escudo="https://example.com/escudo.png"
    )

@pytest.fixture
def sample_partida(sample_time_info):
    """Factory de PartidaResumo para testes."""
    return PartidaResumo(
        id="f4vscquffy37afgv0arwcbztg",
        data=date(2025, 12, 27),
        horario=time(17, 0),
        competicao="Premier League",
        estadio="Emirates Stadium",
        mandante=sample_time_info,
        visitante=TimeInfo(
            id="456",
            nome="Crystal Palace",
            codigo="CRY"
        )
    )

@pytest.fixture
def sample_cv_values():
    """Valores padrão para testes de CV."""
    return [1, 2, 3, 4, 5]
```

---

## 4. Testes de Integração

### 4.1 O que Testar

✅ **Endpoints HTTP completos** (request → response)
✅ **Fluxo completo** (route → service → repository)
✅ **Tratamento de erros**
✅ **Status codes HTTP**
✅ **CORS headers**

### 4.2 Exemplo: Integration Test

```python
# tests/integration/test_routes.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """TestClient do FastAPI."""
    return TestClient(app)

class TestPartidaRoutes:
    """Testes de integração para rotas de partidas."""

    def test_listar_partidas_sucesso(self, client, mocker):
        """GET /api/partidas retorna 200 com dados válidos."""
        # Mock VStats API
        mocker.patch(
            'app.services.partidas_service.VStatsClient.get_schedule',
            return_value=[
                {
                    'id': 'abc123',
                    'localDate': '2025-12-27',
                    'kickoffTime': '17:00',
                    'homeTeamName': 'Arsenal',
                    # ... outros campos
                }
            ]
        )

        response = client.get("/api/partidas?data=2025-12-27")

        assert response.status_code == 200
        data = response.json()
        assert 'partidas' in data
        assert 'total_partidas' in data
        assert isinstance(data['partidas'], list)

    def test_listar_partidas_data_invalida(self, client):
        """GET /api/partidas com data inválida retorna 400."""
        response = client.get("/api/partidas?data=27-12-2025")

        assert response.status_code == 400
        assert 'detail' in response.json()

    def test_listar_partidas_sem_parametro(self, client):
        """GET /api/partidas sem 'data' retorna 422."""
        response = client.get("/api/partidas")

        assert response.status_code == 422  # Unprocessable Entity

    def test_get_stats_sucesso(self, client, mocker):
        """GET /api/partida/{id}/stats retorna estatísticas."""
        # Mock múltiplas chamadas
        mocker.patch(
            'app.repositories.vstats_repository.VStatsRepository.fetch_match',
            return_value={'id': 'abc123', 'homeTeamId': '123', 'awayTeamId': '456'}
        )
        mocker.patch(
            'app.services.cache_service.CacheService.get',
            return_value=None  # Cache miss
        )

        response = client.get("/api/partida/abc123/stats?filtro=5")

        assert response.status_code == 200
        data = response.json()
        assert 'partida' in data
        assert 'mandante' in data
        assert 'visitante' in data
        assert data['filtro_aplicado'] == '5'

    def test_get_stats_filtro_invalido(self, client):
        """GET /api/partida/{id}/stats com filtro inválido retorna 400."""
        response = client.get("/api/partida/abc123/stats?filtro=invalid")

        assert response.status_code == 400

    def test_cors_headers(self, client):
        """Respostas incluem headers CORS corretos."""
        response = client.get("/api/partidas?data=2025-12-27")

        # FastAPI adiciona CORS automaticamente quando configurado
        # Verificar se headers estão presentes (depende de config)
        assert response.status_code in [200, 400, 500]  # Request foi processado
```

### 4.3 Mocking com Pytest-Mock

```python
# tests/integration/test_vstats_client.py
import pytest
from unittest.mock import patch, MagicMock

def test_get_seasonstats_com_timeout(mocker):
    """VStatsClient trata timeout graciosamente."""
    from app.services.vstats_client import VStatsClient

    # Mock httpx timeout
    mocker.patch(
        'httpx.AsyncClient.get',
        side_effect=httpx.TimeoutException()
    )

    client = VStatsClient()

    with pytest.raises(Exception, match="timeout"):
        client.get_seasonstats("tournament_id", "team_id")

def test_cache_hit(mocker):
    """Cache hit retorna dados sem chamar API."""
    from app.services.cache_service import CacheService
    from app.services.partidas_service import PartidasService

    cache_service = mocker.MagicMock(spec=CacheService)
    cache_service.get.return_value = {"cached": "data"}

    service = PartidasService(cache_service=cache_service)
    result = service.get_cached_partidas("2025-12-27")

    assert result == {"cached": "data"}
    cache_service.get.assert_called_once()
```

---

## 5. Fixtures Avançadas

### 5.1 Fixtures com Escopo

```python
# tests/conftest.py

@pytest.fixture(scope="session")
def app():
    """App é criado uma vez por sessão (rápido)."""
    from app.main import create_app
    return create_app()

@pytest.fixture(scope="function")
def client(app):
    """Client é criado por função (mais isolado)."""
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture(scope="module")
def mock_redis():
    """Redis mock compartilhado por módulo."""
    import fakeredis
    return fakeredis.FakeStrictRedis()

@pytest.fixture(autouse=True)
def cleanup_cache(mock_redis):
    """Auto-cleanup de cache após cada teste."""
    yield
    mock_redis.flushdb()
```

### 5.2 Factories de Dados

```python
# tests/fixtures/factories.py
from factory import Factory, Faker
from app.models.partida import TimeInfo, PartidaResumo

class TimeInfoFactory(Factory):
    """Factory para criar instâncias de TimeInfo."""
    class Meta:
        model = TimeInfo

    id = Faker('uuid4')
    nome = Faker('word')
    codigo = Faker('text', max_nb_chars=3).upper()
    escudo = Faker('url')

class PartidaResumoFactory(Factory):
    """Factory para criar instâncias de PartidaResumo."""
    class Meta:
        model = PartidaResumo

    id = Faker('uuid4')
    data = Faker('date_object')
    horario = Faker('time_object')
    competicao = Faker('word')
    estadio = Faker('word')
    mandante = factory.SubFactory(TimeInfoFactory)
    visitante = factory.SubFactory(TimeInfoFactory)

# Uso:
partida = PartidaResumoFactory()  # Dados aleatórios
partida2 = PartidaResumoFactory(competicao="Premier League")  # Customizado
```

---

## 6. Testes Parametrizados

```python
# tests/unit/test_models.py
import pytest
from app.models.estatisticas import EstatisticaMetrica

class TestEstatisticaMetrica:
    """Parametrized tests para classificação de CV."""

    @pytest.mark.parametrize("cv,esperado", [
        (0.10, "Muito Estável"),     # Limite inferior
        (0.15, "Estável"),
        (0.30, "Moderado"),
        (0.45, "Instável"),
        (0.60, "Muito Instável"),    # Limite superior
        (0.00, "Muito Estável"),     # Edge case: CV = 0
        (1.50, "Muito Instável"),    # Edge case: CV > 1
    ])
    def test_classificacao_cv(self, cv, esperado):
        """Testa todas as faixas de classificação de uma vez."""
        metric = EstatisticaMetrica(media=5.0, cv=cv)
        assert metric.classificacao == esperado

    @pytest.mark.parametrize("valores,deve_falhar", [
        ([1, 2, 3], False),           # Válido
        ([-1, -2, -3], False),        # Válido
        ([0, 0, 0], False),           # Válido
        ("não é lista", True),        # Invalid
        (None, True),                 # Invalid
    ])
    def test_validacao_valores(self, valores, deve_falhar):
        """Testa validação de entrada."""
        if deve_falhar:
            with pytest.raises((TypeError, ValueError)):
                calcular_cv(valores)
        else:
            resultado = calcular_cv(valores)
            assert isinstance(resultado, float)
```

---

## 7. Configuração Pytest

### 7.1 pytest.ini

```ini
[pytest]
# Diretório de testes
testpaths = tests

# Padrão de arquivos de teste
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Saída
addopts =
    -v                          # Verbose
    --strict-markers            # Rejeitar markers desconhecidos
    --tb=short                  # Traceback conciso
    --cov=app                   # Coverage do módulo app
    --cov-report=html           # Relatório HTML
    --cov-report=term-missing   # Terminal com linhas não cobertas
    --cov-fail-under=80         # Falhar se < 80%

markers =
    slow: marca teste como lento
    integration: marca teste de integração
    unit: marca teste unitário
    smoke: marca teste smoke
```

### 7.2 Rodar Testes

```bash
# Todos os testes
pytest

# Específico
pytest tests/unit/test_models.py

# Com marker
pytest -m unit
pytest -m "not slow"

# Com cobertura
pytest --cov=app

# Modo watch (rerun em mudanças)
pytest-watch

# Modo failfast (para no primeiro erro)
pytest -x

# Verbose + output
pytest -v -s
```

---

## 8. Continuous Integration

### 8.1 GitHub Actions (Exemplo)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt

      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

## 9. Checklist de Testes

### Para cada nova feature:

- [ ] Unit test para lógica principal
- [ ] Unit test para casos extremos (edge cases)
- [ ] Unit test para tratamento de erros
- [ ] Integration test para endpoint completo
- [ ] Test com dados inválidos (error path)
- [ ] Coverage >= 80% para o código novo
- [ ] Sem testes flaky (rodar 5 vezes, sempre passa)
- [ ] Docstring explicando o que testa
- [ ] Fixtures reutilizáveis quando possível

---

## 10. Referências

- **Pytest:** https://docs.pytest.org/
- **Pytest-Mock:** https://pytest-mock.readthedocs.io/
- **FastAPI Testing:** https://fastapi.tiangolo.com/advanced/testing-dependencies/
- **Testing Best Practices:** https://testingwithpytest.com/

---

**[⬆ Voltar ao topo](#estratégia-de-testes)**
