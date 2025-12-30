# Arquitetura Backend - Sistema de Análise de Estatísticas de Futebol

**Versão:** 1.2
**Data:** 28 de Dezembro de 2025
**Stack:** Python 3.11+ | FastAPI | Pydantic | Redis (opcional)

---

## 1. Visão Geral da Arquitetura

O backend segue uma **arquitetura em camadas** baseada em **Clean Architecture**, com separação clara de responsabilidades entre:

```
┌─────────────────────────────────────────────────┐
│           API LAYER (Rotas)                      │
│    - Validação de entrada                       │
│    - Mapeamento de request/response            │
│    - Status HTTP                               │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│        BUSINESS LOGIC LAYER (Services)           │
│    - Cálculos de estatísticas                   │
│    - Lógica de filtros                         │
│    - Orquestração de dados                     │
│    - Cache management                          │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│    DATA ACCESS LAYER (Repositories)             │
│    - Chamadas a VStats API                      │
│    - Chamadas a TheSportsDB API                │
│    - Abstração de fontes externas              │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│         EXTERNAL SERVICES                        │
│    - VStats API (https://...)                   │
│    - TheSportsDB API (https://...)             │
│    - Redis Cache (localhost:6379)              │
└─────────────────────────────────────────────────┘
```

### Benefícios dessa Arquitetura

✅ **Testabilidade:** Cada camada pode ser testada isoladamente com mocks
✅ **Manutenibilidade:** Mudanças em uma camada não afetam as outras
✅ **Escalabilidade:** Fácil adicionar novos endpoints ou serviços
✅ **Reutilização:** Services podem ser reutilizados por múltiplos endpoints
✅ **Substituição:** Trocar Redis por Memcached sem impacto no código

---

## 2. Estrutura de Pastas

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                           # FastAPI app + routers
│   ├── config.py                         # Settings/Config (Pydantic BaseSettings)
│   ├── dependencies.py                   # Dependency Injection
│   │
│   ├── api/                              # 🔴 CAMADA: API/Presentation
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── partidas.py              # GET /api/partidas
│   │   │   ├── stats.py                 # GET /api/partida/{id}/stats
│   │   │   ├── competicoes.py           # GET /api/competicoes
│   │   │   └── escudos.py               # GET /api/time/{id}/escudo
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── error_handler.py         # Tratamento global de erros
│   │   │   └── cors.py                  # Configuração CORS
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── request.py               # DTOs de entrada (query params)
│   │       └── response.py              # DTOs de saída (response bodies)
│   │
│   ├── models/                           # 🟢 CAMADA: Models/Data Schemas
│   │   ├── __init__.py
│   │   ├── partida.py                   # TimeInfo, PartidaResumo, PartidaListResponse
│   │   ├── estatisticas.py              # EstatisticaMetrica, EstatisticasTime, StatsResponse
│   │   ├── competicao.py                # CompeticaoInfo
│   │   ├── escudo.py                    # EscudoResponse
│   │   └── vstats.py                    # Modelos da API VStats (mapeamento externo)
│   │
│   ├── services/                         # 🔵 CAMADA: Business Logic
│   │   ├── __init__.py
│   │   ├── partidas_service.py          # Busca/filtro de partidas
│   │   │   └── def get_partidas_por_data(data: date) -> List[PartidaResumo]
│   │   │   └── def filtrar_por_data(todas: List, data: date) -> List
│   │   │
│   │   ├── stats_service.py             # Cálculos de estatísticas
│   │   │   └── def calcular_stats(partida_id: str, filtro: str) -> StatsResponse
│   │   │   └── def agregar_estatisticas(matches: List) -> EstatisticasTime
│   │   │
│   │   ├── competicoes_service.py       # Gerenciamento de competições
│   │   │   └── def listar_competicoes() -> List[CompeticaoInfo]
│   │   │
│   │   ├── vstats_client.py             # Cliente HTTP para VStats API
│   │   │   └── class VStatsClient
│   │   │   └── def get_schedule_month(tournament_id: str) -> List[Match]
│   │   │   └── def get_seasonstats(tournament_id: str, team_id: str) -> SeasonStats
│   │   │   └── def get_match_stats(match_id: str) -> MatchStats
│   │   │
│   │   ├── thesportsdb_client.py        # Cliente HTTP para TheSportsDB
│   │   │   └── class TheSportsDBClient
│   │   │   └── def search_team_badge(team_name: str) -> str
│   │   │
│   │   └── cache_service.py             # Gerenciamento de cache
│   │       └── class CacheService
│   │       └── def get(key: str) -> Optional[Any]
│   │       └── def set(key: str, value: Any, ttl: int) -> None
│   │       └── def invalidate(pattern: str) -> None
│   │
│   ├── repositories/                     # 🟡 CAMADA: Data Access/Abstraction
│   │   ├── __init__.py
│   │   ├── vstats_repository.py         # Abstração da VStats API
│   │   │   └── class VStatsRepository
│   │   │   └── def fetch_matches(date: date) -> List[Match]
│   │   │   └── def fetch_season_stats(team: Team) -> SeasonStats
│   │   │
│   │   └── badge_repository.py          # Abstração do TheSportsDB
│   │       └── class BadgeRepository
│   │       └── def fetch_badge(team_name: str) -> str
│   │
│   └── utils/                            # 🟣 CAMADA: Utilities/Helpers
│       ├── __init__.py
│       ├── cv_calculator.py             # Cálculo de Coeficiente de Variação
│       │   └── def calcular_cv(valores: List[float]) -> float
│       │   └── def classificar_cv(cv: float) -> str
│       │
│       ├── date_utils.py                # Manipulação de datas
│       │   └── def parse_date(data_str: str) -> date
│       │   └── def formato_data(data: date) -> str
│       │
│       ├── logger.py                    # Configuração de logging
│       │   └── def get_logger(name: str) -> Logger
│       │
│       └── constants.py                 # Constantes globais
│           └── CV_THRESHOLDS
│           └── API_TIMEOUTS
│           └── STAT_NAMES
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Fixtures globais do pytest
│   ├── unit/
│   │   ├── test_cv_calculator.py
│   │   ├── test_stats_service.py
│   │   ├── test_partidas_service.py
│   │   ├── test_vstats_client.py
│   │   └── test_cache_service.py
│   ├── integration/
│   │   ├── test_partidas_route.py
│   │   ├── test_stats_route.py
│   │   ├── test_competicoes_route.py
│   │   └── test_escudos_route.py
│   └── fixtures/
│       ├── vstats_responses.json
│       ├── thesportsdb_responses.json
│       └── mock_partidas.json
│
├── requirements.txt                     # Dependências de produção
├── requirements-dev.txt                 # Dependências de desenvolvimento
├── Dockerfile                           # Containerização
├── .env.example                         # Variáveis de ambiente (template)
├── .dockerignore
├── .gitignore
└── README.md                            # Setup rápido

```

### Legenda de Cores

- 🔴 **API Layer:** Validação, request/response, HTTP status
- 🟢 **Models Layer:** Definição de estruturas de dados (Pydantic)
- 🔵 **Services Layer:** Lógica de negócio, orquestração
- 🟡 **Repositories Layer:** Acesso a APIs/dados externos
- 🟣 **Utils Layer:** Funções puras, helpers, constantes

---

## 3. Responsabilidades por Camada

### 3.1 API Layer (routes/)

**O QUE FAZ:**
- ✅ Recebe requisições HTTP
- ✅ Valida parâmetros de entrada (query params, path params)
- ✅ Chama services apropriados
- ✅ Mapeia respostas para JSON
- ✅ Define status HTTP (200, 400, 404, 500)
- ✅ Trata exceções em primeiro nível

**O QUE NÃO FAZ:**
- ❌ Cálculos de negócio
- ❌ Acesso direto a APIs externas
- ❌ Lógica de filtros complexa
- ❌ Gerenciamento de cache

**Exemplo:**

```python
# app/api/routes/partidas.py
from fastapi import APIRouter, Query, HTTPException
from datetime import date
from app.models.partida import PartidaListResponse
from app.services.partidas_service import PartidasService

router = APIRouter(prefix="/api", tags=["partidas"])

@router.get("/partidas", response_model=PartidaListResponse)
async def listar_partidas(
    data: str = Query(..., description="Data no formato YYYY-MM-DD"),
    service: PartidasService = Depends(get_partidas_service)
):
    """
    Lista partidas para uma data específica.

    **Parâmetros:**
    - `data`: Data no formato YYYY-MM-DD (obrigatório)

    **Retorno:** Lista de partidas com times, horários e competições
    """
    try:
        partidas = service.get_partidas_por_data(data)
        return PartidaListResponse(data=data, total_partidas=len(partidas), partidas=partidas)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Data inválida: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao buscar partidas")
```

### 3.2 Models Layer

**O QUE FAZ:**
- ✅ Define contratos de dados (Pydantic BaseModel)
- ✅ Valida tipos de dados (strings, dates, floats)
- ✅ Aplica validadores customizados
- ✅ Serializa/desserializa JSON automaticamente
- ✅ Gera documentação OpenAPI automática

**O QUE NÃO FAZ:**
- ❌ Lógica de negócio
- ❌ Acesso a APIs externas
- ❌ Cálculos complexos

**Exemplo:**

```python
# app/models/estatisticas.py
from pydantic import BaseModel, validator
from typing import Dict, Optional

class EstatisticaMetrica(BaseModel):
    media: float
    cv: float
    classificacao: Optional[str] = None

    @validator('media')
    def media_nao_negativa(cls, v):
        if v < 0:
            raise ValueError('Média não pode ser negativa')
        return v

    @validator('cv')
    def cv_nao_negativo(cls, v):
        if v < 0:
            raise ValueError('CV não pode ser negativo')
        return v

    @validator('classificacao', always=True)
    def calcular_classificacao(cls, v, values):
        cv = values.get('cv')
        if cv is None:
            return v
        # Retorna automaticamente baseado no CV
        if cv < 0.15: return "Muito Estável"
        elif cv < 0.30: return "Estável"
        elif cv < 0.45: return "Moderado"
        elif cv < 0.60: return "Instável"
        else: return "Muito Instável"

class EstatisticasTime(BaseModel):
    escanteios: Dict[str, EstatisticaMetrica]     # feitos, sofridos
    gols: Dict[str, EstatisticaMetrica]           # feitos, sofridos
    finalizacoes: Dict[str, EstatisticaMetrica]   # feitas, sofridas
    # ...
```

### 3.3 Services Layer (business logic)

**O QUE FAZ:**
- ✅ Implementa lógica de negócio
- ✅ Orquestra múltiplos repositórios
- ✅ Calcula estatísticas (CV, médias)
- ✅ Aplica filtros
- ✅ Gerencia cache
- ✅ Trata erros de negócio

**O QUE NÃO FAZ:**
- ❌ Responder HTTP diretamente
- ❌ Acessar APIs externas diretamente (usa repositories)
- ❌ Validar tipos HTTP (usa models)

**Exemplo:**

```python
# app/services/stats_service.py
from typing import List
from datetime import date
from app.models.estatisticas import EstatisticasTime, EstatisticaMetrica
from app.models.partida import PartidaResumo
from app.repositories.vstats_repository import VStatsRepository
from app.utils.cv_calculator import calcular_cv, classificar_cv

class StatsService:
    def __init__(self, vstats_repo: VStatsRepository, cache_service):
        self.vstats_repo = vstats_repo
        self.cache_service = cache_service

    async def calcular_stats(
        self,
        partida_id: str,
        filtro: str = "geral"
    ) -> Dict[str, Any]:
        """
        Calcula estatísticas para uma partida.

        Args:
            partida_id: ID da partida
            filtro: "geral", "5", ou "10"

        Returns:
            Dicionário com estatísticas agregadas
        """
        # Tenta cache primeiro
        cache_key = f"stats:{partida_id}:{filtro}"
        cached = self.cache_service.get(cache_key)
        if cached:
            return cached

        # Busca dados da partida e histórico
        partida = await self.vstats_repo.fetch_match(partida_id)
        match_history_home = await self.vstats_repo.fetch_team_history(
            partida['homeTeamId'],
            limit=self._get_limit(filtro)
        )
        match_history_away = await self.vstats_repo.fetch_team_history(
            partida['awayTeamId'],
            limit=self._get_limit(filtro)
        )

        # Calcula estatísticas agregadas
        stats_home = self._agregar_stats(match_history_home)
        stats_away = self._agregar_stats(match_history_away)

        # Armazena em cache por 6 horas
        self.cache_service.set(cache_key, result, ttl=21600)

        return {
            'partida': partida,
            'mandante': stats_home,
            'visitante': stats_away
        }

    def _agregar_stats(self, matches: List) -> Dict:
        """Agrega estatísticas de múltiplas partidas."""
        gols = [m['goals'] for m in matches]
        escanteios = [m['wonCorners'] for m in matches]

        return {
            'gols': {
                'media': sum(gols) / len(gols) if gols else 0,
                'cv': calcular_cv(gols) if len(gols) > 1 else 0
            },
            'escanteios': {
                'media': sum(escanteios) / len(escanteios) if escanteios else 0,
                'cv': calcular_cv(escanteios) if len(escanteios) > 1 else 0
            }
        }
```

### 3.4 Repositories Layer (data access)

**O QUE FAZ:**
- ✅ Faz chamadas HTTP a APIs externas
- ✅ Converte respostas externas para modelos internos
- ✅ Trata erros específicos de APIs (timeout, 404, 500)
- ✅ Implementa retry logic
- ✅ Abstrai fontes de dados

**O QUE NÃO FAZ:**
- ❌ Lógica de negócio
- ❌ Cálculos
- ❌ Gerenciamento de cache (responsabilidade do Service)

**Exemplo:**

```python
# app/repositories/vstats_repository.py
import httpx
from app.config import settings
from typing import List, Optional

class VStatsRepository:
    def __init__(self):
        self.base_url = settings.VSTATS_API_URL
        self.client = httpx.AsyncClient(timeout=10)

    async def fetch_calendar(self) -> List[dict]:
        """
        Busca TODAS as competições disponíveis dinamicamente.

        IMPORTANTE: IDs de torneios mudam a cada temporada.
        Este endpoint retorna os IDs atualizados automaticamente.

        Returns:
            Lista de competições com estrutura normalizada:
            [{"id": "...", "name": "Premier League", "country": "England"}, ...]
        """
        response = await self.client.get(f"{self.base_url}/tournament/v1/calendar")
        response.raise_for_status()

        # Normaliza estrutura da resposta
        competitions = []
        for comp in response.json():
            competitions.append({
                "id": comp.get("tournamentCalendarId"),
                "name": comp.get("knownName") or comp.get("name"),
                "country": comp.get("country"),
            })
        return competitions

    async def fetch_matches(self, tournament_id: str, date: str) -> List[dict]:
        """Busca partidas de um torneio para uma data específica."""
        try:
            response = await self.client.get(
                f"{self.base_url}/schedule/month",
                params={'Tmcl': tournament_id}  # Nota: T maiúsculo!
            )
            response.raise_for_status()

            # Resposta: {"matches": [...]}
            matches = response.json().get('matches', [])

            # Filtra por data (client-side, pois API não suporta filtro por data)
            return [m for m in matches if m.get('localDate') == date]

        except httpx.TimeoutException:
            raise Exception(f"VStats timeout ao buscar partidas")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []  # Torneio não encontrado
            raise Exception(f"VStats erro {e.response.status_code}")

    async def fetch_seasonstats(
        self,
        tournament_id: str,
        team_id: str
    ) -> dict:
        """Busca estatísticas de temporada de um time."""
        try:
            response = await self.client.get(
                f"{self.base_url}/seasonstats",
                params={'Tmcl': tournament_id, 'Ctst': team_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            raise Exception(f"Erro ao buscar seasonstats")

    async def close(self):
        """Fecha a conexão HTTP."""
        await self.client.aclose()
```

### 3.5 Utils Layer

**O QUE FAZ:**
- ✅ Funções puras e reutilizáveis
- ✅ Cálculos matemáticos (CV, médias)
- ✅ Helpers de data/hora
- ✅ Logging configurado
- ✅ Constantes globais

**O QUE NÃO FAZ:**
- ❌ Ter estado (functions puras)
- ❌ Acessar banco de dados ou APIs

**Exemplo:**

```python
# app/utils/cv_calculator.py
from typing import List
from statistics import mean, stdev

def calcular_cv(valores: List[float]) -> float:
    """
    Calcula Coeficiente de Variação.

    CV = Desvio Padrão / Média

    Args:
        valores: Lista de números

    Returns:
        CV arredondado a 2 casas decimais
    """
    if not valores or len(valores) < 2:
        return 0.0

    media = mean(valores)
    if media == 0:
        return 0.0

    desvio = stdev(valores)
    cv = desvio / media

    return round(cv, 2)

def classificar_cv(cv: float) -> str:
    """Classifica o CV em categorias."""
    if cv < 0.15: return "Muito Estável"
    elif cv < 0.30: return "Estável"
    elif cv < 0.45: return "Moderado"
    elif cv < 0.60: return "Instável"
    else: return "Muito Instável"
```

---

## 4. Fluxo Completo de uma Requisição

Exemplo: **GET /api/partida/{matchId}/stats?filtro=5**

```
1. HTTP Request chega
   └─> GET /api/partida/abc123/stats?filtro=5

2. FastAPI Router (routes/stats.py)
   └─> Valida path param: matchId = "abc123"
   └─> Valida query param: filtro = "5"
   └─> Mapeia para função handler
   └─> Injeita StatsService (via Depends)

3. StatsService.calcular_stats(matchId="abc123", filtro="5")
   └─> Verifica cache: cache_service.get("stats:abc123:5")
   └─> Se não encontrado, continua...

4. VStatsRepository.fetch_match("abc123")
   └─> HTTP GET request a VStats API
   └─> Trata erros (timeout, 404, 500)
   └─> Retorna dict com dados da partida

5. VStatsRepository.fetch_team_history(homeTeamId, limit=5)
   └─> HTTP GET request a VStats API
   └─> Retorna últimas 5 partidas do time mandante

6. VStatsRepository.fetch_team_history(awayTeamId, limit=5)
   └─> HTTP GET request a VStats API
   └─> Retorna últimas 5 partidas do time visitante

7. StatsService._agregar_stats(match_history)
   └─> Extrai campos relevantes (gols, escanteios, etc)
   └─> Chama cv_calculator.calcular_cv()
   └─> Retorna EstatisticasTime com médias e CVs

8. Armazena em Cache
   └─> cache_service.set("stats:abc123:5", resultado, ttl=21600)

9. Validação com Pydantic (StatsResponse model)
   └─> Valida tipos de dados
   └─> Serializa para JSON

10. HTTP Response retorna
    └─> Status 200 OK
    └─> Content-Type: application/json
    └─> Body: {"partida": {...}, "mandante": {...}, "visitante": {...}}
```

---

## 5. Padrões Importantes

### 5.1 Dependency Injection (DI)

Usar `FastAPI Depends` para injetar dependências:

```python
# app/dependencies.py
from fastapi import Depends
from app.services.stats_service import StatsService
from app.repositories.vstats_repository import VStatsRepository

def get_vstats_repository() -> VStatsRepository:
    """Factory para VStatsRepository."""
    return VStatsRepository()

def get_stats_service(
    vstats_repo: VStatsRepository = Depends(get_vstats_repository)
) -> StatsService:
    """Factory para StatsService com dependencies injetadas."""
    return StatsService(vstats_repo)

# app/api/routes/stats.py
@router.get("/partida/{matchId}/stats")
async def get_stats(
    matchId: str,
    service: StatsService = Depends(get_stats_service)  # ⬅️ Injetado automáticamente
):
    return service.calcular_stats(matchId)
```

**Benefícios:**
- Fácil mockar em testes
- Reutilizar instâncias
- Injetar diferentes implementações

### 5.2 Error Handling Centralizado

```python
# app/api/middleware/error_handler.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

async def http_exception_handler(request: Request, exc: Exception):
    """Handler global de exceções."""
    logger.error(f"Exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )

# main.py
app.add_exception_handler(Exception, http_exception_handler)
```

### 5.3 Logging Estruturado

```python
# app/utils/logger.py
import logging

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# Uso:
logger = get_logger(__name__)
logger.info("Iniciando busca de partidas")
logger.error(f"Erro ao conectar com API VStats: {error}")
```

---

## 6. Convenções de Código

### 6.1 Nomenclatura

| Elemento | Convenção | Exemplo |
|----------|-----------|---------|
| Módulos | snake_case | `partidas_service.py` |
| Classes | PascalCase | `PartidasService` |
| Funções | snake_case | `calcular_cv()` |
| Constantes | UPPER_SNAKE_CASE | `CACHE_TTL_SCHEDULE` |
| Variáveis | snake_case | `partidas_list` |
| Métodos privados | _snake_case | `_agregar_stats()` |
| Parâmetros | snake_case | `tournament_id` |

### 6.2 Imports

**Ordem correta:**

```python
# 1. Stdlib
import os
from typing import List, Optional
from datetime import date

# 2. Third-party
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
import httpx

# 3. Local
from app.models.partida import PartidaResumo
from app.services.partidas_service import PartidasService
from app.config import settings
```

### 6.3 Docstrings

Usar **Google style** para docstrings:

```python
def calcular_stats(
    self,
    partida_id: str,
    filtro: str = "geral"
) -> Dict[str, Any]:
    """
    Calcula estatísticas para uma partida.

    Busca dados da partida e histórico do time, calcula
    médias e coeficientes de variação.

    Args:
        partida_id: ID único da partida (ex: "abc123xyz")
        filtro: Período de análise ("geral", "5", ou "10")

    Returns:
        Dict com chaves 'partida', 'mandante', 'visitante'
        contendo estatísticas agregadas

    Raises:
        ValueError: Se partida_id é vazio ou filtro inválido
        Exception: Se VStats API retorna erro

    Example:
        >>> stats = service.calcular_stats("abc123", filtro="5")
        >>> print(stats['mandante']['gols']['media'])
        1.82
    """
    pass
```

---

## 7. Tratamento de Erros

### 7.1 Exceções Customizadas

```python
# app/exceptions.py
class APIError(Exception):
    """Exceção base da aplicação."""
    pass

class VStatsAPIError(APIError):
    """Erro ao conectar com VStats API."""
    pass

class DataNotFoundError(APIError):
    """Dados não encontrados."""
    pass

class InvalidFilterError(APIError):
    """Filtro inválido."""
    pass

# Uso:
try:
    result = await vstats_repo.fetch_match(matchId)
except httpx.HTTPStatusError as e:
    raise VStatsAPIError(f"VStats retornou status {e.response.status_code}")
```

### 7.2 HTTP Status Codes

| Status | Uso | Exemplo |
|--------|-----|---------|
| 200 | Sucesso | Partidas encontradas |
| 400 | Bad Request | Data inválida |
| 404 | Not Found | Partida não existe |
| 500 | Server Error | VStats API indisponível |

---

## 8. Testing Strategy

Cada camada tem testes específicos:

```python
# tests/unit/test_stats_service.py
def test_calcular_cv():
    """Testa cálculo de CV (função pura)."""
    from app.utils.cv_calculator import calcular_cv

    resultado = calcular_cv([1, 2, 3, 4, 5])
    assert resultado > 0
    assert isinstance(resultado, float)

# tests/integration/test_stats_route.py
async def test_get_stats_endpoint(app_client):
    """Testa endpoint completo com mock."""
    response = app_client.get(
        "/api/partida/abc123/stats?filtro=5"
    )
    assert response.status_code == 200
    assert 'partida' in response.json()
```

---

## 9. Otimizações de Performance

### 9.1 Reutilização de Schedule (v1.1)

**Problema:** Ao calcular estatísticas de uma partida, o schedule completo do torneio (~380 partidas) era buscado **2 vezes** - uma para cada time, mesmo ambos estando no mesmo torneio.

**Solução:** Buscar o schedule **uma vez** antes do `asyncio.gather()` e passar como parâmetro:

```python
# ANTES (2 chamadas API):
async def calcular_stats(self, match_id, ...):
    home_stats, away_stats = await asyncio.gather(
        self._get_team_stats(home_id),  # → fetch_schedule_full() #1
        self._get_team_stats(away_id),  # → fetch_schedule_full() #2 (DUPLICADA!)
    )

# DEPOIS (1 chamada API):
async def calcular_stats(self, match_id, ...):
    schedule = await self._fetch_tournament_schedule(tournament_id)  # UMA VEZ

    home_stats, away_stats = await asyncio.gather(
        self._get_team_stats(home_id, schedule=schedule),  # usa cache
        self._get_team_stats(away_id, schedule=schedule),  # usa cache
    )
```

**Implementação:**

| Método | Alteração |
|--------|-----------|
| `_fetch_tournament_schedule()` | **NOVO** - Busca schedule com cache de 1h |
| `calcular_stats()` | Busca schedule antes do `asyncio.gather()` |
| `_get_team_stats()` | + parâmetro `schedule: Optional[dict]` |
| `_get_recent_matches_stats()` | + parâmetro `schedule: Optional[dict]` |
| `_get_recent_matches_with_form()` | Usa schedule se fornecido, senão busca/cacheia |

**Resultado:**

| Métrica | Antes | Depois |
|---------|-------|--------|
| Chamadas schedule/request | 2 | 1 |
| Latência estimada (schedule) | ~1000ms | ~500ms |
| Cache hit após 1ª requisição | ✓ | ✓ (1h TTL) |

### 9.2 Time-Weighting (Dixon-Coles Decay) (v1.6)

**Conceito:** Partidas mais recentes devem ter mais peso no cálculo de médias e CV, pois refletem melhor a forma atual do time.

**Implementação:** Decay exponencial padrão Dixon-Coles:

```python
# Fórmula: weight = e^(-decay × days_ago)
# Com decay = 0.0065:

TIME_DECAY_FACTOR = 0.0065

def _calculate_time_weight(self, match_date_str: str) -> float:
    """
    Pesos por idade da partida:
    - Hoje: 100%
    - 30 dias: 82%
    - 60 dias: 68%
    - 90 dias: 56%
    - 180 dias: 31%
    """
    match_date = datetime.strptime(match_date_str, "%Y-%m-%d").date()
    days_ago = (date.today() - match_date).days
    return math.exp(-TIME_DECAY_FACTOR * max(days_ago, 0))
```

**Média e CV Ponderados:**

```python
def _weighted_mean(self, values: List[float], weights: List[float]) -> float:
    """Média ponderada: Σ(v × w) / Σ(w)"""
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)

def _weighted_cv(self, values: List[float], weights: List[float], wmean: float) -> float:
    """CV ponderado: √(Σ(w × (v - wmean)²) / Σ(w)) / wmean"""
    variance = sum(w * (v - wmean) ** 2 for v, w in zip(values, weights)) / sum(weights)
    return math.sqrt(variance) / wmean
```

**Fluxo:**

1. `_get_recent_matches_with_form()` retorna `match_dates` junto com `match_ids`
2. `_get_recent_matches_stats()` calcula pesos para cada partida
3. `_calculate_metrics_from_matches()` usa médias/CV ponderados

**Impacto:**

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Peso das partidas | Igual para todas | Mais recentes = mais peso |
| Forma recente | Não considerada | Valorizada |
| Times em fase ruim | Média "diluída" | Reflete situação atual |

**Referência:** Dixon & Coles (1997) - "Modelling Association Football Scores and Inefficiencies in the Football Betting Market"

---

## 10. Checklist de Implementação

- [ ] Criar estrutura de pastas conforme seção 2
- [ ] Implementar models (app/models/)
- [ ] Implementar repositories (app/repositories/)
- [ ] Implementar services (app/services/)
- [ ] Implementar routes (app/api/routes/)
- [ ] Adicionar dependency injection (app/dependencies.py)
- [ ] Configurar error handling (app/api/middleware/)
- [ ] Adicionar logging (app/utils/logger.py)
- [ ] Escrever testes unitários (tests/unit/)
- [ ] Escrever testes de integração (tests/integration/)
- [ ] Configurar pytest.ini e conftest.py
- [ ] Validar com FastAPI docs em /docs

---

## Referências

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Pydantic Docs:** https://docs.pydantic.dev
- **Clean Architecture:** Robert C. Martin's principles
- **Pytest Docs:** https://docs.pytest.org

---

## Ver Também

Para entender melhor este documento e seu contexto no sistema, consulte:

- **[MODELOS_DE_DADOS.md](MODELOS_DE_DADOS.md)** - Define todos os Pydantic schemas mencionados
- **[API_SPECIFICATION.md](API_SPECIFICATION.md)** - Documentação dos 4 endpoints que usam essa arquitetura
- **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)** - Como testar cada camada da arquitetura
- **[LOCAL_SETUP.md](LOCAL_SETUP.md)** - Como rodar o backend localmente
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Guia de contribuição seguindo esses padrões
- **[tests/README.md](../tests/README.md)** - Guia prático de testes com exemplos

**Próximos Passos Recomendados:**
1. Leia [MODELOS_DE_DADOS.md](MODELOS_DE_DADOS.md) para entender como os schemas Pydantic se encaixam nessa arquitetura
2. Estude [API_SPECIFICATION.md](API_SPECIFICATION.md) para ver quais endpoints implementar
3. Siga [LOCAL_SETUP.md](LOCAL_SETUP.md) para configurar o ambiente
4. Consulte [TESTING_STRATEGY.md](TESTING_STRATEGY.md) para escrever testes para cada camada
