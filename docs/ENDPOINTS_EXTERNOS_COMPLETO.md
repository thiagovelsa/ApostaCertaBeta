# Endpoints Externos - Documentação Completa

**Versão:** 2.0
**Última Atualização:** 27 de Dezembro de 2025

Este documento registra **TODOS** os endpoints externos utilizados no projeto, incluindo APIs, scripts de validação, utilitários e processos de desenvolvimento.

---

## Índice

1. [VStats API](#1-vstats-api)
2. [TheSportsDB API](#2-thesportsdb-api)
3. [Opta CDN (Logos)](#3-opta-cdn-logos)
4. [Wikidata SPARQL](#4-wikidata-sparql)
5. [Endpoints Internos (Backend)](#5-endpoints-internos-backend)
6. [Resumo por Arquivo](#6-resumo-por-arquivo)

---

## 1. VStats API

**Base URL:** `https://vstats-back-bbdfdf0bfd16.herokuapp.com/api`

**Configuração:** `backend/app/config.py:25`

### 1.1 Endpoints de Torneio

#### GET /stats/tournament/v1/calendar
**Descrição:** Lista TODAS as competições disponíveis com IDs atualizados.
**Usado em:** `backend/app/repositories/vstats_repository.py:94`
**Parâmetros:** Nenhum
**Retorno:** Lista de torneios com `tournamentCalendarId`, `knownName`, `country`

```python
# Exemplo
data = await self._get("/stats/tournament/v1/calendar")
```

---

#### GET /stats/tournament/v1/schedule/month
**Descrição:** Busca partidas do mês ATUAL de uma competição.
**Usado em:**
- `backend/app/repositories/vstats_repository.py:133`
- `scripts/validacao/validar_get_match_stats.py:91`

**Parâmetros:**
| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `Tmcl` | string | Sim | Tournament Calendar ID (T maiúsculo!) |

**Retorno:**
```json
{
  "matchDate": [
    {
      "date": "2025-12-27",
      "match": [{"id": "...", "homeContestantId": "...", ...}]
    }
  ]
}
```

**Limitação:** Ignora parâmetros `month`/`year` - sempre retorna mês atual.

---

#### GET /stats/tournament/v1/schedule
**Descrição:** Busca calendário COMPLETO da temporada (~380 jogos).
**Usado em:** `backend/app/repositories/vstats_repository.py:164`
**Descoberta:** 25/12/2025

**Parâmetros:**
| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `tmcl` | string | Sim | Tournament Calendar ID (t minúsculo!) |

**Retorno:**
```json
{
  "matches": [
    {
      "id": "...",
      "localDate": "2025-12-27",
      "homeContestantId": "...",
      "awayContestantId": "...",
      "homeScore": 2,
      "awayScore": 1
    }
  ]
}
```

---

### 1.2 Endpoints de Estatísticas

#### GET /stats/seasonstats/v1/team
**Descrição:** Estatísticas agregadas da temporada para um time.
**Usado em:**
- `backend/app/repositories/vstats_repository.py:189`
- `scripts/validacao/validar_seasonstats_geral.py:61`
- `scripts/validacao/validar_descobertas.py:25`
- `scripts/utilitarios/calcular_estatisticas_sofridas.py`
- `scripts/utilitarios/calcular_coeficiente_variacao.py`
- `scripts/utilitarios/calcular_corners_sofridos.py`

**Parâmetros:**
| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `tmcl` | string | Sim | Tournament ID |
| `ctst` | string | Sim | Contestant (Team) ID |
| `detailed` | string | Não | "yes" para estatísticas detalhadas |

**Retorno:**
```json
{
  "stat": [
    {"name": "Goals", "value": "45", "average": 2.5},
    {"name": "Corners Won", "value": "120", "average": 6.7},
    {"name": "Yellow Cards", "value": "28", "average": 1.6}
  ]
}
```

**Campos Disponíveis (Confirmados):**
- `Goals`, `Goals Conceded`
- `Corners Won` (NÃO tem `Corners Conceded`!)
- `Total Shots`, `Total Shots Conceded`
- `Shots On Target ( inc goals )`
- `Shots On Conceded Inside Box`, `Shots On Conceded Outside Box`
- `Yellow Cards`, `Red Cards`
- `Total Fouls Conceded`
- `Saves`, `Clean Sheets`

---

#### GET /stats/matchstats/v1/get-match-stats
**Descrição:** Estatísticas detalhadas de uma partida específica.
**Usado em:**
- `backend/app/repositories/vstats_repository.py:202`
- `scripts/validacao/validar_get_match_stats.py`
- `scripts/validacao/validar_descobertas.py:78`

**Parâmetros:**
| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `Fx` | string | Sim | Match (Fixture) ID |

**Retorno:**
```json
{
  "liveData": {
    "lineUp": [
      {
        "contestantId": "4dsgumo7d4zupm2ugsvm4zm4d",
        "stat": [
          {"type": "wonCorners", "value": 8},
          {"type": "lostCorners", "value": 3},
          {"type": "goals", "value": 2}
        ]
      }
    ]
  }
}
```

**Campos por Partida:**
- `wonCorners`, `lostCorners`
- `goals`, `goalsConceded`
- `totalScoringAtt`, `ontargetScoringAtt`
- `totalYellowCard`, `totalRedCard`
- `fkFoulLost`, `fkFoulWon`
- `saves`, `penaltyConceded`

---

#### GET /stats/matchstats/v1/get-game-played-stats
**Descrição:** Estatísticas agregadas por time de partida JÁ REALIZADA.
**Usado em:** `backend/app/repositories/vstats_repository.py:215`

**Parâmetros:**
| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `Fx` | string | Sim | Match ID |

---

#### GET /stats/matchstats/v1/match-preview
**Descrição:** Preview de partida (head-to-head, forma recente).
**Usado em:** `backend/app/repositories/vstats_repository.py:228`

**Parâmetros:**
| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `Fx` | string | Sim | Match ID |

---

#### GET /stats/referees/v1/get-by-prsn
**Descrição:** Estatísticas de um árbitro específico.
**Usado em:** `backend/app/repositories/vstats_repository.py:241`

**Parâmetros:**
| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `Prsn` | string | Sim | Person (Referee) ID |

**Retorno:** Média de cartões amarelos/vermelhos por partida.

---

### 1.3 IDs de Referência

**Times (Exemplos):**
| Time | contestantId |
|------|--------------|
| Arsenal | `4dsgumo7d4zupm2ugsvm4zm4d` |
| Manchester City | `1c8m2ko0wxq1asfkuykurdr0y` |

**Competições (2025/26):**
| Competição | tournamentCalendarId |
|------------|---------------------|
| Premier League | `51r6ph2woavlbbpk8f29nynf8` |
| La Liga | `80zg2v1cuqcfhphn56u4qpyqc` |
| Serie A | `emdmtfr1v8rey2qru3xzfwges` |
| Bundesliga | `2bchmrj23l9u42d68ntcekob8` |
| Ligue 1 | `dbxs75cag7zyip5re0ppsanmc` |

> **IMPORTANTE:** IDs mudam a cada temporada! Use `/stats/tournament/v1/calendar` para obter IDs atualizados.

---

## 2. TheSportsDB API

**Base URL:** `https://www.thesportsdb.com/api/v1/json`
**API Key:** `3` (grátis, pública)
**Configuração:** `backend/app/config.py:30`

### 2.1 Busca de Times

#### GET /{api_key}/searchteams.php
**Descrição:** Busca time por nome.
**Usado em:** `backend/app/repositories/badge_repository.py:73`

**Parâmetros:**
| Param | Tipo | Descrição |
|-------|------|-----------|
| `t` | string | Nome do time |

**Exemplo:**
```
https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t=Arsenal
```

**Retorno:**
```json
{
  "teams": [
    {
      "idTeam": "133604",
      "strTeam": "Arsenal",
      "strTeamBadge": "https://www.thesportsdb.com/images/media/team/badge/...",
      "strStadium": "Emirates Stadium",
      "strCountry": "England"
    }
  ]
}
```

---

#### GET /{api_key}/search_all_teams.php
**Descrição:** Lista todos os times de uma liga.
**Usado em:** `scripts/download_thesportsdb_logos.py` (desenvolvimento)

**Parâmetros:**
| Param | Tipo | Descrição |
|-------|------|-----------|
| `l` | string | Nome da liga |

**Exemplos:**
```
https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php?l=Scottish Premier League
https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php?l=Austrian Bundesliga
https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php?l=Swiss Super League
```

---

#### GET /{api_key}/search_all_leagues.php
**Descrição:** Lista todas as ligas de um país.
**Usado em:** Desenvolvimento (busca de nomes de ligas)

**Parâmetros:**
| Param | Tipo | Descrição |
|-------|------|-----------|
| `c` | string | Nome do país |

**Exemplo:**
```
https://www.thesportsdb.com/api/v1/json/3/search_all_leagues.php?c=Scotland
```

**Retorno:**
```json
{
  "countries": [
    {"idLeague": "4330", "strLeague": "Scottish Premier League"},
    {"idLeague": "4395", "strLeague": "Scottish Championship"}
  ]
}
```

---

### 2.2 URLs de Badges (CDN)

**Padrão:** `https://www.thesportsdb.com/images/media/team/badge/{hash}.png`
**CDN Alternativo:** `https://r2.thesportsdb.com/images/media/team/badge/{hash}.png`

---

## 3. Opta CDN (Logos)

**Base URL:** `https://omo.akamai.opta.net/image.php`
**Usado em:** `scripts/download_logos.py:9`

### 3.1 Endpoint de Imagens

**URL Completa:**
```
https://omo.akamai.opta.net/image.php?secure=true&h=omo.akamai.opta.net&sport=football&entity=team&description=badges&dimensions=150&id={TEAM_ID}
```

**Parâmetros:**
| Param | Valor Fixo | Descrição |
|-------|------------|-----------|
| `secure` | `true` | HTTPS |
| `h` | `omo.akamai.opta.net` | Host |
| `sport` | `football` | Esporte |
| `entity` | `team` | Tipo de entidade |
| `description` | `badges` | Tipo de imagem |
| `dimensions` | `150` | Tamanho em pixels |
| `id` | variável | ID do time |

### 3.2 Formatos de ID Aceitos

| Formato | Exemplo | Fonte |
|---------|---------|-------|
| Alfanumérico | `4dsgumo7d4zupm2ugsvm4zm4d` | VStats contestantId |
| Numérico | `202` | Wikidata P8737 |

### 3.3 Ligas Cobertas (via VStats)

| País | Liga |
|------|------|
| 🇦🇷 Argentina | Liga Profesional |
| 🇧🇷 Brasil | Série A, Série B |
| 🇬🇧 Inglaterra | Premier League, Championship |
| 🇫🇷 França | Ligue 1, Ligue 2 |
| 🇩🇪 Alemanha | Bundesliga, 2. Bundesliga |
| 🇮🇹 Itália | Serie A, Serie B |
| 🇲🇽 México | Liga MX |
| 🇳🇱 Holanda | Eredivisie, Eerste Divisie |
| 🇵🇹 Portugal | Primeira Liga, Segunda Liga |
| 🇪🇸 Espanha | La Liga, La Liga 2 |
| 🇹🇷 Turquia | Süper Lig |
| 🇺🇸 USA | MLS |

---

## 4. Wikidata SPARQL

**Endpoint:** `https://query.wikidata.org/sparql`
**Usado em:** Desenvolvimento (obtenção de IDs Opta numéricos)

### 4.1 Query para IDs Opta (P8737)

```sparql
SELECT ?team ?teamLabel ?optaId WHERE {
  ?team wdt:P118 wd:Q147459;  # Liga (ex: Super League Greece = Q147459)
        wdt:P8737 ?optaId.    # Opta football team ID
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

### 4.2 IDs de Ligas no Wikidata

| Liga | Wikidata ID | Cobertura P8737 |
|------|-------------|-----------------|
| Super League Greece | Q147459 | ~40% (17/43 times) |
| Austrian Bundesliga | Q306847 | 1 time (Salzburg) |
| Swiss Super League | Q324414 | 0 clubes |
| Scottish Premiership | Q653653 | 0 clubes |

---

## 5. Endpoints Internos (Backend)

**Base URL Local:** `http://localhost:8000`
**Configuração:** `frontend/src/services/api.ts:3`

### 5.1 Rotas da API Própria

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/partidas?data=YYYY-MM-DD` | Lista partidas por data |
| GET | `/api/partida/{matchId}/stats?filtro=geral\|5\|10` | Estatísticas de partida |
| GET | `/api/competicoes` | Lista competições |
| GET | `/api/time/{teamId}/escudo?nome=...` | Busca escudo |

### 5.2 Proxy Vite (Desenvolvimento)

**Configuração:** `frontend/vite.config.ts:16`
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

---

## 6. Resumo por Arquivo

### Backend

| Arquivo | Endpoints Usados |
|---------|------------------|
| `config.py` | Define URLs base: VStats, TheSportsDB |
| `vstats_repository.py` | 7 endpoints VStats |
| `badge_repository.py` | 1 endpoint TheSportsDB |

### Scripts de Validação

| Arquivo | Endpoints |
|---------|-----------|
| `validar_seasonstats_geral.py` | `/stats/seasonstats/v1/team` |
| `validar_get_match_stats.py` | `/stats/matchstats/v1/get-match-stats`, `/stats/tournament/v1/schedule/month` |
| `validar_descobertas.py` | `/stats/seasonstats/v1/team`, `/stats/matchstats/v1/get-match-stats` |

### Scripts Utilitários

| Arquivo | Endpoints |
|---------|-----------|
| `calcular_coeficiente_variacao.py` | VStats API (múltiplos) |
| `calcular_estatisticas_sofridas.py` | `/stats/seasonstats/v1/team` |
| `calcular_corners_sofridos.py` | `/stats/seasonstats/v1/team` |

### Scripts de Logos

| Arquivo | Endpoints |
|---------|-----------|
| `download_logos.py` | Opta CDN (`omo.akamai.opta.net`) |
| `download_thesportsdb_logos.py` | TheSportsDB CDN (`r2.thesportsdb.com`) |

---

## Changelog

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0 | 2025-12-25 | Documentação inicial (logos apenas) |
| 2.0 | 2025-12-27 | Documentação COMPLETA de todos endpoints |
