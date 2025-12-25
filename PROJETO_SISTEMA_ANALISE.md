# Sistema de Analise de Estatisticas de Futebol

**Versao:** 1.0
**Data:** 24 de Dezembro de 2025
**Fonte dos Dados:** `DOCUMENTACAO_VSTATS_COMPLETA.md`

---

## Indice

1. [Visao Geral do Sistema](#1-visao-geral-do-sistema)
   - 1.3 Notas Importantes sobre a API
2. [Tela: Lista de Partidas](#2-tela-lista-de-partidas)
3. [Tela: Painel de Estatisticas](#3-tela-painel-de-estatisticas)
4. [Logica de Filtros](#4-logica-de-filtros)
5. [Calculos](#5-calculos)
6. [Arquitetura Backend](#6-arquitetura-backend)
7. [Endpoints VStats Utilizados](#7-endpoints-vstats-utilizados)
8. [IDs de Competicoes](#8-ids-de-competicoes)
9. [Cache e Otimizacao](#9-cache-e-otimizacao)
10. [Arquivos a Criar](#10-arquivos-a-criar)
11. [Resumo das Estatisticas](#11-resumo-das-estatisticas)
12. [Scripts de Validacao](#12-scripts-de-validacao)
13. [Proximos Passos](#13-proximos-passos)
14. [Fluxo da Aplicacao](#14-fluxo-da-aplicacao)
15. [Modelo de Previsao de Estatisticas](#15-modelo-de-previsao-de-estatisticas)

---

## 1. VISAO GERAL DO SISTEMA

> **Referencia:** Secoes 4.11-4.12 da `DOCUMENTACAO_VSTATS_COMPLETA.md`

### 1.1 Objetivo do Sistema

Sistema web para analise estatistica de partidas de futebol, permitindo ao usuario:

- Visualizar partidas agendadas para qualquer data
- Analisar estatisticas detalhadas de cada confronto
- Comparar desempenho de mandante vs visitante
- Filtrar por diferentes periodos (temporada completa, ultimas 5 ou 10 partidas)
- Avaliar estabilidade das equipes via Coeficiente de Variacao (CV)

### 1.2 Stack Tecnologica

| Camada | Tecnologia |
|--------|------------|
| Frontend | React + TypeScript |
| Backend | Python + FastAPI |
| Dados Primarios | VStats API (Opta/Stats Perform) |
| Escudos | TheSportsDB (API gratuita) |

### 1.3 Notas Importantes sobre a API (Verificado 25/12/2025)

> **CRITICO:** Algumas limitacoes da VStats API que impactam a implementacao:

| Endpoint | Problema | Solucao |
|----------|----------|---------|
| `schedule/day?date=` | Parametro `date` retorna array vazio | Usar `schedule/month` e filtrar client-side |
| `schedule/month?month=&year=` | Parametros `month` e `year` sao **IGNORADOS** | Endpoint sempre retorna mes atual |
| `seasonstats` | Nao fornece `lostCorners` (corners sofridos) | Usar `get-match-stats` por partida |

#### DESCOBERTA IMPORTANTE (25/12/2025): Endpoint /schedule (Temporada Completa)

> **CRITICO:** O endpoint `/schedule` **SEM sufixo** retorna TODA a temporada!

| Endpoint | Retorno | Quantidade |
|----------|---------|------------|
| `/stats/tournament/v1/schedule?tmcl={id}` | Temporada COMPLETA | ~380 jogos (Ago-Mai) |
| `/stats/tournament/v1/schedule/month?Tmcl={id}` | Apenas mes atual | ~16 jogos |
| `/stats/tournament/v1/schedule/week?tmcl={id}` | Apenas semana atual | ~10 jogos |

**Vantagens do /schedule:**
- Acesso a TODAS as partidas (passadas e futuras)
- Permite buscar ultimas 5/10 partidas de qualquer time
- Dados incluem placar (`homeScore`, `awayScore`) para partidas realizadas
- Resolve problema de "poucas partidas no mes atual"

**Uso recomendado para filtros 5/10:**
```python
# Buscar temporada completa
GET /stats/tournament/v1/schedule?tmcl={tournamentId}

# Filtrar client-side:
# 1. Partidas do time (homeContestantId ou awayContestantId)
# 2. Partidas realizadas (homeScore != null)
# 3. Ordenar por data decrescente
# 4. Pegar ultimas N
```

**Recomendacao de Implementacao:**

```python
# NAO FAZER (nao funciona):
GET /schedule/day?date=2025-12-27  # Retorna vazio

# FAZER para partidas do DIA (funciona):
GET /schedule/month?Tmcl={id}      # Retorna mes atual
GET /schedule/week?tmcl={id}       # Retorna semana atual

# FAZER para HISTORICO COMPLETO (filtros 5/10):
GET /schedule?tmcl={id}            # Retorna temporada inteira!

# Filtrar no codigo:
partidas_do_dia = [m for m in todas_partidas if m['localDate'] == data_desejada]
```

**Fluxo Correto para Buscar Partidas por Data:**
1. Chamar `schedule/month` ou `schedule/week`
2. Filtrar array `matches` pela `localDate` desejada
3. Cachear resultado por 1 hora (partidas nao mudam frequentemente)

**Fluxo Correto para Buscar Historico (Filtros 5/10):**
1. Chamar `schedule` (sem sufixo) para temporada completa
2. Filtrar por `contestantId` (home ou away)
3. Filtrar partidas realizadas (`homeScore != null`)
4. Ordenar por `localDate` decrescente
5. Pegar ultimas N partidas
6. Cachear schedule completo por 6 horas

---

### 1.4 Fluxo Principal do Usuario

```
[TELA 1: HOME]
     |
     +-- Seletor de data (datepicker)
     +-- Botao "Gerar Partidas"
     |
     v
[TELA 2: LISTA DE PARTIDAS]
     |
     +-- Cards visuais centralizados
     +-- Escudo + Nome dos times
     +-- Horario e competicao
     +-- Clicar no card abre detalhes
     |
     v
[TELA 3: PAINEL DE ESTATISTICAS]
     |
     +-- Cabecalho: [Filtro: Geral | 5 | 10]
     +-- Lado Esquerdo: MANDANTE
     |      +-- Escudo abaixo do nome
     |      +-- Estatisticas (media + CV)
     +-- Lado Direito: VISITANTE
            +-- Escudo abaixo do nome
            +-- Estatisticas (media + CV)
```

### 1.4 Estrutura de Telas

| Tela | Descricao | Dados Necessarios |
|------|-----------|-------------------|
| **Home** | Seletor de data + botao | Nenhum (frontend apenas) |
| **Lista de Partidas** | Cards com partidas do dia | `schedule/day` + TheSportsDB |
| **Painel de Estatisticas** | Comparativo completo | `seasonstats` + `get-match-stats` |

### 1.5 Parametros Globais da API VStats

| Parametro | Significado | Exemplo |
|-----------|-------------|---------|
| `tmcl` | Tournament Calendar ID (temporada) | `51r6ph2woavlbbpk8f29nynf8` |
| `ctst` | Contestant ID (ID do time) | `4dsgumo7d4zupm2ugsvm4zm4d` |
| `Fx` | Match ID (ID da partida) | `f4vscquffy37afgv0arwcbztg` |
| `detailed` | Retornar dados detalhados | `yes` (string, nao boolean!) |

---

## 2. TELA: LISTA DE PARTIDAS

> **Referencia:** Secao 4.3 (Schedule Day) e 7.3 (TheSportsDB) da `DOCUMENTACAO_VSTATS_COMPLETA.md`

### 2.1 Layout do Card de Partida

```
+----------------------------------------------------------+
|                                                          |
|   [ESCUDO]                              [ESCUDO]         |
|                                                          |
|   ARSENAL           vs          CRYSTAL PALACE           |
|                                                          |
|              Emirates Stadium - 17:00                    |
|                 Premier League                           |
|                                                          |
+----------------------------------------------------------+
```

**Caracteristicas do Card:**

- Layout centralizado e responsivo
- Escudos proeminentes acima dos nomes
- Visual limpo com hierarquia clara
- Hover effect para indicar interatividade
- Click abre o painel de estatisticas

### 2.2 Dados do Card (Mapeamento Completo)

| Campo Visual | Campo API | Endpoint | Secao Doc |
|--------------|-----------|----------|-----------|
| Nome Mandante | `homeContestantName` | schedule/day | 4.3 |
| Nome Visitante | `awayContestantName` | schedule/day | 4.3 |
| Codigo Mandante | `homeContestantCode` | schedule/day | 4.3 |
| Codigo Visitante | `awayContestantCode` | schedule/day | 4.3 |
| ID Mandante | `homeContestantId` | schedule/day | 4.3 |
| ID Visitante | `awayContestantId` | schedule/day | 4.3 |
| Escudo Mandante | `strBadge` | TheSportsDB | 7.3 |
| Escudo Visitante | `strBadge` | TheSportsDB | 7.3 |
| Estadio | `venueName` | match-preview | 4.5 |
| Horario Local | `localTime` | schedule/day | 4.3 |
| Data Local | `localDate` | schedule/day | 4.3 |
| Competicao | `tournamentCalendarName` | schedule/day | 4.3 |
| ID da Partida | `id` | schedule/day | 4.3 |

### 2.3 Endpoint Principal: Schedule Day

```http
GET https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/tournament/v1/schedule/day
    ?tmcl={tournamentCalendarId}
    &date={YYYY-MM-DD}
```

**Exemplo Real:**

```http
GET /stats/tournament/v1/schedule/day?tmcl=51r6ph2woavlbbpk8f29nynf8&date=2025-12-27
```

**Resposta Esperada:**

```json
{
  "matches": [
    {
      "id": "f4vscquffy37afgv0arwcbztg",
      "date": "2025-12-27T00:00:00+00:00",
      "localTime": "17:00:00",
      "localDate": "2025-12-27",
      "homeContestantId": "4dsgumo7d4zupm2ugsvm4zm4d",
      "awayContestantId": "1c8m2ko0wxq1asfkuykurdr0y",
      "homeContestantName": "Arsenal",
      "awayContestantName": "Crystal Palace",
      "homeContestantCode": "ARS",
      "awayContestantCode": "CRY",
      "tournamentCalendarName": "Premier League 2025/2026"
    }
  ]
}
```

### 2.4 Fallback: Schedule Month

> **IMPORTANTE:** O parametro `date` no `schedule/day` frequentemente retorna vazio.
> Usar `schedule/month` como fonte principal e filtrar client-side.

```http
GET /stats/tournament/v1/schedule/month?Tmcl={tournamentCalendarId}
```

**Notas:**
- O parametro e `Tmcl` (maiusculo T) no schedule/month!
- **ATENCAO:** Os parametros `month` e `year` sao **IGNORADOS** pela API
- O endpoint sempre retorna o mes **ATUAL**, independente dos parametros
- Para filtrar por data especifica, fazer o filtro no client-side

> **IMPORTANTE - Case-Sensitivity dos Parametros:**
> - `schedule/day` usa parametro `tmcl` (minusculo)
> - `schedule/month` usa parametro `Tmcl` (T maiusculo)
> - `schedule/week` usa parametro `tmcl` (minusculo)
> - Reversao destes valores pode resultar em erro 400/500

**Alternativa - Schedule Week:**
```http
GET /stats/tournament/v1/schedule/week?tmcl={tournamentCalendarId}
```
Retorna partidas da semana atual.

### 2.5 Estrategia para Multiplas Competicoes

Para cobrir todas as 33+ competicoes, iterar sobre os IDs obtidos via:

```http
GET /stats/tournament/v1/calendar?Comp=2kwbbcootiqqgmrzs6o5inle5
```

**Logica:**

```
para cada competicao em lista_competicoes:
    partidas = buscar_schedule_day(competicao.id, data)
    todas_partidas.adicionar(partidas)

ordenar(todas_partidas, por=horario)
```

### 2.6 Obtendo Escudos (TheSportsDB)

> **Referencia:** Secao 7.3 da `DOCUMENTACAO_VSTATS_COMPLETA.md`

```http
GET https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={nome_time}
```

**Resposta:**

```json
{
  "teams": [{
    "strTeam": "Arsenal",
    "strBadge": "https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png",
    "strLogo": "https://r2.thesportsdb.com/images/media/team/logo/...",
    "strLeague": "English Premier League"
  }]
}
```

**Campo para escudo:** `teams[0].strBadge`

**Recomendacao:** Cachear escudos por 7 dias (ver secao 9).

---

## 3. TELA: PAINEL DE ESTATISTICAS

> **Referencia:** Secoes 4.15 (Seasonstats), 4.8 (Get Match Stats) e 7.4 (CV) da `DOCUMENTACAO_VSTATS_COMPLETA.md`

### 3.1 Layout Principal

```
+-----------------------------------------------------------------------+
|                                                                       |
|                    [  Geral  ] [ 5 Partidas ] [ 10 Partidas ]         |
|                                                                       |
+-----------------------------------------------------------------------+
|                                                                       |
|        MANDANTE                              VISITANTE                |
|        =========                             ==========               |
|                                                                       |
|        [ESCUDO]                              [ESCUDO]                 |
|        Arsenal                               Crystal Palace           |
|                                                                       |
+-----------------------------------------------------------------------+
|                                                                       |
|   ESTATISTICA              MANDANTE              VISITANTE            |
|   ============================================================        |
|                                                                       |
|   ESCANTEIOS                                                          |
|   - Feitos:           5.88 (CV: 0.32 Moderado)   4.20 (CV: 0.45)     |
|   - Sofridos:         3.50 (CV: 0.28 Estavel)    5.10 (CV: 0.52)     |
|                                                                       |
|   GOLS                                                                |
|   - Feitos:           1.82 (CV: 0.41 Moderado)   1.20 (CV: 0.55)     |
|   - Sofridos:         0.59 (CV: 0.65 Instavel)   1.40 (CV: 0.48)     |
|                                                                       |
|   FINALIZACOES                                                        |
|   - Feitas:          10.82 (CV: 0.25 Estavel)    8.50 (CV: 0.38)     |
|   - Sofridas:         8.20 (CV: 0.35 Moderado)   9.80 (CV: 0.42)     |
|                                                                       |
|   FINALIZACOES AO GOL                                                 |
|   - Feitas:           4.50 (CV: 0.30 Moderado)   3.20 (CV: 0.45)     |
|   - Sofridas:         2.80 (CV: 0.40 Moderado)   3.50 (CV: 0.38)     |
|                                                                       |
|   CARTOES AMARELOS                                                    |
|   - Recebidos:        1.29 (CV: 0.55 Instavel)   1.80 (CV: 0.62)     |
|                                                                       |
|   CARTOES VERMELHOS                                                   |
|   - Recebidos:        0.12 (CV: 0.85 M.Instavel) 0.20 (CV: 0.90)     |
|                                                                       |
+-----------------------------------------------------------------------+
```

### 3.2 Estatisticas a Exibir

| Categoria | FEITOS (Campo API) | SOFRIDOS (Campo API) |
|-----------|-------------------|---------------------|
| **Escanteios** | `wonCorners` | `lostCorners` |
| **Gols** | `goals` | `goalsConceded` |
| **Finalizacoes** | `Total Shots` | `Total Shots Conceded` |
| **Finalizacoes ao Gol** | `Shots On Target` | `Shots On Conceded Inside/Outside Box` |
| **Cartoes Amarelos** | `totalYellowCard` | - |
| **Cartoes Vermelhos** | `totalRedCard` | - |

> **NOTA (Atualizado 24/12/2025):** Finalizacoes sofridas agora disponiveis diretamente via `Total Shots Conceded` no seasonstats!

### 3.3 Coeficiente de Variacao (CV)

> **Referencia:** Secao 7.4 da `DOCUMENTACAO_VSTATS_COMPLETA.md`

**Formula:** `CV = Desvio Padrao / Media`

| CV | Classificacao | Cor Sugerida | Significado |
|----|---------------|--------------|-------------|
| 0.00 - 0.15 | Muito Estavel | Verde escuro | Time muito consistente |
| 0.15 - 0.30 | Estavel | Verde | Time consistente |
| 0.30 - 0.50 | Moderado | Amarelo | Variacao normal |
| 0.50 - 0.75 | Instavel | Laranja | Time inconsistente |
| 0.75+ | Muito Instavel | Vermelho | Resultados imprevisiveis |

### 3.4 Posicionamento do Escudo

O escudo deve aparecer **abaixo do nome** da equipe, centralizado:

```
    Arsenal
   [ESCUDO]
```

---

## 4. LOGICA DE FILTROS

> **Referencia:** Secoes 4.15 (Seasonstats) e 7.2 (Feitos vs Sofridos) da `DOCUMENTACAO_VSTATS_COMPLETA.md`

### 4.1 Filtro "Geral" (Temporada Completa)

**Endpoint:** `seasonstats/v1/team`

```http
GET /stats/seasonstats/v1/team?ctst={contestantId}&tmcl={tournamentCalendarId}&detailed=yes
```

**Resposta:**

```json
{
  "id": "4dsgumo7d4zupm2ugsvm4zm4d",
  "name": "Arsenal FC",
  "stat": [
    {"name": "Corners Won", "value": "100", "average": 5.88},
    {"name": "Goals", "value": "31", "average": 1.82},
    {"name": "Goals Conceded", "value": "10", "average": 0.59},
    {"name": "Yellow Cards", "value": "22", "average": 1.29},
    {"name": "Total Shots", "value": "184", "average": 10.82},
    {"name": "Shots On Target", "value": "77", "average": 4.53}
  ]
}
```

**Mapeamento de campos seasonstats:**

| Estatistica | Campo seasonstats | Disponivel |
|-------------|-------------------|------------|
| Escanteios Feitos | `Corners Won` | SIM |
| Escanteios Sofridos | - | NAO* |
| Gols Feitos | `Goals` | SIM |
| Gols Sofridos | `Goals Conceded` | SIM |
| Finalizacoes | `Total Shots` | SIM |
| Finalizacoes Sofridas | `Total Shots Conceded` | **SIM** |
| Finalizacoes ao Gol | `Shots On Target ( inc goals )` | SIM |
| Cartoes Amarelos | `Yellow Cards` | SIM |
| Cartoes Vermelhos | `Red Cards` | SIM |

> *Para estatisticas nao disponiveis no seasonstats (apenas escanteios sofridos), usar get-match-stats (ver 4.2)

**Limitacoes do seasonstats (Verificado v5.2+):**

- **NAO fornece** `lostCorners` (corners sofridos) - ver nota abaixo
- ✅ **DISPONIVEL:** `Total Shots Conceded` (finalizacoes sofridas) desde v5.2
- **NAO fornece** CV (Coeficiente de Variacao) - precisa calcular manualmente via partidas individuais
- **OBS:** `get-match-stats` só traz lineUp com stats para partidas JA disputadas; partidas futuras retornam apenas matchInfo/arbitragem

> **Nota sobre Corners Sofridos (Investigado 24/12/2025):**
> A Opta possui o campo `lost_corners` na fonte original. A VStats expõe como `lostCorners`
> por partida no get-match-stats, mas **optou por não agregar** no seasonstats.
> Isso é uma inconsistência da VStats (agregaram `Total Shots Conceded` mas não `Corners Conceded`).
> **Solução:** Para filtro Geral, agregar `lostCorners` manualmente das últimas N partidas.

### 4.2 Filtro "5 Partidas" / "10 Partidas"

**Fluxo Completo (Atualizado 25/12/2025):**

```
1. OBTER IDS DE PARTIDAS ANTERIORES
   --------------------------------
   RECOMENDADO: Via /schedule (temporada completa)
   GET /stats/tournament/v1/schedule?tmcl={tmcl}
   → Retorna TODA a temporada (~380 jogos)
   → Filtrar por contestantId (home ou away)
   → Filtrar partidas realizadas (homeScore != null)
   → Ordenar por data decrescente
   → Pegar ultimas N

   OBSOLETO: Via schedule/month (limitado ao mes atual)
   GET /stats/tournament/v1/schedule/month?Tmcl={tmcl}
   → Retorna apenas mes atual (~16 jogos)
   → PROBLEMA: No inicio do mes pode nao ter 5/10 partidas!

2. PARA CADA PARTIDA (limite 5 ou 10):
   -----------------------------------
   GET /stats/matchstats/v1/get-match-stats?Fx={matchId}
   → liveData.lineUp[].stat[]
   Se lineUp estiver vazio (partida futura ou sem stats), usar fallback:
   GET /stats/matchstats/v1/get-game-played-stats?Fx={matchId}
   → stats (arrays por time: home/away)

3. EXTRAIR ESTATISTICAS
   --------------------
   Para cada partida, extrair:
   - wonCorners
   - lostCorners
   - goals
   - goalsConceded
   - totalScoringAtt
   - ontargetScoringAtt
   - totalYellowCard
   - totalRedCard

4. CALCULAR AGREGADOS
   ------------------
   - Media de cada estatistica
   - Desvio Padrao
   - CV = Desvio Padrao / Media
```

**Campos disponiveis em get-match-stats (por partida):**

| Campo | Descricao | Localizacao |
|-------|-----------|-------------|
| `wonCorners` | Escanteios feitos | `liveData.lineUp[].stat[]` |
| `lostCorners` | Escanteios SOFRIDOS | `liveData.lineUp[].stat[]` |
| `goals` | Gols feitos | `liveData.lineUp[].stat[]` |
| `goalsConceded` | Gols sofridos | `liveData.lineUp[].stat[]` |
| `totalScoringAtt` | Finalizacoes | `liveData.lineUp[].stat[]` |
| `ontargetScoringAtt` | Finalizacoes ao gol | `liveData.lineUp[].stat[]` |
| `totalYellowCard` | Cartoes amarelos | `liveData.lineUp[].stat[]` |
| `totalRedCard` | Cartoes vermelhos | `liveData.lineUp[].stat[]` |
| `saves` | Defesas do goleiro | `liveData.lineUp[].stat[]` |

**Fallback recomendado (partidas JA disputadas):**

Use `get-game-played-stats` quando `lineUp` vier vazio ou sem `stat[]`.  
Mapeamento básico:
- `attempts` → totalScoringAtt (home idx 0 / away idx 1)
- `attemptsOnGoal` → ontargetScoringAtt
- `corners` → wonCorners (home/away) e lostCorners (via oponente)
- `fouls` → fkFoulLost
- `yellowCards` / `redCards` → totalYellowCard / totalRedCard
- `homeScore` / `awayScore` → goals / goalsConceded

### 4.3 Diferenca entre Filtros

| Aspecto | Geral | 5 Partidas | 10 Partidas |
|---------|-------|------------|-------------|
| Fonte | seasonstats | get-match-stats (fallback: get-game-played-stats) | get-match-stats (fallback: get-game-played-stats) |
| Periodo | Temporada toda | Ultimas 5 | Ultimas 10 |
| CV Disponivel | NAO | SIM* | SIM* |
| Corners Sofridos | ❌ NAO | ✅ SIM | ✅ SIM |
| Finalizacoes Sofridas | ✅ **SIM** (Total Shots Conceded) | ✅ SIM | ✅ SIM |
| Requisicoes API | 1 | 5+ | 10+ |
| Performance | Rapido | Moderado | Lento |

*CV só é calculado quando existem partidas jogadas no período (dados por partida).

---

## 5. CALCULOS

> **Referencia:** Secao 7.4 da `DOCUMENTACAO_VSTATS_COMPLETA.md`

### 5.1 Media Simples

```python
def calcular_media(valores: List[int]) -> float:
    """
    Calcula a media aritmetica simples.

    Exemplo:
        valores = [5, 3, 7, 4, 6]
        media = (5 + 3 + 7 + 4 + 6) / 5 = 5.0
    """
    if not valores:
        return 0.0
    return sum(valores) / len(valores)
```

### 5.2 Desvio Padrao

```python
import statistics

def calcular_desvio_padrao(valores: List[int]) -> float:
    """
    Calcula o desvio padrao amostral.

    Minimo de 2 valores para calculo valido.

    Exemplo:
        valores = [5, 3, 7, 4, 6]
        desvio = 1.58 (aproximadamente)
    """
    if len(valores) < 2:
        return 0.0
    return statistics.stdev(valores)
```

### 5.3 Coeficiente de Variacao (CV)

```python
def calcular_cv(valores: List[int]) -> dict:
    """
    Calcula o Coeficiente de Variacao.

    CV = Desvio Padrao / Media

    Quanto MENOR o CV, MAIS ESTAVEL o time.
    Quanto MAIOR o CV, MAIS INSTAVEL o time.

    Retorna:
        {
            "cv": float,
            "classificacao": str
        }
    """
    if len(valores) < 2:
        return {"cv": 0, "classificacao": "N/A"}

    media = statistics.mean(valores)
    desvio = statistics.stdev(valores)

    # Evitar divisao por zero
    cv = desvio / media if media > 0 else 0

    # Classificar
    if cv < 0.15:
        classificacao = "Muito Estavel"
    elif cv < 0.30:
        classificacao = "Estavel"
    elif cv < 0.50:
        classificacao = "Moderado"
    elif cv < 0.75:
        classificacao = "Instavel"
    else:
        classificacao = "Muito Instavel"

    return {"cv": cv, "classificacao": classificacao}
```

**Exemplo de Calculo:**

```
Corners do Arsenal em 5 partidas: [8, 5, 3, 6, 7]

Media = (8 + 5 + 3 + 6 + 7) / 5 = 5.8
Desvio Padrao = 1.92
CV = 1.92 / 5.8 = 0.33

Classificacao: Moderado (0.30 - 0.50)
```

### 5.4 Finalizacoes Sofridas

> **ATUALIZADO (24/12/2025):** O campo `Total Shots Conceded` EXISTE no seasonstats!
> Para filtro "Geral": usar `Total Shots Conceded` direto.
> Para filtros "5/10 partidas": calcular via adversario (get-match-stats).

```python
def calcular_finalizacoes_sofridas(match_ids: List[str], team_id: str) -> List[int]:
    """
    Para cada partida, buscar totalScoringAtt do ADVERSARIO.
    Isso representa as finalizacoes que o time sofreu.

    Logica:
        Em cada partida, ha 2 times no lineUp.
        Buscar o time que NAO e o nosso (adversario).
        Pegar o totalScoringAtt do adversario.
    """
    finalizacoes_sofridas = []

    for match_id in match_ids:
        stats = get_match_stats(match_id)
        lineup = stats['liveData']['lineUp']

        for team in lineup:
            # Identificar o adversario (NAO e o nosso time)
            if team['contestantId'] != team_id:
                for stat in team['stat']:
                    if stat['type'] == 'totalScoringAtt':
                        finalizacoes_sofridas.append(int(stat['value']))
                        break

    return finalizacoes_sofridas
```

---

## 6. ARQUITETURA BACKEND

### 6.1 Endpoints da API Propria

| Metodo | Rota | Descricao | Parametros |
|--------|------|-----------|------------|
| GET | `/api/partidas` | Lista partidas do dia | `data` (YYYY-MM-DD) |
| GET | `/api/partida/{matchId}/stats` | Stats da partida | `filtro` (geral/5/10) |
| GET | `/api/competicoes` | Lista competicoes | - |
| GET | `/api/time/{teamId}/escudo` | Escudo do time | - |

### 6.2 Estrutura de Resposta: Lista de Partidas

```json
{
  "data": "2025-12-27",
  "total_partidas": 15,
  "partidas": [
    {
      "id": "f4vscquffy37afgv0arwcbztg",
      "data": "2025-12-27",
      "horario": "17:00",
      "competicao": "Premier League",
      "estadio": "Emirates Stadium",
      "mandante": {
        "id": "4dsgumo7d4zupm2ugsvm4zm4d",
        "nome": "Arsenal",
        "codigo": "ARS",
        "escudo": "https://r2.thesportsdb.com/.../uyhbfe1612467038.png"
      },
      "visitante": {
        "id": "1c8m2ko0wxq1asfkuykurdr0y",
        "nome": "Crystal Palace",
        "codigo": "CRY",
        "escudo": "https://r2.thesportsdb.com/.../ia6i3m1656014992.png"
      }
    }
  ]
}
```

### 6.3 Estrutura de Resposta: Stats da Partida

```json
{
  "partida": {
    "id": "f4vscquffy37afgv0arwcbztg",
    "data": "2025-12-27",
    "horario": "17:00",
    "competicao": "Premier League",
    "estadio": "Emirates Stadium"
  },
  "filtro_aplicado": "5_partidas",
  "partidas_analisadas": 5,
  "mandante": {
    "id": "4dsgumo7d4zupm2ugsvm4zm4d",
    "nome": "Arsenal",
    "escudo": "https://r2.thesportsdb.com/.../uyhbfe1612467038.png",
    "estatisticas": {
      "escanteios": {
        "feitos": {"media": 5.88, "cv": 0.32, "classificacao": "Moderado"},
        "sofridos": {"media": 3.50, "cv": 0.28, "classificacao": "Estavel"}
      },
      "gols": {
        "feitos": {"media": 1.82, "cv": 0.41, "classificacao": "Moderado"},
        "sofridos": {"media": 0.59, "cv": 0.65, "classificacao": "Instavel"}
      },
      "finalizacoes": {
        "feitas": {"media": 10.82, "cv": 0.25, "classificacao": "Estavel"},
        "sofridas": {"media": 8.20, "cv": 0.35, "classificacao": "Moderado"}
      },
      "finalizacoes_gol": {
        "feitas": {"media": 4.50, "cv": 0.30, "classificacao": "Moderado"},
        "sofridas": {"media": 2.80, "cv": 0.40, "classificacao": "Moderado"}
      },
      "cartoes": {
        "amarelos": {"media": 1.29, "cv": 0.55, "classificacao": "Instavel"},
        "vermelhos": {"media": 0.12, "cv": 0.85, "classificacao": "Muito Instavel"}
      }
    }
  },
  "visitante": {
    "id": "1c8m2ko0wxq1asfkuykurdr0y",
    "nome": "Crystal Palace",
    "escudo": "https://r2.thesportsdb.com/.../ia6i3m1656014992.png",
    "estatisticas": {
      "escanteios": {
        "feitos": {"media": 4.20, "cv": 0.45, "classificacao": "Moderado"},
        "sofridos": {"media": 5.10, "cv": 0.52, "classificacao": "Instavel"}
      },
      "gols": {
        "feitos": {"media": 1.20, "cv": 0.55, "classificacao": "Instavel"},
        "sofridos": {"media": 1.40, "cv": 0.48, "classificacao": "Moderado"}
      },
      "finalizacoes": {
        "feitas": {"media": 8.50, "cv": 0.38, "classificacao": "Moderado"},
        "sofridas": {"media": 9.80, "cv": 0.42, "classificacao": "Moderado"}
      },
      "finalizacoes_gol": {
        "feitas": {"media": 3.20, "cv": 0.45, "classificacao": "Moderado"},
        "sofridas": {"media": 3.50, "cv": 0.38, "classificacao": "Moderado"}
      },
      "cartoes": {
        "amarelos": {"media": 1.80, "cv": 0.62, "classificacao": "Instavel"},
        "vermelhos": {"media": 0.20, "cv": 0.90, "classificacao": "Muito Instavel"}
      }
    }
  }
}
```

---

## 7. ENDPOINTS VSTATS UTILIZADOS

> **Referencia:** Secao 4 (Endpoints Funcionais) da `DOCUMENTACAO_VSTATS_COMPLETA.md`

### 7.1 Schedule Day (Partidas por Data)

```http
GET /stats/tournament/v1/schedule/day?tmcl={tmcl}&date={YYYY-MM-DD}
```

**Uso:** Listar partidas de uma data especifica.

### 7.2 Season Stats (Medias da Temporada)

```http
GET /stats/seasonstats/v1/team?ctst={contestantId}&tmcl={tmcl}&detailed=yes
```

**Uso:** Obter medias agregadas da temporada (filtro "Geral").

### 7.3 Match Preview (IDs de Partidas Anteriores)

```http
GET /stats/matchpreview/v1/get-match-preview?Fx={matchId}
```

**Uso:** Obter IDs de partidas anteriores via `previousMeetingsAnyComp.ids`.

### 7.4 Get Match Stats (Stats por Partida)

```http
GET /stats/matchstats/v1/get-match-stats?Fx={matchId}
```

**Uso:** Obter estatisticas detalhadas de uma partida (filtros 5/10).

**Localizacao dos dados:** `liveData.lineUp[].stat[]`

### 7.5 TheSportsDB (Escudos)

```http
GET https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={nome_time}
```

**Uso:** Obter URL do escudo via `teams[0].strBadge`.

### 7.6 Tournament Calendar (Lista de Competicoes)

```http
GET /stats/tournament/v1/calendar?Comp={competitionId}
```

**Uso:** Listar todas as competicoes disponiveis.

**Competition ID Principal:** `2kwbbcootiqqgmrzs6o5inle5` (Premier League)

### 7.7 Schedule (Temporada Completa) - DESCOBERTA 25/12/2025

```http
GET /stats/tournament/v1/schedule?tmcl={tournamentCalendarId}
```

**Uso:** Obter TODAS as partidas da temporada (passadas e futuras).

**Retorno:** ~380 partidas por competicao (temporada completa Ago-Mai)

**Campos importantes na resposta:**
```json
{
  "matches": [
    {
      "id": "abc123xyz",
      "localDate": "2025-12-20",
      "localTime": "16:00:00",
      "homeContestantId": "team1id",
      "awayContestantId": "team2id",
      "homeScore": 2,       // null se nao realizada
      "awayScore": 1,       // null se nao realizada
      "matchStatus": "Played"  // ou "Fixture"
    }
  ]
}
```

**Diferenca dos outros endpoints schedule:**

| Endpoint | Retorno | Uso Recomendado |
|----------|---------|-----------------|
| `/schedule` | Temporada completa (~380) | Filtros 5/10, historico |
| `/schedule/month` | Mes atual (~16) | Listagem de partidas do dia |
| `/schedule/week` | Semana atual (~10) | Listagem rapida |

**IMPORTANTE:** Este endpoint resolve o problema de buscar partidas historicas para calcular CV nos filtros 5/10!

---

## 8. IDS DE COMPETICOES

> **Referencia:** Secao 3 da `DOCUMENTACAO_VSTATS_COMPLETA.md`

### 8.1 Abordagem Dinamica (Recomendada)

**IMPORTANTE:** Os IDs de competicoes (tournamentCalendarId) mudam a cada temporada. Em vez de hardcodar IDs, use o endpoint `/calendar` para obter dinamicamente todas as competicoes disponiveis.

```http
GET /stats/tournament/v1/calendar
```

**Resposta:**
```json
[
  {
    "tournamentCalendarId": "51r6ph2woavlbbpk8f29nynf8",
    "knownName": "Premier League",
    "translatedName": "Premier League 2025/2026",
    "country": "England",
    "startDate": "2025-08-16",
    "endDate": "2026-05-24"
  },
  {
    "tournamentCalendarId": "80zg2v1cuqcfhphn56u4qpyqc",
    "knownName": "La Liga",
    "translatedName": "La Liga 2025/2026",
    "country": "Spain"
  }
]
```

**Implementacao no Backend:**
```python
async def fetch_calendar() -> List[Dict]:
    """Busca TODAS as competicoes disponiveis dinamicamente."""
    response = await client.get("/stats/tournament/v1/calendar")
    data = response.json()

    competitions = []
    raw_list = data if isinstance(data, list) else data.get("tournaments", [])

    for comp in raw_list:
        competitions.append({
            "id": comp.get("tournamentCalendarId"),
            "name": comp.get("knownName") or comp.get("translatedName"),
            "country": comp.get("country"),
        })

    return competitions
```

### 8.2 Campos de Identificacao

| Campo | Descricao | Exemplo |
|-------|-----------|---------|
| `tournamentCalendarId` | ID unico da competicao (muda por temporada) | `51r6ph2woavlbbpk8f29nynf8` |
| `knownName` | Nome curto/comum | `Premier League` |
| `translatedName` | Nome com temporada | `Premier League 2025/2026` |
| `country` | Pais/regiao | `England` |

### 8.3 Total de Competicoes

A API VStats retorna **32+ competicoes globais**, incluindo:

- Ligas europeias principais (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
- Copas nacionais
- Competicoes europeias (Champions League, Europa League, Conference League)
- Ligas sul-americanas

---

## 9. CACHE E OTIMIZACAO

### 9.1 O Que Cachear

| Dado | TTL Sugerido | Justificativa |
|------|--------------|---------------|
| Escudos (TheSportsDB) | 7 dias | Raramente mudam |
| IDs de competicoes | 30 dias | Mudam por temporada |
| seasonstats (temporada) | 1 hora | Atualiza apos cada rodada |
| Stats de partidas passadas | Permanente | Dados historicos nao mudam |
| Lista de partidas do dia | 15 minutos | Pode haver alteracoes |

### 9.2 Estrategia de Cache

```python
# Estrutura de cache sugerida
cache = {
    "escudos": {
        "Arsenal": {
            "url": "https://...",
            "expires_at": "2025-12-31T00:00:00"
        }
    },
    "competicoes": [
        {"id": "51r6...", "name": "Premier League 2025/2026"}
    ],
    "seasonstats": {
        "4dsgumo7d4zupm2ugsvm4zm4d": {
            "data": {...},
            "expires_at": "2025-12-24T18:00:00"
        }
    },
    "match_stats": {
        "f4vscquffy37afgv0arwcbztg": {...}  # Permanente
    }
}
```

### 9.3 Recomendacoes

1. **Escudos:** Usar Redis ou cache em memoria com TTL de 7 dias
2. **Stats de partidas passadas:** Armazenar em banco de dados (imutaveis)
3. **Seasonstats:** Cache curto (1h) pois atualiza frequentemente
4. **Requisicoes paralelas:** Buscar stats de multiplas partidas em paralelo

---

## 10. ARQUIVOS A CRIAR

### 10.1 Estrutura de Pastas

```
projeto/
├── backend/
│   ├── main.py                 # FastAPI app principal
│   ├── config.py               # Configuracoes
│   ├── api/
│   │   ├── __init__.py
│   │   ├── vstats.py           # Cliente VStats API
│   │   └── thesportsdb.py      # Cliente TheSportsDB
│   ├── services/
│   │   ├── __init__.py
│   │   ├── stats.py            # Calculos de medias e CV
│   │   └── cache.py            # Gerenciamento de cache
│   ├── models/
│   │   ├── __init__.py
│   │   ├── partida.py          # Modelo Partida
│   │   └── estatisticas.py     # Modelo Estatisticas
│   └── routers/
│       ├── __init__.py
│       ├── partidas.py         # Endpoints de partidas
│       └── stats.py            # Endpoints de estatisticas
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx        # Tela inicial
│   │   │   ├── Partidas.tsx    # Lista de partidas
│   │   │   └── Estatisticas.tsx# Painel comparativo
│   │   ├── components/
│   │   │   ├── CardPartida.tsx # Card de partida
│   │   │   ├── StatsPanel.tsx  # Painel de stats
│   │   │   ├── FiltroStats.tsx # Botoes de filtro
│   │   │   └── TeamBadge.tsx   # Componente de escudo
│   │   ├── services/
│   │   │   └── api.ts          # Cliente da API
│   │   └── types/
│   │       └── index.ts        # Tipos TypeScript
│   └── package.json
│
└── README.md
```

### 10.2 Lista de Arquivos (Backend)

| Arquivo | Descricao |
|---------|-----------|
| `main.py` | Aplicacao FastAPI, rotas principais |
| `config.py` | Variaveis de ambiente, URLs base |
| `api/vstats.py` | Cliente para VStats API |
| `api/thesportsdb.py` | Cliente para TheSportsDB |
| `services/stats.py` | Funcoes de calculo (media, CV) |
| `services/cache.py` | Logica de cache |
| `models/partida.py` | Modelo Pydantic de Partida |
| `models/estatisticas.py` | Modelo Pydantic de Stats |
| `routers/partidas.py` | GET /api/partidas |
| `routers/stats.py` | GET /api/partida/{id}/stats |

### 10.3 Lista de Arquivos (Frontend)

| Arquivo | Descricao |
|---------|-----------|
| `pages/Home.tsx` | Seletor de data + botao |
| `pages/Partidas.tsx` | Grid de cards |
| `pages/Estatisticas.tsx` | Painel comparativo |
| `components/CardPartida.tsx` | Card visual |
| `components/StatsPanel.tsx` | Tabela de stats |
| `components/FiltroStats.tsx` | Geral/5/10 |
| `components/TeamBadge.tsx` | Escudo + nome |
| `services/api.ts` | Axios client |
| `types/index.ts` | Interfaces TS |

---

## 11. RESUMO DAS ESTATISTICAS

### 11.1 Tabela Completa de Campos

| Estatistica | Feitos (Campo) | Sofridos (Campo) | Fonte | Filtro Geral | Filtro 5/10 |
|-------------|----------------|------------------|-------|--------------|-------------|
| Escanteios | `wonCorners` | `lostCorners` | get-match-stats | Parcial* | SIM |
| Gols | `goals` | `goalsConceded` | ambos | SIM | SIM |
| Finalizacoes | `Total Shots` | `Total Shots Conceded` | seasonstats | SIM | SIM |
| Finalizacoes Gol | `Shots On Target` | `Shots On Conceded In/Out Box` | seasonstats | SIM | SIM |
| Cartoes Amarelos | `totalYellowCard` | - | ambos | SIM | SIM |
| Cartoes Vermelhos | `totalRedCard` | - | ambos | SIM | SIM |

> *Parcial: Apenas "feitos" disponivel no seasonstats. "Sofridos" requer get-match-stats.

### 11.2 Campos do seasonstats (Filtro Geral)

| Campo API | Estatistica |
|-----------|-------------|
| `Corners Won` | Escanteios feitos |
| `Goals` | Gols feitos |
| `Goals Conceded` | Gols sofridos |
| `Total Shots` | Finalizacoes |
| `Shots On Target` | Finalizacoes ao gol |
| `Yellow Cards` | Cartoes amarelos |
| `Red Cards` | Cartoes vermelhos |

### 11.3 Campos do get-match-stats (Filtros 5/10)

| Campo API | Estatistica |
|-----------|-------------|
| `wonCorners` | Escanteios feitos |
| `lostCorners` | Escanteios sofridos |
| `goals` | Gols feitos |
| `goalsConceded` | Gols sofridos |
| `totalScoringAtt` | Finalizacoes feitas |
| `ontargetScoringAtt` | Finalizacoes ao gol feitas |
| `totalYellowCard` | Cartoes amarelos |
| `totalRedCard` | Cartoes vermelhos |

---

## 12. SCRIPTS DE VALIDACAO (Testados 24/12/2025)

> **Status:** Todos os testes passaram com sucesso!

### 12.1 scripts/validacao/validar_seasonstats_geral.py

**Objetivo:** Validar todos os campos do Filtro "Geral" (seasonstats)

**Resultado:** 10/10 campos CONFIRMADOS (100%)

| Campo API | Estatistica | Status | Valor (Arsenal) |
|-----------|-------------|--------|-----------------|
| `Corners Won` | Escanteios Feitos | OK | 100 (5.88/jogo) |
| `Goals` | Gols Feitos | OK | 31 (1.82/jogo) |
| `Goals Conceded` | Gols Sofridos | OK | 10 (0.59/jogo) |
| `Total Shots` | Finalizacoes | OK | 184 (10.82/jogo) |
| `Total Shots Conceded` | Finalizacoes Sofridas | OK | 124 (7.29/jogo) |
| `Shots On Target ( inc goals )` | Finalizacoes ao Gol | OK | 84 (4.94/jogo) |
| `Shots On Conceded Inside Box` | Finalizacoes ao Gol Sofridas (Dentro) | OK | 29 (1.71/jogo) |
| `Shots On Conceded Outside Box` | Finalizacoes ao Gol Sofridas (Fora) | OK | 8 (0.47/jogo) |
| `Yellow Cards` | Cartoes Amarelos | OK | 22 (1.29/jogo) |
| `Red Cards` | Cartoes Vermelhos | OK | 0 (sem ocorrencias) |
| `Corners Conceded` | Escanteios Sofridos | NAO EXISTE | Usar get-match-stats |

**Uso:**
```bash
python scripts/validacao/validar_seasonstats_geral.py
```

### 12.2 scripts/validacao/validar_get_match_stats.py

**Objetivo:** Validar todos os campos dos Filtros "5" e "10 Partidas" (get-match-stats)

**Resultado:** Todos os campos obrigatorios presentes

| Campo API | Estatistica | Presenca | Status |
|-----------|-------------|----------|--------|
| `wonCorners` | Escanteios Feitos | 100% | OK |
| `lostCorners` | Escanteios Sofridos | 100% | **CONFIRMADO!** |
| `goals` | Gols Feitos | 100% | OK |
| `goalsConceded` | Gols Sofridos | 75% | OK (condicional) |
| `totalScoringAtt` | Finalizacoes | 100% | OK |
| `ontargetScoringAtt` | Finalizacoes ao Gol | 100% | OK |
| `totalYellowCard` | Cartoes Amarelos | 75% | OK (condicional) |
| `totalRedCard` | Cartoes Vermelhos | 25% | Raro (esperado) |

**Validacoes Adicionais:**
- Calculo via adversario (finalizacoes sofridas) VALIDADO
- CV calculado corretamente para todas as metricas
- Classificacao de estabilidade funcionando

**Uso:**
```bash
python scripts/validacao/validar_get_match_stats.py
```

### 12.3 Resumo da Validacao

| Filtro | Script | Resultado |
|--------|--------|-----------|
| Geral | `scripts/validacao/validar_seasonstats_geral.py` | 10/10 (100%) |
| 5 Partidas | `scripts/validacao/validar_get_match_stats.py` | Todos OK |
| 10 Partidas | `scripts/validacao/validar_get_match_stats.py` | Todos OK |

**Conclusao:** Sistema pronto para implementacao!

---

## 13. PROXIMOS PASSOS

### 13.1 Backend (Python/FastAPI)

1. **Setup inicial**
   - Criar projeto FastAPI
   - Configurar ambiente virtual
   - Instalar dependencias (fastapi, uvicorn, requests, pydantic)

2. **Clientes de API**
   - Implementar cliente VStats (`api/vstats.py`)
   - Implementar cliente TheSportsDB (`api/thesportsdb.py`)

3. **Servicos**
   - Criar servico de calculos (`services/stats.py`)
   - Implementar cache basico (`services/cache.py`)

4. **Modelos**
   - Definir modelos Pydantic

5. **Rotas**
   - GET /api/partidas
   - GET /api/partida/{id}/stats
   - GET /api/competicoes

### 13.2 Frontend (React/TypeScript)

1. **Setup inicial**
   - Criar projeto com Vite ou Create React App
   - Configurar TypeScript
   - Instalar dependencias (axios, react-router, etc.)

2. **Paginas**
   - Implementar Home (datepicker + botao)
   - Implementar Lista de Partidas (cards)
   - Implementar Painel de Estatisticas

3. **Componentes**
   - CardPartida
   - StatsPanel
   - FiltroStats
   - TeamBadge

4. **Integracao**
   - Conectar com API backend
   - Implementar estados e loading

### 13.3 Integracao Final

1. **Testes**
   - Testar fluxo completo
   - Validar calculos de CV
   - Testar com diferentes competicoes

2. **Otimizacao**
   - Implementar cache Redis
   - Otimizar requisicoes paralelas

3. **Deploy**
   - Backend: Heroku, Railway ou similar
   - Frontend: Vercel, Netlify ou similar

---

## 14. FLUXO DA APLICACAO

> Documentacao do fluxo completo de interacao usuario → sistema → APIs

### 14.1 Visao Geral do Fluxo

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FLUXO COMPLETO                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. BUSCAR PARTIDAS DO DIA                                          │
│     └── GET /schedule/month?Tmcl={id}                               │
│         └── Filtrar por data no backend                             │
│                                                                     │
│  2. EXIBIR PARTIDAS                                                 │
│     └── GET thesportsdb.com/searchteams?t={name}                    │
│         └── Obter escudos (cachear!)                                │
│                                                                     │
│  3. CLIQUE NA PARTIDA → Abrir painel de estatisticas                │
│     │                                                               │
│     ├── FILTRO "GERAL" (1 request por time = 2 total)               │
│     │   └── GET /seasonstats/v1/team?ctst={id}&detailed=yes         │
│     │       └── Retorna medias pre-calculadas                       │
│     │                                                               │
│     ├── FILTRO "5 PARTIDAS" (1 + 5 requests por time = 12 total)    │
│     │   ├── GET /schedule → IDs das ultimas 5 (temporada completa)  │
│     │   └── GET /get-match-stats?Fx={id} x 5 partidas               │
│     │       └── Calcular medias e CV                                │
│     │                                                               │
│     └── FILTRO "10 PARTIDAS" (1 + 10 requests por time = 22 total)  │
│         ├── GET /schedule → IDs das ultimas 10 (temporada completa) │
│         └── GET /get-match-stats?Fx={id} x 10 partidas              │
│             └── Calcular medias e CV                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 14.2 Passo 1: Buscar Partidas do Dia

**Acao do Usuario:** Seleciona data e clica no botao de busca

**Endpoint VStats:**
```
GET /stats/tournament/v1/schedule/month?Tmcl={tournamentId}
```

**Observacao Importante:** Este endpoint ignora parametros de data e retorna sempre o mes atual. O filtro por data especifica deve ser feito no backend.

**Logica do Backend:**
```python
def get_matches_by_date(date: str, tournament_id: str):
    response = requests.get(
        f"{BASE_URL}/stats/tournament/v1/schedule/month",
        params={"Tmcl": tournament_id}
    )

    # Estrutura: {"matches": [...]} com campo "localDate" em cada partida
    all_matches_raw = response.json().get('matches', [])

    # Filtra partidas pela data especifica
    all_matches = []
    for match in all_matches_raw:
        if match.get('localDate') == date:  # Formato: YYYY-MM-DD
            all_matches.append({
                'id': match.get('id'),
                'homeTeam': {
                    'id': match.get('homeContestantId'),
                    'name': match.get('homeContestantClubName') or match.get('homeContestantName'),
                    'code': match.get('homeContestantCode'),
                },
                'awayTeam': {
                    'id': match.get('awayContestantId'),
                    'name': match.get('awayContestantClubName') or match.get('awayContestantName'),
                    'code': match.get('awayContestantCode'),
                },
                'time': match.get('localTime'),
                'status': match.get('matchStatus'),
                'homeScore': match.get('homeScore'),
                'awayScore': match.get('awayScore'),
            })
    return all_matches
```

**Resposta para o Frontend:**
```json
[
  {
    "id": "abc123xyz",
    "homeTeam": {"id": "team1", "name": "Arsenal", "code": "ARS"},
    "awayTeam": {"id": "team2", "name": "Chelsea", "code": "CHE"},
    "time": "16:00",
    "status": "Fixture"
  }
]
```

---

### 14.3 Passo 2: Exibir Partidas na Interface

**Acao do Sistema:** Renderizar cards de partidas com escudos

**Endpoint TheSportsDB (escudos):**
```
GET https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}
```

**Logica do Backend:**
```python
def get_team_badge(team_name: str) -> str:
    response = requests.get(
        f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php",
        params={"t": team_name}
    )
    teams = response.json().get('teams', [])
    return teams[0].get('strBadge') if teams else None
```

**Visualizacao do Card:**
```
┌─────────────────────────────────────┐
│  [escudo]  Arsenal  vs  Chelsea [escudo]  │
│            16:00 - Fixture          │
│         Premier League              │
└─────────────────────────────────────┘
```

**Recomendacao:** Cachear escudos por 7+ dias (raramente mudam).

---

### 14.4 Passo 3: Abrir Painel de Estatisticas

**Acao do Usuario:** Clica em um card de partida

**Resultado:** Abre painel com estatisticas dos dois times, com 3 opcoes de filtro.

#### 14.4.1 Filtro "GERAL" (Temporada Completa)

**Requests necessarios:** 2 (1 por time)

**Endpoint:**
```
GET /stats/seasonstats/v1/team?ctst={teamId}&tmcl={tournamentId}&detailed=yes
```

**Logica do Backend:**
```python
def get_season_stats(team_id: str, tournament_id: str):
    response = requests.get(
        f"{BASE_URL}/stats/seasonstats/v1/team",
        params={"ctst": team_id, "tmcl": tournament_id, "detailed": "yes"}
    )

    data = response.json()
    stats = {s.get('name'): {'value': s.get('value'), 'avg': s.get('average')}
             for s in data.get('stat', [])}

    return {
        'corners_feitos': stats.get('Corners Won'),
        'gols_feitos': stats.get('Goals'),
        'gols_sofridos': stats.get('Goals Conceded'),
        'finalizacoes': stats.get('Total Shots'),
        'finalizacoes_sofridas': stats.get('Total Shots Conceded'),
        'finalizacoes_gol': stats.get('Shots On Target ( inc goals )'),
        'cartoes_amarelos': stats.get('Yellow Cards'),
    }
```

**Vantagem:** Medias ja vem pre-calculadas pela API.

**Limitacao:** Escanteios sofridos nao disponiveis (usar filtros 5/10).

---

#### 14.4.2 Filtro "5 PARTIDAS" ou "10 PARTIDAS"

**Requests necessarios:** 12 (filtro 5) ou 22 (filtro 10)

**Sub-passo A: Obter IDs das ultimas N partidas (Atualizado 25/12/2025)**
```python
def get_recent_match_ids(team_id: str, tournament_id: str, limit: int = 10):
    # IMPORTANTE: Usar /schedule (sem sufixo) para obter temporada completa!
    # /schedule/month retorna apenas mes atual e pode nao ter 5/10 partidas
    response = requests.get(
        f"{BASE_URL}/stats/tournament/v1/schedule",
        params={"tmcl": tournament_id}  # minusculo!
    )

    # Estrutura: {"matches": [...]} com ~380 partidas da temporada
    all_matches = response.json().get('matches', [])

    # Filtrar partidas do time que ja foram realizadas
    team_matches = []
    for match in all_matches:
        is_home = match.get('homeContestantId') == team_id
        is_away = match.get('awayContestantId') == team_id
        has_score = match.get('homeScore') is not None

        if (is_home or is_away) and has_score:
            team_matches.append(match)

    # Ordenar por data (mais recentes primeiro)
    team_matches.sort(key=lambda m: m.get('localDate', ''), reverse=True)

    # Retornar IDs das ultimas N partidas
    return [m.get('id') for m in team_matches[:limit]]
```

**Sub-passo B: Extrair stats de cada partida**
```python
def get_match_stats(match_id: str, team_id: str):
    response = requests.get(
        f"{BASE_URL}/stats/matchstats/v1/get-match-stats",
        params={"Fx": match_id}
    )

    data = response.json()
    lineup = data.get('liveData', {}).get('lineUp', [])

    team_stats = None
    opponent_stats = None

    for team in lineup:
        stats = {s.get('type'): int(float(s.get('value', 0)))
                 for s in team.get('stat', [])}

        if team.get('contestantId') == team_id:
            team_stats = stats
        else:
            opponent_stats = stats

    return {
        'corners_feitos': team_stats.get('wonCorners', 0),
        'corners_sofridos': team_stats.get('lostCorners', 0),
        'gols_feitos': team_stats.get('goals', 0),
        'gols_sofridos': team_stats.get('goalsConceded', 0),
        'finalizacoes': team_stats.get('totalScoringAtt', 0),
        'finalizacoes_sofridas': opponent_stats.get('totalScoringAtt', 0),
        'finalizacoes_gol': team_stats.get('ontargetScoringAtt', 0),
        'finalizacoes_gol_sofridas': opponent_stats.get('ontargetScoringAtt', 0),
        'cartoes_amarelos': team_stats.get('totalYellowCard', 0),
    }
```

**Sub-passo C: Agregar e calcular medias/CV**
```python
def calculate_aggregated_stats(match_stats_list: List[dict]):
    import statistics

    aggregated = {}
    fields = ['corners_feitos', 'corners_sofridos', 'gols_feitos',
              'gols_sofridos', 'finalizacoes', 'finalizacoes_sofridas',
              'finalizacoes_gol', 'finalizacoes_gol_sofridas', 'cartoes_amarelos']

    for field in fields:
        values = [m.get(field, 0) for m in match_stats_list]
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        cv = std_dev / mean if mean > 0 else 0

        aggregated[field] = {
            'media': round(mean, 2),
            'desvio': round(std_dev, 2),
            'cv': round(cv, 3),
            'classificacao': classify_cv(cv)
        }

    return aggregated
```

---

### 14.5 Diagrama de Sequencia

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌─────────────┐
│ Usuario  │     │ Frontend │     │ Backend  │     │ APIs Externas│
└────┬─────┘     └────┬─────┘     └────┬─────┘     └──────┬──────┘
     │                │                │                   │
     │ Seleciona Data │                │                   │
     │───────────────>│                │                   │
     │                │                │                   │
     │ Clica Buscar   │                │                   │
     │───────────────>│ GET /partidas  │                   │
     │                │───────────────>│ GET /schedule     │
     │                │                │──────────────────>│ VStats
     │                │                │<──────────────────│
     │                │                │ GET /searchteams  │
     │                │                │──────────────────>│ TheSportsDB
     │                │                │<──────────────────│
     │                │<───────────────│                   │
     │ Lista Partidas │                │                   │
     │<───────────────│                │                   │
     │                │                │                   │
     │ Clica Partida  │                │                   │
     │───────────────>│ GET /stats     │                   │
     │                │───────────────>│                   │
     │                │                │ [Se Filtro Geral] │
     │                │                │ GET /seasonstats  │
     │                │                │──────────────────>│ VStats (x2)
     │                │                │<──────────────────│
     │                │                │                   │
     │                │                │ [Se Filtro 5/10]  │
     │                │                │ GET /schedule     │
     │                │                │──────────────────>│ VStats
     │                │                │ GET /match-stats  │
     │                │                │──────────────────>│ VStats (x5 ou x10)
     │                │                │<──────────────────│
     │                │                │ Calcular CV       │
     │                │<───────────────│                   │
     │ Painel Stats   │                │                   │
     │<───────────────│                │                   │
     │                │                │                   │
```

---

### 14.6 Contagem de Requests por Acao

| Acao | Filtro | Requests VStats | Requests TheSportsDB | Total |
|------|--------|-----------------|---------------------|-------|
| Buscar partidas | - | 1 | 2-20 (escudos)* | 3-21 |
| Abrir estatisticas | Geral | 2 | 0 | 2 |
| Abrir estatisticas | 5 Partidas | 12 | 0 | 12 |
| Abrir estatisticas | 10 Partidas | 22 | 0 | 22 |

*Escudos devem ser cacheados, entao na pratica sera 0 apos primeiro acesso.

---

### 14.7 Otimizacoes Recomendadas

| Problema | Solucao | Impacto |
|----------|---------|---------|
| Muitos requests (22 para filtro 10) | Executar em paralelo (`asyncio`) | -80% tempo |
| Escudos repetidos | Cache Redis/memoria (7 dias) | -95% requests TheSportsDB |
| Schedule repetido | Cache por 1 hora | -90% requests schedule |
| Seasonstats nao muda frequente | Cache por 24 horas | -90% requests seasonstats |
| Match stats historicos | Cache permanente | -100% requests repetidos |

---

### 14.8 Resposta Final do Backend

**Estrutura da resposta para o frontend:**

```json
{
  "match": {
    "id": "abc123xyz",
    "date": "2025-12-24",
    "time": "16:00",
    "status": "Fixture",
    "tournament": "Premier League"
  },
  "homeTeam": {
    "id": "team1",
    "name": "Arsenal",
    "code": "ARS",
    "badge": "https://r2.thesportsdb.com/.../arsenal.png",
    "stats": {
      "corners_feitos": {"media": 5.80, "cv": 0.393, "classificacao": "Moderado"},
      "corners_sofridos": {"media": 3.40, "cv": 0.535, "classificacao": "Instavel"},
      "gols_feitos": {"media": 1.60, "cv": 0.556, "classificacao": "Instavel"},
      "gols_sofridos": {"media": 0.80, "cv": 1.050, "classificacao": "Muito Instavel"},
      "finalizacoes": {"media": 12.40, "cv": 0.283, "classificacao": "Estavel"},
      "finalizacoes_sofridas": {"media": 8.60, "cv": 0.314, "classificacao": "Moderado"},
      "finalizacoes_gol": {"media": 4.80, "cv": 0.342, "classificacao": "Moderado"},
      "finalizacoes_gol_sofridas": {"media": 3.20, "cv": 0.463, "classificacao": "Moderado"},
      "cartoes_amarelos": {"media": 1.60, "cv": 0.556, "classificacao": "Instavel"}
    }
  },
  "awayTeam": {
    "id": "team2",
    "name": "Chelsea",
    "code": "CHE",
    "badge": "https://r2.thesportsdb.com/.../chelsea.png",
    "stats": {
      // Mesma estrutura
    }
  },
  "filter": "5_partidas",
  "matchesAnalyzed": 5
}
```

---

## 15. MODELO DE PREVISAO DE ESTATISTICAS

> Modelo para prever quantidades de estatisticas por jogo (ex: "previsao de 10 escanteios totais")

### 15.1 Conceito do Modelo

O modelo de previsao combina:
- **Ataque do Mandante** (estatisticas feitas em casa)
- **Defesa do Visitante** (estatisticas sofridas fora)
- **Ataque do Visitante** (estatisticas feitas fora)
- **Defesa do Mandante** (estatisticas sofridas em casa)
- **Coeficientes de Variacao (CV)** para ponderar confiabilidade

**Objetivo:** Gerar previsoes realistas com intervalos de confianca honestos.

---

### 15.2 Formula: Media Ponderada Cruzada

**Principio:** Para prever quanto o Time A fara de uma estatistica, combinar:
1. O **ataque** do Time A (quanto ele costuma fazer)
2. A **defesa** do adversario (quanto ele costuma sofrer)

**Pesos Base:**
| Componente | Peso | Justificativa |
|------------|------|---------------|
| Ataque | 55% | Ataque tem ligeiramente mais influencia |
| Defesa Adversaria | 45% | Defesa impacta, mas menos que o ataque |

**Formula Completa:**

```
# Pesos base (importancia relativa)
PesoBase_Ataque = 0.55
PesoBase_Defesa = 0.45

# Fatores de confiabilidade (quanto menor CV, mais confiavel)
FatorCV_Ataque = 1 / (1 + CV_Ataque)
FatorCV_Defesa = 1 / (1 + CV_Defesa)

# Pesos finais (importancia × confiabilidade)
PesoFinal_Ataque = PesoBase_Ataque × FatorCV_Ataque
PesoFinal_Defesa = PesoBase_Defesa × FatorCV_Defesa

# Previsao
Previsao = (MediaAtaque × PesoFinal_Ataque + MediaDefesa × PesoFinal_Defesa) / (PesoFinal_Ataque + PesoFinal_Defesa)

# Intervalo de confianca
CV_Combinado = (CV_Ataque + CV_Defesa) / 2
FatorAjuste = 1.2 se CV_Combinado > 0.6, senao 1.0
Margem = Previsao × CV_Combinado × FatorAjuste

Minimo = max(0, Previsao - Margem)
Maximo = Previsao + Margem
```

---

### 15.3 Exemplo Numerico Completo

**Cenario:** Arsenal (casa) vs Chelsea (fora) - Escanteios

**Dados de Entrada:**
| Time | Metrica | Media | CV |
|------|---------|-------|-----|
| Arsenal (casa) | Escanteios Feitos | 6.2 | 0.35 |
| Chelsea (fora) | Escanteios Sofridos | 5.5 | 0.42 |

**Calculo Passo a Passo:**

```
1. Fatores de confiabilidade:
   FatorCV_Ataque = 1 / (1 + 0.35) = 0.741
   FatorCV_Defesa = 1 / (1 + 0.42) = 0.704

2. Pesos finais:
   PesoFinal_Ataque = 0.55 × 0.741 = 0.407
   PesoFinal_Defesa = 0.45 × 0.704 = 0.317

3. Previsao:
   Previsao = (6.2 × 0.407 + 5.5 × 0.317) / (0.407 + 0.317)
            = (2.52 + 1.74) / 0.724
            = 5.9 escanteios

4. Intervalo:
   CV_Combinado = (0.35 + 0.42) / 2 = 0.385 (< 0.6, fator = 1.0)
   Margem = 5.9 × 0.385 × 1.0 = 2.3

   Minimo = max(0, 5.9 - 2.3) = 3.6 → arredondar para 4
   Maximo = 5.9 + 2.3 = 8.2 → arredondar para 8
```

**Resultado:**
```
Arsenal: 5.9 escanteios (intervalo: 4-8) - Confianca Media
```

---

### 15.4 Classificacao de Confianca

| CV Combinado | Classificacao | Significado |
|--------------|---------------|-------------|
| < 0.20 | Alta | Times muito consistentes, previsao confiavel |
| 0.20 - 0.40 | Media | Previsao razoavel, alguma variacao |
| 0.40 - 0.60 | Baixa | Times inconsistentes, margem de erro grande |
| > 0.60 | Muito Baixa | Resultado imprevisivel, intervalo muito largo |

---

### 15.5 Limitadores de Realismo

Para evitar previsoes absurdas, aplicar limites maximos:

| Estatistica | Max por Time | Max Total | Justificativa |
|-------------|--------------|-----------|---------------|
| Escanteios | 12 | 20 | Raro passar desses valores |
| Gols | 5 | 8 | Goleadas sao excecao |
| Finalizacoes | 25 | 45 | Jogos muito movimentados sao raros |
| Finalizacoes ao Gol | 12 | 20 | Proporcional as finalizacoes |
| Cartoes Amarelos | 5 | 8 | 5+ cartoes = jogo tenso |

**Logica:**
```
Se previsao > limite_maximo:
    previsao = limite_maximo
    confianca = "Baixa"  # Reduziu por bater no limite
```

---

### 15.6 Avaliacao de Qualidade dos Dados

| Media dos CVs | Qualidade | Mensagem ao Usuario |
|---------------|-----------|---------------------|
| < 0.30 | Excelente | Times muito consistentes |
| 0.30 - 0.50 | Boa | Dados confiaveis |
| 0.50 - 0.70 | Razoavel | Alguma variacao nos dados |
| > 0.70 | Baixa | Times inconsistentes, previsoes incertas |

---

### 15.7 Apresentacao na Interface

**Layout Visual:**
```
┌──────────────────────────────────────────────────────────────┐
│  ESCANTEIOS                                                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Arsenal (Casa)          PREVISAO          Chelsea (Fora)    │
│  5.9 (4-8) 🟡                               4.1 (3-6) 🔴     │
│  CV: 0.35                                  CV: 0.50          │
│                                                              │
│                    ┌─────────────────┐                       │
│                    │  TOTAL: 10.0    │                       │
│                    │  (7-14)         │                       │
│                    │  Confianca Media│                       │
│                    └─────────────────┘                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘

Legenda cores:
🟢 Alta confianca (CV < 0.20)
🟡 Media confianca (CV 0.20-0.40)
🟠 Baixa confianca (CV 0.40-0.60)
🔴 Muito baixa confianca (CV > 0.60)
```

---

### 15.8 Estrutura de Resposta com Previsoes

**Adicao ao endpoint `/api/partida/{id}/stats`:**

```json
{
  "match": { ... },
  "homeTeam": {
    "name": "Arsenal",
    "stats": { ... }
  },
  "awayTeam": {
    "name": "Chelsea",
    "stats": { ... }
  },
  "predictions": {
    "corners": {
      "homeTeam": {
        "prediction": 5.9,
        "min": 4,
        "max": 8,
        "confidence": "Media"
      },
      "awayTeam": {
        "prediction": 4.1,
        "min": 3,
        "max": 6,
        "confidence": "Baixa"
      },
      "total": {
        "prediction": 10.0,
        "min": 7,
        "max": 14,
        "confidence": "Media"
      }
    },
    "goals": {
      "homeTeam": {
        "prediction": 1.6,
        "min": 1,
        "max": 3,
        "confidence": "Baixa"
      },
      "awayTeam": {
        "prediction": 1.1,
        "min": 0,
        "max": 2,
        "confidence": "Muito Baixa"
      },
      "total": {
        "prediction": 2.7,
        "min": 1,
        "max": 5,
        "confidence": "Baixa"
      }
    },
    "shots": { ... },
    "shotsOnTarget": { ... },
    "yellowCards": { ... }
  },
  "data_quality": "Boa",
  "filter": "5_partidas",
  "matchesAnalyzed": 5
}
```

---

### 15.9 Casos Especiais

| Situacao | Tratamento |
|----------|------------|
| Time com < 5 partidas | Aumentar margem em 30%, avisar usuario |
| CV > 1.0 | Classificar como "Muito Baixa", aumentar margem em 50% |
| Media de gols < 0.5 | Usar minimo 0.5 (nao prever fracoes muito pequenas) |
| Estatistica zerada | Previsao = 0, intervalo 0-2, confianca "Baixa" |

---

### 15.10 Vantagens do Modelo

| Caracteristica | Beneficio |
|----------------|-----------|
| Cruzamento ataque × defesa | Considera forca dos dois times |
| Vies 55/45 para ataque | Reflete realidade do futebol |
| Ponderacao por CV | Times consistentes tem mais peso |
| Intervalos honestos | Nao finge precisao inexistente |
| Limitadores de realismo | Evita previsoes absurdas |
| Transparente | Facil entender e debugar |

---

### 15.11 Limitacoes Conhecidas

| Limitacao | Impacto | Melhoria Futura |
|-----------|---------|-----------------|
| Nao considera forma recente | Pode ignorar sequencias | Peso temporal |
| Nao considera confrontos diretos | Historico H2H ignorado | Ajuste por historico |
| Nao considera contexto | Lesoes, importancia ignoradas | Fatores externos |
| Assume independencia | Estatisticas correlacionadas | Modelo multivariado |

---

### 15.12 Resumo das Decisoes de Design

**Aprovado e Documentado:**

1. **Formula:** Media Ponderada Cruzada com vies 55/45
2. **Ponderacao:** Por CV (times consistentes pesam mais)
3. **Intervalos:** Baseados em CV combinado + fator de ajuste
4. **Arredondamentos:** 1 decimal (previsao), inteiros (intervalo)
5. **Limitadores:** Maximos por estatistica para realismo
6. **Apresentacao:** Previsao entre estatisticas dos times

**Filosofia "Pe no Chao":**
- Nao exagerar precisao
- Intervalos largos quando incerto
- Avisos claros sobre qualidade dos dados
- Limites realistas baseados em futebol real

---

## Estrutura de Pastas

```
API/
├── PROJETO_SISTEMA_ANALISE.md          # Este documento
├── DOCUMENTACAO_VSTATS_COMPLETA.md     # Documentacao tecnica da API (v5.5)
├── ALINHAMENTO_DOCUMENTACAO.md         # Analise de alinhamento entre documentos
├── CLAUDE.md                           # Guia para Claude Code
├── .env.example                        # Template de variaveis de ambiente
├── docs/                               # Documentacao tecnica adicional
│   ├── ARQUITETURA_BACKEND.md          # Arquitetura do backend
│   ├── MODELOS_DE_DADOS.md             # Modelos de dados
│   ├── TESTING_STRATEGY.md             # Estrategia de testes
│   ├── API_SPECIFICATION.md            # Especificacao da API propria
│   ├── LOCAL_SETUP.md                  # Setup local
│   └── frontend/                       # Documentacao do frontend
│       ├── ARQUITETURA_FRONTEND.md
│       ├── COMPONENTES_REACT.md
│       ├── DESIGN_SYSTEM.md
│       ├── INTEGRACAO_API.md
│       └── RESPONSIVIDADE_E_ACESSIBILIDADE.md
├── scripts/
│   ├── validacao/                      # Scripts de validacao
│   │   ├── validar_seasonstats_geral.py
│   │   ├── validar_get_match_stats.py
│   │   └── validar_descobertas.py
│   └── utilitarios/                    # Scripts de calculo
│       ├── calcular_coeficiente_variacao.py
│       ├── calcular_estatisticas_sofridas.py
│       ├── calcular_corners_sofridos.py
│       ├── compare_detailed.py
│       └── extract_arsenal_fields.py
└── data/
    └── samples/                        # Dados de exemplo (JSON)
        ├── arsenal_detailed_true.json
        ├── arsenal_full_data.json
        ├── arsenal_seasonstats.json
        ├── arsenal_team_rankings.json
        ├── arsenal_vs_crystal_palace.json
        └── premier_league_teams.json
```

---

## Referencias

- **Documentacao Completa da API:** `DOCUMENTACAO_VSTATS_COMPLETA.md`
- **Script de Calculo CV:** `scripts/utilitarios/calcular_coeficiente_variacao.py`
- **Script de Estatisticas Sofridas:** `scripts/utilitarios/calcular_estatisticas_sofridas.py`
- **Script de Validacao Inicial:** `scripts/validacao/validar_descobertas.py`
- **Script de Validacao Seasonstats:** `scripts/validacao/validar_seasonstats_geral.py` (Filtro Geral)
- **Script de Validacao Get-Match-Stats:** `scripts/validacao/validar_get_match_stats.py` (Filtros 5/10)

---

**Versao:** 1.3
**Ultima Atualizacao:** 25 de Dezembro de 2025
**Alinhado com:** DOCUMENTACAO_VSTATS_COMPLETA.md v5.5
**Status de Alinhamento:** ✅ Verificado (ver ALINHAMENTO_DOCUMENTACAO.md)

### Changelog v1.3 (25/12/2025)
- **DESCOBERTA:** Endpoint `/schedule` (sem sufixo) retorna temporada completa (~380 jogos)
- Atualizada seção 1.3 com nova descoberta
- Atualizada seção 4.2 para usar /schedule em vez de /schedule/month
- Adicionada seção 7.7 documentando endpoint /schedule
- Atualizado diagrama de fluxo na seção 14
