# Modelos de Dados - Pydantic Schemas

**Versão:** 1.6
**Data:** 07 de fevereiro de 2026
**Framework:** Pydantic v2.x (com FastAPI)

---

## 1. Visão Geral

Este documento define todos os modelos Pydantic (schemas/DTOs) usados na API. Pydantic valida automaticamente os tipos de dados e serializa/desserializa JSON.

**Estrutura de Pastas:**

```
app/models/
├── __init__.py              # Importa todos os modelos
├── partida.py               # TimeInfo, PartidaResumo, PartidaListResponse
├── estatisticas.py          # EstatisticaMetrica, EstatisticasTime, StatsResponse (+ contexto/H2H)
├── contexto.py              # ContextoPartida, ContextoTime, H2HInfo, ClassificacaoTimeInfo
├── analysis.py              # DTOs de previsões e over/under (payload do /analysis)
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
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class EstatisticaMetrica(BaseModel):
    """Métrica com média, CV, classificação calibrada e estabilidade (0-100)."""

    media: float = Field(..., ge=0, description="Valor médio")
    cv: float = Field(..., ge=0, description="Coeficiente de Variação (CV)")
    classificacao: Literal[
        "Muito Estável",
        "Estável",
        "Moderado",
        "Instável",
        "Muito Instável",
        "N/A",
    ] = Field(..., description="Classificação baseada no CV calibrado")
    estabilidade: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Estabilidade em porcentagem (0-100%, onde 100% = muito estável).",
    )

    @field_validator("media", "cv")
    @classmethod
    def arredondar(cls, v: float) -> float:
        return round(v, 2)

    model_config = {
        "json_schema_extra": {
            "example": {
                "media": 5.88,
                "cv": 0.32,
                "classificacao": "Estável",
                "estabilidade": 68,
            }
        }
    }
```

**Nota:** a classificação/estabilidade são calculadas no `StatsService` (não são inferidas no schema).

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
    cartoes_amarelos: EstatisticaMetrica = Field(..., description="Cartões amarelos")
    faltas: EstatisticaMetrica = Field(..., description="Faltas cometidas")

    model_config = {
        "json_schema_extra": {
            "example": {
                "escanteios": {
                    "feitos": {"media": 5.88, "cv": 0.32, "classificacao": "Moderado", "estabilidade": 58},
                    "sofridos": {"media": 3.50, "cv": 0.28, "classificacao": "Estável", "estabilidade": 63}
                },
                "gols": {
                    "feitos": {"media": 1.82, "cv": 0.41, "classificacao": "Moderado", "estabilidade": 49},
                    "sofridos": {"media": 0.59, "cv": 0.65, "classificacao": "Instável", "estabilidade": 40}
                },
                "finalizacoes": {
                    "feitos": {"media": 10.82, "cv": 0.25, "classificacao": "Estável", "estabilidade": 54},
                    "sofridos": {"media": 8.20, "cv": 0.35, "classificacao": "Moderado", "estabilidade": 36}
                },
                "finalizacoes_gol": {
                    "feitos": {"media": 4.50, "cv": 0.30, "classificacao": "Moderado", "estabilidade": 62},
                    "sofridos": {"media": 2.80, "cv": 0.40, "classificacao": "Moderado", "estabilidade": 50}
                },
                "cartoes_amarelos": {"media": 1.29, "cv": 0.55, "classificacao": "Instável", "estabilidade": 47},
                "faltas": {"media": 12.4, "cv": 0.40, "classificacao": "Moderado", "estabilidade": 27}
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
    estatisticas: EstatisticasTime = Field(..., description="Estatísticas agregadas do time")
    recent_form: List[Literal["W", "D", "L"]] = Field(
        default_factory=list,
        description="Sequência de resultados recentes (W=Win, D=Draw, L=Loss)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "4dsgumo7d4zupm2ugsvm4zm4d",
                "nome": "Arsenal",
                "escudo": "https://...",
                "estatisticas": { },
                "recent_form": ["W", "D", "W", "L", "W"]
            }
        }
    }
```

**Campo `recent_form`:**
- Array de resultados recentes do time (mais recente primeiro)
- Valores: `"W"` (Vitória), `"D"` (Empate), `"L"` (Derrota)
- Calculado a partir de `goals` vs `goalsConceded` de cada partida
- Limitado pelo filtro: `geral` (até 50), `5` (até 5), `10` (até 10). Se não houver N jogos, usa as partidas disponíveis.

---

### 3.5 StatsResponse

```python
class StatsResponse(BaseModel):
    """Response para GET /api/partida/{matchId}/stats."""

    partida: PartidaResumo = Field(..., description="Metadados da partida")
    filtro_aplicado: Literal["geral", "5", "10"] = Field(..., description="Período analisado")
    partidas_analisadas: int = Field(..., ge=1, description="N efetivo usado nas previsões (menor lado)")

    # Contagem real por lado (especialmente relevante com subfiltro de mando).
    partidas_analisadas_mandante: Optional[int] = Field(default=None, ge=0)
    partidas_analisadas_visitante: Optional[int] = Field(default=None, ge=0)

    mandante: TimeComEstatisticas = Field(..., description="Estatísticas do mandante")
    visitante: TimeComEstatisticas = Field(..., description="Estatísticas do visitante")

    arbitro: Optional[ArbitroInfo] = Field(None, description="Informações do árbitro (best-effort)")
    contexto: Optional[ContextoPartida] = Field(None, description="Contexto pré-jogo (standings, descanso, H2H, etc.)")
    h2h_all_comps: Optional[H2HInfo] = Field(None, description="H2H em todas competições (ajuste leve do modelo)")

    # Apenas quando debug=1 (no endpoint /analysis):
    debug_amostra: Optional[DebugAmostra] = Field(default=None, description="IDs/datas/pesos usados no recorte por lado")

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

**Campo `debug_amostra` (quando `debug=1` em `/analysis`):**
- Exibe a amostra efetiva usada no cálculo por lado (mandante/visitante)
- Inclui `match_ids`, `match_dates` e `weights` (time-weighting)
- Quando o backend cai em fallback de temporada, `source="seasonstats_fallback"` e os arrays podem estar vazios (não há partidas individuais)

#### Estrutura (resumo)

```python
class DebugAmostraTime(BaseModel):
    source: Literal["matches", "seasonstats_fallback"]
    limit: int
    periodo: Literal["integral", "1T", "2T"]
    mando: Optional[Literal["casa", "fora"]]
    n_used: int
    match_ids: List[str]
    match_dates: List[Optional[str]]  # YYYY-MM-DD
    weights: List[float]
    reason: Optional[str] = None


class DebugAmostra(BaseModel):
    mandante: DebugAmostraTime
    visitante: DebugAmostraTime
```

---

## 3.6 ArbitroInfo

```python
class ArbitroInfo(BaseModel):
    """Informações do árbitro com estatísticas de competição E temporada."""

    id: str = Field(..., description="ID único do árbitro")
    nome: str = Field(..., description="Nome do árbitro")
    partidas: int = Field(
        ...,
        ge=0,
        description="Partidas apitadas NA COMPETIÇÃO específica"
    )
    partidas_temporada: int = Field(
        ...,
        ge=0,
        description="Total de partidas na TEMPORADA (todas competições)"
    )
    media_cartoes_amarelos: float = Field(
        ...,
        ge=0,
        description="Média de cartões amarelos por jogo NA COMPETIÇÃO"
    )
    media_cartoes_temporada: float = Field(
        ...,
        ge=0,
        description="Média ponderada de cartões na TEMPORADA"
    )
    media_faltas: Optional[float] = Field(
        None,
        ge=0,
        description="Média de faltas por jogo"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "3e8y9u6dcbjomw0ucdbxi3c44",
                "nome": "A. Zanotti",
                "partidas": 2,
                "partidas_temporada": 9,
                "media_cartoes_amarelos": 0.5,
                "media_cartoes_temporada": 3.77,
                "media_faltas": 26.0
            }
        }
```

**Cálculo da Média Ponderada (temporada):**
```
media_cartoes_temporada = Σ(partidas × média_cartões) / Σ(partidas)
```

**Exemplo:**
- Serie B: 2 jogos × 0.5 = 1 cartão
- Coppa Italia: 4 jogos × 5.0 = 20 cartões
- Serie A: 3 jogos × 4.0 = 12 cartões
- **Total:** (1 + 20 + 12) / 9 = 3.67 cartões/jogo na temporada

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
    filtro: Literal["geral", "5", "10"] = Query("geral", description="Período de análise"),
    periodo: Literal["integral", "1T", "2T"] = Query("integral", description="Tempo do jogo (integral, 1º tempo, 2º tempo)"),
    home_mando: Optional[Literal["casa", "fora"]] = Query(None, description="Filtro casa/fora do mandante"),
    away_mando: Optional[Literal["casa", "fora"]] = Query(None, description="Filtro casa/fora do visitante")
) -> StatsResponse:
    """
    Busca estatísticas detalhadas de uma partida.

    - **matchId**: ID único da partida
    - **filtro**: "geral" (até 50 jogos disputados), "5" (últimas até 5), "10" (últimas até 10)
    - **periodo**: "integral" (jogo completo), "1T" (1º tempo), "2T" (2º tempo)
    - **home_mando**: "casa" ou "fora" para filtrar jogos do mandante (opcional)
    - **away_mando**: "casa" ou "fora" para filtrar jogos do visitante (opcional)
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

## 13. Modelos de Busca Inteligente (Frontend)

Modelos TypeScript usados exclusivamente no frontend para a funcionalidade de Busca Inteligente.

### 13.1 TimeResumo

```typescript
// src/types/smartSearch.ts

export interface TimeResumo {
  id: string;
  nome: string;
  escudo: string | null;
}
```

### 13.2 Oportunidade

```typescript
export type ConfiancaLabel = 'Alta' | 'Média' | 'Baixa';

export interface Oportunidade {
  matchId: string;
  mandante: TimeResumo;
  visitante: TimeResumo;
  competicao: string;
  horario: string;
  estatistica: string;        // 'gols', 'escanteios', etc.
  estatisticaLabel: string;   // 'Gols', 'Escanteios', etc.
  tipo: 'over' | 'under';
  linha: number;              // ex: 2.5
  probabilidade: number;      // 0.0-1.0
  confianca: number;          // CV convertido (0.0-1.0)
  confiancaLabel: ConfiancaLabel;
  score: number;              // confiança × probabilidade
}
```

**Campo `score`:**
- Fórmula: `score = confiança × probabilidade`
- Range: 0.0 a 1.0
- Usado para ranquear oportunidades

### 13.3 SmartSearchResult

```typescript
export interface SmartSearchResult {
  partidas_analisadas: number;
  partidas_com_oportunidades: number;
  total_oportunidades: number;
  oportunidades: Oportunidade[];  // Ranqueadas por score
  timestamp: string;              // ISO 8601
}
```

### 13.4 SmartSearchProgress

```typescript
export interface SmartSearchProgress {
  total: number;        // Total de partidas a analisar
  analisadas: number;   // Partidas já processadas
  porcentagem: number;  // % concluído (0-100)
}
```

### 13.5 STAT_THRESHOLDS

```typescript
export interface StatThresholds {
  overMin: number;       // Probabilidade mínima para Over (0.60-0.65)
  underMin: number;      // Probabilidade mínima para Under (0.70-0.75)
  confiancaMin: number;  // Confiança mínima (0.70)
}

export const STAT_THRESHOLDS: Record<string, StatThresholds> = {
  gols: { overMin: 0.60, underMin: 0.70, confiancaMin: 0.70 },
  escanteios: { overMin: 0.60, underMin: 0.75, confiancaMin: 0.70 },
  finalizacoes: { overMin: 0.60, underMin: 0.70, confiancaMin: 0.70 },
  finalizacoes_gol: { overMin: 0.60, underMin: 0.70, confiancaMin: 0.70 },
  cartoes_amarelos: { overMin: 0.65, underMin: 0.75, confiancaMin: 0.70 },
  faltas: { overMin: 0.60, underMin: 0.70, confiancaMin: 0.70 },
};
```

### 13.6 STAT_LABELS

```typescript
export const STAT_LABELS: Record<string, string> = {
  gols: 'Gols',
  escanteios: 'Escanteios',
  finalizacoes: 'Finalizações',
  finalizacoes_gol: 'Finalizações no Gol',
  cartoes_amarelos: 'Cartões Amarelos',
  faltas: 'Faltas',
};
```

### 13.7 Constantes de Análise

```typescript
// Limites de probabilidade
const PROBABILITY_CUTOFF = 0.98;  // Descarta linhas muito óbvias
const MIN_EDGE = 0.30;            // Edge mínimo (|over - under|)
const MAX_OPPORTUNITIES = 999;    // Exibe todas oportunidades
```

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
