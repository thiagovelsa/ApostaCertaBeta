# Modelos de Dados - Pydantic Schemas

**Versão:** 1.1
**Data:** 26 de Dezembro de 2025
**Framework:** Pydantic v2.x (com FastAPI)

---

## 1. Visão Geral

Este documento define todos os modelos Pydantic (schemas/DTOs) usados na API. Pydantic valida automaticamente os tipos de dados e serializa/desserializa JSON.

**Estrutura de Pastas:**

```
app/models/
├── __init__.py              # Importa todos os modelos
├── partida.py               # TimeInfo, PartidaResumo, PartidaListResponse
├── estatisticas.py          # EstatisticaMetrica, EstatisticasTime, StatsResponse
├── competicao.py            # CompeticaoInfo
├── escudo.py                # EscudoResponse
└── vstats.py                # Modelos da API VStats (mapeamento externo)
```

---

## 2. Modelos de Partida

### 2.1 TimeInfo

```python
# app/models/partida.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class TimeInfo(BaseModel):
    """Informações básicas de um time (mandante/visitante)."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="ID único do time na VStats API"
    )
    nome: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nome oficial do time (ex: Arsenal)"
    )
    codigo: str = Field(
        ...,
        min_length=2,
        max_length=5,
        description="Código do time (ex: ARS)"
    )
    escudo: Optional[str] = Field(
        None,
        description="URL do escudo/logo do time (de TheSportsDB)",
        examples=["https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "4dsgumo7d4zupm2ugsvm4zm4d",
                "nome": "Arsenal",
                "codigo": "ARS",
                "escudo": "https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png"
            }
        }
```

**Validações:**
- `id`: Obrigatório, 1-50 caracteres
- `nome`: Obrigatório, 1-100 caracteres
- `codigo`: Obrigatório, 2-5 caracteres (ex: ARS, MU, LIV)
- `escudo`: Opcional, URL válida

### 2.2 PartidaResumo

```python
from datetime import date, time

class PartidaResumo(BaseModel):
    """Resumo de uma partida (usado em listas)."""

    id: str = Field(
        ...,
        description="ID único da partida"
    )
    data: date = Field(
        ...,
        description="Data da partida (formato YYYY-MM-DD)"
    )
    horario: time = Field(
        ...,
        description="Horário da partida (formato HH:MM)"
    )
    competicao: str = Field(
        ...,
        max_length=100,
        description="Nome da competição (ex: Premier League)"
    )
    estadio: str = Field(
        ...,
        max_length=100,
        description="Nome do estádio"
    )
    mandante: TimeInfo = Field(
        ...,
        description="Time mandante (casa)"
    )
    visitante: TimeInfo = Field(
        ...,
        description="Time visitante"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "f4vscquffy37afgv0arwcbztg",
                "data": "2025-12-27",
                "horario": "17:00",
                "competicao": "Premier League",
                "estadio": "Emirates Stadium",
                "mandante": {
                    "id": "4dsgumo7d4zupm2ugsvm4zm4d",
                    "nome": "Arsenal",
                    "codigo": "ARS",
                    "escudo": "https://..."
                },
                "visitante": {
                    "id": "1c8m2ko0wxq1asfkuykurdr0y",
                    "nome": "Crystal Palace",
                    "codigo": "CRY",
                    "escudo": "https://..."
                }
            }
        }
```

### 2.3 PartidaListResponse

```python
from typing import List

class PartidaListResponse(BaseModel):
    """Response para GET /api/partidas."""

    data: date = Field(
        ...,
        description="Data das partidas"
    )
    total_partidas: int = Field(
        ...,
        ge=0,
        description="Total de partidas encontradas para essa data"
    )
    partidas: List[PartidaResumo] = Field(
        ...,
        description="Array de partidas"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "data": "2025-12-27",
                "total_partidas": 2,
                "partidas": [
                    {
                        "id": "f4vscquffy37afgv0arwcbztg",
                        "data": "2025-12-27",
                        "horario": "17:00",
                        # ... resto dos campos
                    }
                ]
            }
        }
```

**Validações:**
- `total_partidas`: Não pode ser negativo (ge=0 = greater or equal)
- `data`: Formato YYYY-MM-DD obrigatório
- `partidas`: Array pode estar vazio

---

## 3. Modelos de Estatísticas

### 3.1 EstatisticaMetrica

```python
# app/models/estatisticas.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class EstatisticaMetrica(BaseModel):
    """Métrica de estatística com média, CV e classificação."""

    media: float = Field(
        ...,
        ge=0,
        description="Valor médio (ex: 5.88 gols por partida)"
    )
    cv: float = Field(
        ...,
        ge=0,
        description="Coeficiente de Variação (0.0 a infinito)"
    )
    classificacao: Literal[
        "Muito Estável",
        "Estável",
        "Moderado",
        "Instável",
        "Muito Instável"
    ] = Field(
        ...,
        description="Classificação automática baseada no CV"
    )

    @field_validator('media')
    @classmethod
    def validar_media(cls, v):
        """Media não pode ser negativa."""
        if v < 0:
            raise ValueError('Média não pode ser negativa')
        return round(v, 2)

    @field_validator('cv')
    @classmethod
    def validar_cv(cls, v):
        """CV não pode ser negativo."""
        if v < 0:
            raise ValueError('CV não pode ser negativo')
        return round(v, 2)

    @field_validator('classificacao', mode='before')
    @classmethod
    def calcular_classificacao(cls, v, info):
        """Calcula classificação automaticamente baseado no CV."""
        # Se classificação foi fornecida explicitamente, usa
        if v is not None:
            return v

        # Caso contrário, calcula baseado no CV
        cv = info.data.get('cv')
        if cv is None:
            return "Moderado"  # Default

        if cv < 0.15:
            return "Muito Estável"
        elif cv < 0.30:
            return "Estável"
        elif cv < 0.50:
            return "Moderado"
        elif cv < 0.75:
            return "Instável"
        else:
            return "Muito Instável"

    class Config:
        json_schema_extra = {
            "example": {
                "media": 5.88,
                "cv": 0.32,
                "classificacao": "Moderado"
            }
        }
```

### 3.2 EstatisticaFeitos

```python
class EstatisticaFeitos(BaseModel):
    """Estatísticas feitas vs sofridas (gols, escanteios, etc)."""

    feitos: EstatisticaMetrica = Field(
        ...,
        description="Estatística feita/marcada pelo time"
    )
    sofridos: EstatisticaMetrica = Field(
        ...,
        description="Estatística sofrida/concedida pelo time"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "feitos": {
                    "media": 5.88,
                    "cv": 0.32,
                    "classificacao": "Moderado"
                },
                "sofridos": {
                    "media": 3.50,
                    "cv": 0.28,
                    "classificacao": "Estável"
                }
            }
        }
```

### 3.3 EstatisticasTime

```python
from typing import Dict

class EstatisticasTime(BaseModel):
    """Todas as estatísticas de um time para uma partida."""

    escanteios: EstatisticaFeitos = Field(
        ...,
        description="Escanteios feitos e sofridos"
    )
    gols: EstatisticaFeitos = Field(
        ...,
        description="Gols feitos e sofridos"
    )
    finalizacoes: EstatisticaFeitos = Field(
        ...,
        description="Total de finalizações (shots) feitas e sofridas"
    )
    finalizacoes_gol: EstatisticaFeitos = Field(
        ...,
        description="Finalizações ao gol (shots on target) feitas e sofridas"
    )
    cartoes: Dict[str, EstatisticaMetrica] = Field(
        ...,
        description="Cartões (amarelos, vermelhos)"
    )

    @field_validator('cartoes')
    @classmethod
    def validar_cartoes(cls, v):
        """Valida que cartoes contém apenas 'amarelos' e 'vermelhos'."""
        permitidos = {'amarelos', 'vermelhos'}
        if not all(key in permitidos for key in v.keys()):
            raise ValueError(f"Cartões deve conter apenas {permitidos}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "escanteios": {
                    "feitos": {"media": 5.88, "cv": 0.32, "classificacao": "Moderado"},
                    "sofridos": {"media": 3.50, "cv": 0.28, "classificacao": "Estável"}
                },
                "gols": {
                    "feitos": {"media": 1.82, "cv": 0.41, "classificacao": "Moderado"},
                    "sofridos": {"media": 0.59, "cv": 0.65, "classificacao": "Instável"}
                },
                "finalizacoes": {
                    "feitas": {"media": 10.82, "cv": 0.25, "classificacao": "Estável"},
                    "sofridas": {"media": 8.20, "cv": 0.35, "classificacao": "Moderado"}
                },
                "finalizacoes_gol": {
                    "feitas": {"media": 4.50, "cv": 0.30, "classificacao": "Moderado"},
                    "sofridas": {"media": 2.80, "cv": 0.40, "classificacao": "Moderado"}
                },
                "cartoes": {
                    "amarelos": {"media": 1.29, "cv": 0.55, "classificacao": "Instável"},
                    "vermelhos": {"media": 0.12, "cv": 0.85, "classificacao": "Muito Instável"}
                }
            }
        }
```

### 3.4 TimeComEstatisticas

```python
class TimeComEstatisticas(BaseModel):
    """Time com suas estatísticas e forma recente."""

    id: str = Field(..., description="ID único do time")
    nome: str = Field(..., description="Nome do time")
    escudo: Optional[str] = Field(None, description="URL do escudo")
    estatisticas: EstatisticasAgregadas = Field(..., description="Estatísticas agregadas")
    recent_form: List[Literal["W", "D", "L"]] = Field(
        default=[],
        description="Sequência de resultados recentes (W=Win, D=Draw, L=Loss)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "4dsgumo7d4zupm2ugsvm4zm4d",
                "nome": "Arsenal",
                "escudo": "https://...",
                "estatisticas": { ... },
                "recent_form": ["W", "D", "W", "L", "W"]
            }
        }
```

**Campo `recent_form`:**
- Array de resultados recentes do time (mais recente primeiro)
- Valores: `"W"` (Vitória), `"D"` (Empate), `"L"` (Derrota)
- Calculado a partir de `goals` vs `goalsConceded` de cada partida
- Limitado pelo filtro: Temporada/Últimos 5 → 5 resultados, Últimos 10 → 10 resultados

---

### 3.5 StatsResponse

```python
class StatsResponse(BaseModel):
    """Response para GET /api/partida/{matchId}/stats."""

    filtro_aplicado: Literal["geral", "5", "10"] = Field(
        ...,
        description="Qual período foi analisado"
    )
    partidas_analisadas: int = Field(
        ...,
        ge=1,
        description="Número de partidas usadas para calcular as médias"
    )
    mandante: TimeComEstatisticas = Field(
        ...,
        description="Estatísticas do time mandante"
    )
    visitante: TimeComEstatisticas = Field(
        ...,
        description="Estatísticas do time visitante"
    )
    arbitro: Optional[ArbitroInfo] = Field(
        None,
        description="Informações do árbitro e estatísticas de cartões"
    )

    @field_validator('mandante', 'visitante', mode='before')
    @classmethod
    def montar_dict_time(cls, v):
        """Monta dict com id, nome, escudo e estatisticas."""
        if isinstance(v, dict):
            # Se já é dict, retorna como está
            return {
                'id': v.get('id'),
                'nome': v.get('nome'),
                'escudo': v.get('escudo'),
                'estatisticas': v.get('estatisticas')
            }
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "partida": {
                    "id": "f4vscquffy37afgv0arwcbztg",
                    "data": "2025-12-27",
                    "horario": "17:00",
                    "competicao": "Premier League",
                    "estadio": "Emirates Stadium",
                    "mandante": {"id": "4dsgumo7d4zupm2ugsvm4zm4d", "nome": "Arsenal", "codigo": "ARS", "escudo": "https://..."},
                    "visitante": {"id": "1c8m2ko0wxq1asfkuykurdr0y", "nome": "Crystal Palace", "codigo": "CRY", "escudo": "https://..."}
                },
                "filtro_aplicado": "5",
                "partidas_analisadas": 5,
                "mandante": {
                    "id": "4dsgumo7d4zupm2ugsvm4zm4d",
                    "nome": "Arsenal",
                    "escudo": "https://...",
                    "estatisticas": {
                        "escanteios": {"feitos": {"media": 5.88, "cv": 0.32, "classificacao": "Moderado"}, "sofridos": {"media": 3.50, "cv": 0.28, "classificacao": "Estável"}},
                        # ... resto das estatísticas
                    }
                },
                "visitante": {
                    "id": "1c8m2ko0wxq1asfkuykurdr0y",
                    "nome": "Crystal Palace",
                    "escudo": "https://...",
                    "estatisticas": {
                        # ...
                    }
                }
            }
        }
```

---

## 3.6 ArbitroInfo

```python
class ArbitroInfo(BaseModel):
    """Informações do árbitro e estatísticas de cartões."""

    id: str = Field(..., description="ID único do árbitro")
    nome: str = Field(..., description="Nome do árbitro")
    pais: Optional[str] = Field(None, description="País do árbitro")
    media_amarelos: float = Field(
        ...,
        ge=0,
        description="Média de cartões amarelos por partida"
    )
    media_vermelhos: float = Field(
        ...,
        ge=0,
        description="Média de cartões vermelhos por partida"
    )
    total_jogos: int = Field(
        ...,
        ge=0,
        description="Total de jogos apitados na competição"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "nome": "Michael Oliver",
                "pais": "England",
                "media_amarelos": 3.5,
                "media_vermelhos": 0.2,
                "total_jogos": 15
            }
        }
```

---

## 4. Modelos de Competição

### 4.1 CompeticaoInfo

```python
# app/models/competicao.py
from pydantic import BaseModel, Field

class CompeticaoInfo(BaseModel):
    """Informações de uma competição."""

    id: str = Field(
        ...,
        description="ID único da competição na VStats API"
    )
    nome: str = Field(
        ...,
        max_length=100,
        description="Nome da competição (ex: Premier League 2025/26)"
    )
    pais: str = Field(
        ...,
        max_length=50,
        description="País da competição"
    )
    tipo: str = Field(
        ...,
        description="Tipo de competição (liga, copa, etc)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "51r6ph2woavlbbpk8f29nynf8",
                "nome": "Premier League 2025/26",
                "pais": "Inglaterra",
                "tipo": "Liga"
            }
        }
```

---

## 5. Modelos de Escudo

### 5.1 EscudoResponse

```python
# app/models/escudo.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class EscudoResponse(BaseModel):
    """Response para GET /api/time/{teamId}/escudo."""

    escudo: Optional[str] = Field(
        None,
        description="URL do escudo/logo do time"
    )
    nome_time: Optional[str] = Field(
        None,
        description="Nome do time (obtido via escudo)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "escudo": "https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png",
                "nome_time": "Arsenal"
            }
        }
```

---

## 6. Modelos da API VStats (Mapeamento Externo)

Estes modelos mapeiam respostas da API VStats para estruturas internas.

### 6.1 VStatsMatch

```python
# app/models/vstats.py
from pydantic import BaseModel, Field
from typing import Optional

class VStatsMatch(BaseModel):
    """Partida retornada pela API VStats."""

    id: str = Field(alias='Fx', description="Match ID")
    localDate: str = Field(description="Data no formato YYYY-MM-DD")
    kickoffTime: str = Field(description="Horário no formato HH:MM")
    homeTeamId: str = Field(description="ID do time mandante")
    awayTeamId: str = Field(description="ID do time visitante")
    homeTeamName: str = Field(description="Nome do time mandante")
    awayTeamName: str = Field(description="Nome do time visitante")
    homeTeamCode: str = Field(description="Código do time mandante")
    awayTeamCode: str = Field(description="Código do time visitante")
    venueName: str = Field(description="Nome do estádio")
    tournamentCalendarName: str = Field(description="Nome do torneio")

    class Config:
        populate_by_name = True  # Permite alias
        json_schema_extra = {
            "example": {
                "Fx": "f4vscquffy37afgv0arwcbztg",
                "localDate": "2025-12-27",
                "kickoffTime": "17:00",
                "homeTeamId": "4dsgumo7d4zupm2ugsvm4zm4d",
                "awayTeamId": "1c8m2ko0wxq1asfkuykurdr0y",
                "homeTeamName": "Arsenal",
                "awayTeamName": "Crystal Palace",
                "homeTeamCode": "ARS",
                "awayTeamCode": "CRY",
                "venueName": "Emirates Stadium",
                "tournamentCalendarName": "Premier League"
            }
        }
```

### 6.2 VStatsSeasonStats

```python
class VStatsSeasonStats(BaseModel):
    """Estatísticas de temporada da API VStats."""

    goals: float = Field(description="Gols feitos")
    goalsConceded: float = Field(description="Gols sofridos")
    wonCorners: float = Field(description="Escanteios a favor")
    totalShotsPerMatch: float = Field(description="Total de chutes por partida")
    shotsOnTarget: float = Field(description="Chutes ao gol")
    totalYellowCard: float = Field(description="Cartões amarelos")
    totalRedCard: float = Field(description="Cartões vermelhos")

    class Config:
        populate_by_name = True
```

---

## 7. Modelos de Erro

### 7.1 ErrorResponse

```python
# app/models/error.py
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    """Response padrão para erros."""

    detail: str = Field(
        ...,
        description="Descrição do erro"
    )
    status_code: int = Field(
        ...,
        description="HTTP Status Code"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Data inválida: 2025-13-01",
                "status_code": 400
            }
        }
```

---

## 8. Guia de Uso nos Routes

```python
# app/api/routes/stats.py
from fastapi import APIRouter, Query
from app.models.estatisticas import StatsResponse
from app.models.error import ErrorResponse

router = APIRouter(prefix="/api", tags=["stats"])

@router.get(
    "/partida/{matchId}/stats",
    response_model=StatsResponse,
    responses={
        200: {"description": "Estatísticas calculadas com sucesso"},
        400: {"model": ErrorResponse, "description": "Parâmetros inválidos"},
        404: {"model": ErrorResponse, "description": "Partida não encontrada"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_stats(
    matchId: str = Path(..., description="ID da partida"),
    filtro: Literal["geral", "5", "10"] = Query("geral", description="Período de análise")
) -> StatsResponse:
    """
    Busca estatísticas detalhadas de uma partida.

    - **matchId**: ID único da partida
    - **filtro**: "geral" (toda temporada), "5" (últimas 5 partidas), "10" (últimas 10 partidas)
    """
    pass
```

---

## 9. Conversão entre Modelos

```python
# app/services/converter.py
from app.models.vstats import VStatsMatch
from app.models.partida import PartidaResumo, TimeInfo
from datetime import datetime

def converter_vstats_para_partida_resumo(
    vstats_match: VStatsMatch,
    escudo_mandante: str = None,
    escudo_visitante: str = None
) -> PartidaResumo:
    """Converte resposta VStats para PartidaResumo."""

    return PartidaResumo(
        id=vstats_match.id,
        data=datetime.strptime(vstats_match.localDate, "%Y-%m-%d").date(),
        horario=datetime.strptime(vstats_match.kickoffTime, "%H:%M").time(),
        competicao=vstats_match.tournamentCalendarName,
        estadio=vstats_match.venueName,
        mandante=TimeInfo(
            id=vstats_match.homeTeamId,
            nome=vstats_match.homeTeamName,
            codigo=vstats_match.homeTeamCode,
            escudo=escudo_mandante
        ),
        visitante=TimeInfo(
            id=vstats_match.awayTeamId,
            nome=vstats_match.awayTeamName,
            codigo=vstats_match.awayTeamCode,
            escudo=escudo_visitante
        )
    )
```

---

## 10. Validações Customizadas

### 10.1 Validar Data Válida

```python
from pydantic import field_validator
from datetime import datetime

@field_validator('data')
@classmethod
def validar_data(cls, v):
    """Data não pode ser anterior a 2024."""
    if v.year < 2024:
        raise ValueError('Data deve ser 2024 ou posterior')
    return v
```

### 10.2 Validar Filtro

```python
@field_validator('filtro_aplicado')
@classmethod
def validar_filtro(cls, v):
    """Filtro deve ser um dos permitidos."""
    permitidos = ['geral', '5', '10']
    if v not in permitidos:
        raise ValueError(f'Filtro deve ser um de {permitidos}')
    return v
```

---

## 11. Exportar Modelos

```python
# app/models/__init__.py
from .partida import (
    TimeInfo,
    PartidaResumo,
    PartidaListResponse
)
from .estatisticas import (
    EstatisticaMetrica,
    EstatisticaFeitos,
    EstatisticasTime,
    StatsResponse
)
from .competicao import CompeticaoInfo
from .escudo import EscudoResponse
from .error import ErrorResponse

__all__ = [
    'TimeInfo',
    'PartidaResumo',
    'PartidaListResponse',
    'EstatisticaMetrica',
    'EstatisticaFeitos',
    'EstatisticasTime',
    'StatsResponse',
    'CompeticaoInfo',
    'EscudoResponse',
    'ErrorResponse'
]
```

---

## 12. Testes de Modelos

```python
# tests/unit/test_models.py
import pytest
from app.models.partida import TimeInfo, PartidaResumo
from app.models.estatisticas import EstatisticaMetrica
from datetime import date, time

def test_time_info_valido():
    """TimeInfo com dados válidos."""
    time = TimeInfo(
        id="123",
        nome="Arsenal",
        codigo="ARS"
    )
    assert time.id == "123"
    assert time.nome == "Arsenal"

def test_time_info_id_vazio():
    """TimeInfo com ID vazio deve falhar."""
    with pytest.raises(ValueError):
        TimeInfo(
            id="",  # Vazio
            nome="Arsenal",
            codigo="ARS"
        )

def test_estatistica_metrica_cv_negativo():
    """CV negativo deve ser rejeitado."""
    with pytest.raises(ValueError):
        EstatisticaMetrica(
            media=5.0,
            cv=-0.5,  # CV negativo
            classificacao="Estável"
        )

def test_estatistica_metrica_classificacao_automatica():
    """Classificação deve ser calculada automaticamente."""
    metric = EstatisticaMetrica(
        media=5.0,
        cv=0.10  # < 0.15
    )
    assert metric.classificacao == "Muito Estável"
```

---

## Referências

- **Pydantic Docs:** https://docs.pydantic.dev/latest/
- **FastAPI Models:** https://fastapi.tiangolo.com/tutorial/body/
- **JSON Schema:** https://json-schema.org/

---

## Ver Também

Para entender como os modelos são utilizados no sistema, consulte:

- **[ARQUITETURA_BACKEND.md](ARQUITETURA_BACKEND.md)** - Onde os models se encaixam na arquitetura em camadas
- **[API_SPECIFICATION.md](API_SPECIFICATION.md)** - Endpoints que usam esses schemas de request/response
- **[openapi.yaml](../openapi.yaml)** - Especificação OpenAPI 3.0 gerada automaticamente pelo FastAPI
- **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)** - Como testar validações e transformações de modelos
- **[LOCAL_SETUP.md](LOCAL_SETUP.md)** - Como rodar a API para testar os modelos
- **[tests/README.md](../tests/README.md)** - Exemplos práticos de testes para validações Pydantic

**Próximos Passos Recomendados:**
1. Entenda como esses models se encaixam na arquitetura consultando [ARQUITETURA_BACKEND.md](ARQUITETURA_BACKEND.md)
2. Veja quais endpoints usam esses schemas em [API_SPECIFICATION.md](API_SPECIFICATION.md)
3. Estude como testar validadores consultando [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
4. Implemente testes seguindo padrões em [tests/README.md](../tests/README.md)
