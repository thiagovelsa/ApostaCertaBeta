# Testes - Documentação

**Versão:** 1.0
**Data:** 24 de dezembro de 2025
**Framework:** Pytest

---

## 1. Visão Geral

Esta pasta contém todos os testes automatizados do sistema. Os testes são organizados em **Unit** e **Integration** tests com objetivo de manter qualidade, confiabilidade e facilitar manutenção.

### 1.1 Estrutura

```
tests/
├── __init__.py
├── conftest.py                  # Fixtures compartilhadas
├── pytest.ini                    # Configuração do pytest
├── unit/                         # Testes unitários (70%)
│   ├── __init__.py
│   ├── test_cv_calculator.py    # Testes de cálculos
│   ├── test_models.py           # Testes de validação Pydantic
│   ├── test_services.py         # Testes de lógica (com mocks)
│   └── test_validators.py       # Testes de validadores customizados
├── integration/                  # Testes de integração (20%)
│   ├── __init__.py
│   ├── test_routes.py           # Testes de endpoints HTTP
│   ├── test_vstats_client.py    # Testes de cliente VStats (mock)
│   ├── test_cache.py            # Testes de cache Redis (mock)
│   └── test_end_to_end.py       # Testes de fluxo completo
└── fixtures/                     # Dados mock e factories
    ├── __init__.py
    ├── vstats_responses.json    # Respostas mock da VStats API
    ├── mock_partidas.json       # Dados de exemplo
    └── factories.py             # Factories para criar dados
```

---

## 2. Rodando Testes

### 2.1 Rápido Start

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=app

# Verboso
pytest -v -s

# Apenas unit tests
pytest tests/unit/

# Apenas integration tests
pytest tests/integration/

# Teste específico
pytest tests/unit/test_cv_calculator.py::TestCalcularCV::test_calcular_cv_com_valores_validos
```

### 2.2 Opções Comuns

| Opção | Descrição | Exemplo |
|-------|-----------|---------|
| `-v` | Verbose (mostra cada teste) | `pytest -v` |
| `-s` | Sem captura de output (mostra prints) | `pytest -s` |
| `-x` | Para no primeiro erro | `pytest -x` |
| `-k` | Filtra por nome | `pytest -k "cv"` |
| `--lf` | Roda último falho | `pytest --lf` |
| `--ff` | Falhos primeiro | `pytest --ff` |
| `-m` | Por marker | `pytest -m "unit"` |
| `--cov` | Cobertura | `pytest --cov=app` |
| `--pdb` | Debugger ao falhar | `pytest --pdb` |

### 2.3 Executar Testes Específicos

```bash
# Por arquivo
pytest tests/unit/test_models.py

# Por classe
pytest tests/unit/test_models.py::TestTimeInfo

# Por função
pytest tests/unit/test_models.py::TestTimeInfo::test_time_info_valido

# Por padrão
pytest -k "cv"              # Tudo com "cv" no nome
pytest -k "not slow"        # Exclui testes "slow"
pytest -k "test_get and not cache"
```

---

## 3. Estrutura de um Teste

### 3.1 Teste Unitário

```python
# tests/unit/test_example.py
import pytest
from app.utils.cv_calculator import calcular_cv

class TestCalcularCV:
    """Agrupa testes relacionados em uma classe."""

    def test_caso_de_sucesso(self):
        """Nome descreve o que testa."""
        # ARRANGE - Preparar dados
        valores = [1, 2, 3, 4, 5]

        # ACT - Executar função
        resultado = calcular_cv(valores)

        # ASSERT - Verificar resultado
        assert resultado > 0
        assert isinstance(resultado, float)

    def test_tratamento_de_erro(self):
        """Testa lançamento de exceção."""
        with pytest.raises(ValueError, match="não pode ser vazio"):
            calcular_cv([])

    @pytest.mark.skip(reason="Implementação pendente")
    def test_futuro(self):
        """Testes para features futuras."""
        pass
```

### 3.2 Teste de Integração

```python
# tests/integration/test_routes.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestPartidaRoutes:
    """Testes de endpoints de partidas."""

    def test_get_partidas_com_data_valida(self, client, mocker):
        """GET /api/partidas retorna 200 com dados válidos."""
        # Mock API externa
        mocker.patch(
            'app.services.partidas_service.VStatsClient.get_schedule',
            return_value=[{"id": "123", "localDate": "2025-12-27"}]
        )

        response = client.get("/api/partidas?data=2025-12-27")

        assert response.status_code == 200
        data = response.json()
        assert "partidas" in data
        assert data["total_partidas"] >= 0

    def test_get_partidas_com_data_invalida(self, client):
        """GET /api/partidas com data inválida retorna 400."""
        response = client.get("/api/partidas?data=invalid")

        assert response.status_code == 400
```

---

## 4. Fixtures

### 4.1 Fixtures Básicas

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """TestClient para testar endpoints HTTP."""
    return TestClient(app)

@pytest.fixture
def sample_cv_values():
    """Valores padrão para testes de CV."""
    return [1, 2, 3, 4, 5]

@pytest.fixture
def sample_partida():
    """PartidaResumo para testes."""
    from app.models.partida import PartidaResumo, TimeInfo
    from datetime import date, time

    return PartidaResumo(
        id="f4vscquffy37afgv0arwcbztg",
        data=date(2025, 12, 27),
        horario=time(17, 0),
        competicao="Premier League",
        estadio="Emirates Stadium",
        mandante=TimeInfo(id="123", nome="Arsenal", codigo="ARS"),
        visitante=TimeInfo(id="456", nome="Crystal Palace", codigo="CRY")
    )
```

### 4.2 Usar Fixtures nos Testes

```python
# Fixture é injetada como parâmetro
def test_endpoint(client):  # client é a fixture
    response = client.get("/api/competicoes")
    assert response.status_code == 200

def test_calculo(sample_cv_values):  # sample_cv_values é a fixture
    resultado = calcular_cv(sample_cv_values)
    assert resultado > 0

# Múltiplas fixtures
def test_com_multiplas(client, sample_partida):
    assert client is not None
    assert sample_partida.id is not None
```

### 4.3 Fixtures com Autouse

```python
@pytest.fixture(autouse=True)
def reset_cache():
    """Limpa cache antes de cada teste."""
    import redis
    r = redis.Redis()
    r.flushdb()
    yield  # Teste roda aqui
    r.flushdb()  # Cleanup após teste
```

---

## 5. Mocking e Patching

### 5.1 Mock com Pytest-Mock

```python
def test_com_mock(mocker):
    """Mock para evitar chamar APIs externas."""
    # Mockar uma função
    mocker.patch(
        'app.services.vstats_client.VStatsClient.get_seasonstats',
        return_value={'goals': 1.5, 'goalsConceded': 0.8}
    )

    # Sua função agora chamará o mock em vez da API
    resultado = service.calcular_stats("abc123")
    assert resultado is not None

def test_mock_com_side_effect(mocker):
    """Mock que lança exceção ou retorna valores diferentes."""
    mock = mocker.patch('app.services.vstats_client.VStatsClient.get_match')

    # Primeira chamada retorna dados
    mock.side_effect = [
        {'id': '123', 'goals': 2},
        Exception("API error")
    ]

    # Primeira chamada sucede
    resultado1 = mock()
    assert resultado1['id'] == '123'

    # Segunda chamada falha
    with pytest.raises(Exception):
        mock()

def test_verificar_chamadas(mocker):
    """Verificar se função foi chamada com argumentos corretos."""
    mock = mocker.patch('app.services.cache_service.CacheService.get')
    mock.return_value = None

    # Executar código que usa o mock
    service.get_cached_data("key123")

    # Verificar chamada
    mock.assert_called_once_with("key123")
    assert mock.call_count == 1
```

---

## 6. Dados de Teste (Test Data)

### 6.1 JSON Fixtures

```python
# tests/fixtures/vstats_responses.json
{
  "schedule_month": {
    "matches": [
      {
        "Fx": "f4vscquffy37afgv0arwcbztg",
        "localDate": "2025-12-27",
        "kickoffTime": "17:00",
        "homeTeamId": "4dsgumo7d4zupm2ugsvm4zm4d",
        "homeTeamName": "Arsenal",
        "homeTeamCode": "ARS"
      }
    ]
  },
  "seasonstats": {
    "goals": 1.5,
    "goalsConceded": 0.8,
    "wonCorners": 5.2
  }
}
```

### 6.2 Usar Fixtures JSON nos Testes

```python
@pytest.fixture
def vstats_responses(scope="session"):
    """Carrega respostas mock da VStats."""
    import json
    with open("tests/fixtures/vstats_responses.json") as f:
        return json.load(f)

def test_com_response_mock(mocker, vstats_responses):
    """Testa com dados do arquivo JSON."""
    mocker.patch(
        'app.services.vstats_client.VStatsClient.get_schedule',
        return_value=vstats_responses['schedule_month']['matches']
    )

    resultado = service.get_partidas("2025-12-27")
    assert len(resultado) > 0
```

---

## 7. Parametrized Tests

```python
# Testar múltiplos casos com uma única função
@pytest.mark.parametrize("entrada,esperado", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_quadrado(entrada, esperado):
    """Testa quadrado de números."""
    assert entrada ** 2 == esperado

# IDs customizados para melhor legibilidade
@pytest.mark.parametrize(
    "cv,classificacao",
    [
        (0.10, "Muito Estável"),
        (0.20, "Estável"),
        (0.50, "Instável"),
    ],
    ids=["muito_estavel", "estavel", "instavel"]
)
def test_classificacao(cv, classificacao):
    """Testa classificação de CV."""
    assert classificar_cv(cv) == classificacao
```

---

## 8. Markers (Etiquetas de Testes)

### 8.1 Usar Markers

```python
@pytest.mark.slow
def test_operacao_lenta():
    """Este teste é lento."""
    time.sleep(10)

@pytest.mark.integration
def test_com_api_externa():
    """Teste de integração."""
    response = client.get("/api/partidas")
    assert response.status_code == 200

@pytest.mark.skip(reason="Não implementado ainda")
def test_futuro():
    """Teste para futura implementação."""
    pass

@pytest.mark.xfail(reason="Bug conhecido")
def test_com_bug():
    """Teste que falha mas é esperado falhar."""
    assert 1 == 2  # Falhará, mas é esperado
```

### 8.2 Rodar Tests por Marker

```bash
# Apenas unit tests
pytest -m unit

# Exclui slow tests
pytest -m "not slow"

# Unit tests que não são slow
pytest -m "unit and not slow"
```

---

## 9. Coverage (Cobertura de Testes)

### 9.1 Gerar Relatório de Coverage

```bash
# Terminal
pytest --cov=app

# HTML
pytest --cov=app --cov-report=html
# Abrir: htmlcov/index.html

# XML (para CI/CD)
pytest --cov=app --cov-report=xml

# Mostrar linhas não cobertas
pytest --cov=app --cov-report=term-missing
```

### 9.2 Interpretando Coverage

```
Name                    Stmts   Miss  Cover
-------------------------------------------
app/__init__.py              0      0   100%
app/main.py                  5      0   100%
app/models/partida.py       20      2    90%
app/services/stats.py       50     10    80%  ← Abaixo de 80%!
```

**Meta:** 80% mínimo

---

## 10. Debugging

### 10.1 Print Debugging

```python
def test_com_prints(capsys):
    """capsys captura prints."""
    print("Debug info")
    assert 1 == 1

    captured = capsys.readouterr()
    assert "Debug info" in captured.out
```

### 10.2 PDB Debugger

```bash
# Parar no primeiro erro
pytest --pdb

# Breakpoint no código
def test_algo():
    breakpoint()  # Para aqui, abre debugger
    assert 1 == 1
```

### 10.3 Logging nos Testes

```python
import logging

def test_com_logging(caplog):
    """caplog captura logs."""
    logger = logging.getLogger(__name__)
    logger.info("Mensagem de teste")

    assert "Mensagem de teste" in caplog.text
```

---

## 11. Testes Flaky (Intermitentes)

### ❌ Evitar

```python
# ❌ Ruim - tempo aleatório
import time
import random

def test_flaky():
    time.sleep(random.randint(1, 10))  # Aleatoriedade!
    assert True

# ❌ Ruim - dependência de estado externo
def test_flaky_external():
    response = requests.get("https://api-externa.com")  # Pode falhar
    assert response.status_code == 200
```

### ✅ Fazer

```python
# ✅ Bom - determinístico, sem I/O externo
def test_determinístico():
    resultado = calcular_cv([1, 2, 3, 4, 5])
    assert resultado > 0

# ✅ Bom - com mock
def test_com_mock(mocker):
    mocker.patch('requests.get', return_value=MagicMock(status_code=200))
    response = requests.get("https://api-externa.com")
    assert response.status_code == 200
```

---

## 12. Checklist Antes de Commit

- [ ] Todos os testes passam: `pytest`
- [ ] Cobertura >= 80%: `pytest --cov=app`
- [ ] Sem warnings: `pytest -v --tb=short`
- [ ] Tests formatados com Black: `black tests/`
- [ ] Linting passa: `ruff check tests/`
- [ ] Docstrings nos testes: cada função tem docstring
- [ ] Sem testes flaky: rodar 5 vezes, sempre passa
- [ ] Novos testes para novo código: sempre TDD!

---

## 13. Comandos Rápidos

```bash
# Setup initial
pytest --cov=app --cov-report=html --cov-fail-under=80

# Desenvolvimento rápido
pytest -x -v -s tests/

# Coverage detalhado
pytest --cov=app --cov-report=term-missing --cov-report=html

# CI/CD
pytest --cov=app --cov-report=xml --cov-fail-under=80

# Watch mode (rerun em mudanças)
pytest-watch

# Parallell (rápido)
pytest -n auto  # Requer pytest-xdist
```

---

## 14. Referências

- **Pytest Docs:** https://docs.pytest.org/
- **Pytest-Mock:** https://pytest-mock.readthedocs.io/
- **FastAPI Testing:** https://fastapi.tiangolo.com/tutorial/testing/
- **Testing Best Practices:** https://testingwithpytest.com/

---

## 15. Contatos & Suporte

- 📖 Ler [TESTING_STRATEGY.md](../docs/TESTING_STRATEGY.md) para mais detalhes
- 🐛 Issues: GitHub Issues
- 💬 Perguntas: contato@palpitremestre.com

---

**[⬆ Voltar ao topo](#testes---documentação)**

---

## Ver Também

Para entender melhor como estruturar e executar os testes, consulte:

- **[../docs/TESTING_STRATEGY.md](../docs/TESTING_STRATEGY.md)** - Estratégia completa e fundamentação teórica
- **[../docs/MODELOS_DE_DADOS.md](../docs/MODELOS_DE_DADOS.md)** - Schemas que você vai validar nos testes
- **[../docs/ARQUITETURA_BACKEND.md](../docs/ARQUITETURA_BACKEND.md)** - Arquitetura em camadas (o que testar em cada nível)
- **[../docs/API_SPECIFICATION.md](../docs/API_SPECIFICATION.md)** - Endpoints para integration tests
- **[../docs/LOCAL_SETUP.md](../docs/LOCAL_SETUP.md)** - Setup completo incluindo requirements-dev.txt
- **[../CONTRIBUTING.md](../CONTRIBUTING.md)** - Checklist que inclui testes (min 80% coverage)

**Próximos Passos Recomendados:**
1. Comece lendo [../docs/TESTING_STRATEGY.md](../docs/TESTING_STRATEGY.md) para entender a estratégia completa
2. Configure seu ambiente com [../docs/LOCAL_SETUP.md](../docs/LOCAL_SETUP.md)
3. Crie fixtures baseadas em exemplos desta página
4. Implemente testes unitários (70%) e integration (20%) como padrões mostrados aqui
5. Valide cobertura mínima de 80% antes de fazer commit
