"""
Modelos de Estatisticas
=======================

Schemas para estatisticas de times e partidas.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, computed_field, field_validator

from .partida import PartidaResumo
from .contexto import ContextoPartida, H2HInfo


class EstatisticaMetrica(BaseModel):
    """Metrica de estatistica com media, CV, classificacao e estabilidade."""

    media: float = Field(..., ge=0, description="Valor medio")
    cv: float = Field(..., ge=0, description="Coeficiente de Variacao")
    classificacao: Literal[
        "Muito Estável",
        "Estável",
        "Moderado",
        "Instável",
        "Muito Instável",
        "N/A",
    ] = Field(..., description="Classificacao baseada no CV calibrado")
    estabilidade: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Estabilidade em porcentagem (0-100%, onde 100% = muito estavel)",
    )

    @field_validator("media", "cv")
    @classmethod
    def arredondar(cls, v: float) -> float:
        """Arredonda para 2 casas decimais."""
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


class EstatisticaFeitos(BaseModel):
    """Estatisticas feitas vs sofridas."""

    feitos: EstatisticaMetrica = Field(..., description="Estatistica feita pelo time")
    sofridos: EstatisticaMetrica = Field(
        ..., description="Estatistica sofrida pelo time"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "feitos": {"media": 5.88, "cv": 0.32, "classificacao": "Moderado"},
                "sofridos": {"media": 3.50, "cv": 0.28, "classificacao": "Estável"},
            }
        }
    }


class EstatisticasTime(BaseModel):
    """Todas as estatisticas de um time."""

    escanteios: EstatisticaFeitos = Field(..., description="Escanteios")
    gols: EstatisticaFeitos = Field(..., description="Gols")
    finalizacoes: EstatisticaFeitos = Field(..., description="Finalizacoes totais")
    finalizacoes_gol: EstatisticaFeitos = Field(..., description="Finalizacoes no gol")
    cartoes_amarelos: EstatisticaMetrica = Field(..., description="Cartoes amarelos")
    faltas: EstatisticaMetrica = Field(..., description="Faltas cometidas")
    # cartoes_vermelhos removido - evento muito raro para analise de CV


class TimeComEstatisticas(BaseModel):
    """Time com suas estatisticas."""

    id: str = Field(..., description="ID do time")
    nome: str = Field(..., description="Nome do time")
    escudo: Optional[str] = Field(None, description="URL do escudo")
    estatisticas: EstatisticasTime = Field(..., description="Estatisticas do time")
    recent_form: List[Literal["W", "D", "L"]] = Field(
        default_factory=list,
        description="Sequencia de resultados recentes (W=win, D=draw, L=loss)",
    )


class ArbitroInfo(BaseModel):
    """Informacoes do arbitro da partida com estatisticas."""

    id: str = Field(..., description="ID do arbitro")
    nome: str = Field(..., description="Nome do arbitro")
    partidas: int = Field(..., ge=0, description="Partidas apitadas na competicao")
    partidas_temporada: int = Field(
        ..., ge=0, description="Total de partidas na temporada (todas competicoes)"
    )
    media_cartoes_amarelos: float = Field(
        ..., ge=0, description="Media de cartoes amarelos por jogo na competicao"
    )
    media_cartoes_temporada: float = Field(
        ..., ge=0, description="Media ponderada de cartoes na temporada"
    )
    media_faltas: Optional[float] = Field(
        None, ge=0, description="Media de faltas por jogo"
    )

    @field_validator(
        "media_cartoes_amarelos",
        "media_cartoes_temporada",
        "media_faltas",
        mode="before",
    )
    @classmethod
    def parse_float(cls, v):
        """Converte string para float se necessario."""
        if v is None:
            return None
        try:
            return round(float(v), 2)
        except (TypeError, ValueError):
            return 0.0


DebugSampleSource = Literal["matches", "seasonstats_fallback"]


class DebugAmostraTime(BaseModel):
    """Metadados do recorte usado para calcular stats de um time (debug=1)."""

    source: DebugSampleSource = Field(
        ..., description="Origem da amostra: partidas individuais ou fallback seasonstats"
    )
    limit: int = Field(
        ..., ge=0, description="Limite solicitado (5/10/50), antes de dedupe/falhas"
    )
    periodo: Literal["integral", "1T", "2T"] = Field(
        ..., description="Periodo solicitado para extração"
    )
    mando: Optional[Literal["casa", "fora"]] = Field(
        default=None,
        description="Subfiltro de mando aplicado ao time (casa/fora) ou None",
    )
    n_used: int = Field(
        ..., ge=0, description="Tamanho efetivo da amostra usada no cálculo"
    )
    match_ids: List[str] = Field(
        default_factory=list, description="IDs das partidas efetivamente usadas"
    )
    match_dates: List[Optional[str]] = Field(
        default_factory=list,
        description="Datas (YYYY-MM-DD) alinhadas com match_ids (pode conter None)",
    )
    weights: List[float] = Field(
        default_factory=list, description="Pesos temporais alinhados com match_ids"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Motivo do fallback/ajuste (opcional; útil para auditoria)",
    )


class DebugAmostra(BaseModel):
    """Amostra usada por lado para o cálculo das estatísticas (debug=1)."""

    mandante: DebugAmostraTime
    visitante: DebugAmostraTime


class StatsResponse(BaseModel):
    """Response para GET /api/partida/{matchId}/stats."""

    partida: PartidaResumo = Field(..., description="Informacoes da partida")
    filtro_aplicado: Literal["geral", "5", "10"] = Field(
        ..., description="Periodo analisado"
    )
    partidas_analisadas: int = Field(
        ..., ge=1, description="Numero de partidas usadas no calculo"
    )
    # Contagem real por lado (especialmente relevante quando há subfiltro de mando).
    # Mantemos opcionais para retrocompatibilidade em testes/consumidores antigos.
    partidas_analisadas_mandante: Optional[int] = Field(
        default=None,
        ge=0,
        description="Numero de partidas usadas para o mandante (pode diferir por subfiltros)",
    )
    partidas_analisadas_visitante: Optional[int] = Field(
        default=None,
        ge=0,
        description="Numero de partidas usadas para o visitante (pode diferir por subfiltros)",
    )
    mandante: TimeComEstatisticas = Field(
        ..., description="Estatisticas do time mandante"
    )
    visitante: TimeComEstatisticas = Field(
        ..., description="Estatisticas do time visitante"
    )
    arbitro: Optional[ArbitroInfo] = Field(
        None, description="Informacoes do arbitro da partida"
    )
    # Contexto pre-jogo (standings, descanso, H2H etc.).
    contexto: Optional[ContextoPartida] = None
    # H2H em todas competicoes (usado pelo AnalysisService para ajuste leve).
    h2h_all_comps: Optional[H2HInfo] = None
    # Transparência (quando debug=1): quais partidas entraram no cálculo por lado.
    debug_amostra: Optional[DebugAmostra] = None

    @computed_field  # type: ignore[misc]
    @property
    def amostra_suficiente(self) -> bool:
        """True quando a menor amostra por lado >= 3 (mínimo para CV significativo)."""
        counts = [
            v for v in (
                self.partidas_analisadas_mandante,
                self.partidas_analisadas_visitante,
            )
            if v is not None
        ]
        effective = min(counts) if counts else self.partidas_analisadas
        return effective >= 3

    model_config = {
        "json_schema_extra": {
            "example": {
                "partida": {
                    "id": "f4vscquffy37afgv0arwcbztg",
                    "tournament_id": "51r6ph2woavlbbpk8f29nynf8",
                    "data": "2025-12-27",
                    "horario": "17:00:00",
                    "competicao": "Premier League",
                    "estadio": "Emirates Stadium",
                    "mandante": {
                        "id": "4dsgumo7d4zupm2ugsvm4zm4d",
                        "nome": "Arsenal",
                        "codigo": "ARS",
                    },
                    "visitante": {
                        "id": "1c8m2ko0wxq1asfkuykurdr0y",
                        "nome": "Crystal Palace",
                        "codigo": "CRY",
                    },
                },
                "filtro_aplicado": "5",
                "partidas_analisadas": 5,
            }
        }
    }
