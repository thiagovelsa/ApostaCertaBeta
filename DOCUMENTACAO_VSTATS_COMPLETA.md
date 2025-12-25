# VStats API - Documentacao Unificada

**Data:** 25 de Dezembro de 2025
**Versao:** 5.6 - Busca dinamica de competicoes via /calendar
**Status:** Documentacao Completa e Validada

---

## Indice

1. [Resumo Executivo](#1-resumo-executivo)
2. [Informacoes da API](#2-informacoes-da-api)
3. [Competicoes Disponiveis](#3-competicoes-disponiveis)
4. [Endpoints Funcionais](#4-endpoints-funcionais)
5. [Endpoints com Erro](#5-endpoints-com-erro)
6. [Estrutura de Dados](#6-estrutura-de-dados)
7. [Limitacoes e Solucoes](#7-limitacoes-e-solucoes)
8. [Exemplos de Uso](#8-exemplos-de-uso)
9. [Caso de Uso: Arsenal vs Crystal Palace](#9-caso-de-uso-arsenal-vs-crystal-palace)
10. [Metodologia de Descoberta](#10-metodologia-de-descoberta)
11. [Guia para Descoberta de Novos Endpoints](#11-guia-para-descoberta-de-novos-endpoints)
12. [IDs de Referencia](#12-ids-de-referencia)
13. [Erros Comuns e Solucoes](#13-erros-comuns-e-solucoes)
14. [Licenca e Uso](#14-licenca-e-uso)

---

## Estrutura de Pastas

```
API/
├── DOCUMENTACAO_VSTATS_COMPLETA.md     # Esta documentacao tecnica (v5.5)
├── PROJETO_SISTEMA_ANALISE.md          # Documento do sistema de analise
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

## 1. Resumo Executivo

A API do VStats.com.br e um servico RESTful hospedado no Heroku que fornece dados estatisticos de futebol de **33+ competicoes globais**.

### Status da Descoberta

| Item | Status |
|------|--------|
| API backend descoberta | OK |
| Credenciais encontradas | OK |
| 32 competicoes catalogadas (via `/calendar`) | OK |
| Estrutura de dados mapeada (15 campos) | OK |
| Dados reais validados | OK |
| **Estatisticas avancadas (escanteios, cartoes, chutes)** | **DISPONIVEL!** |
| **MEDIAS PRE-CALCULADAS (seasonstats/team)** | **v5.2 CRUCIAL!** |
| **Estatisticas Feitas vs Sofridas** | **v5.3 CRUCIAL!** |
| **Elencos completos (squads)** | **v5.2 NOVO!** |
| **Lista de times (teams)** | **v5.2 NOVO!** |
| **Mapa completo de endpoints** | **v5.2 ATUALIZADO** |
| **Lista de arbitros com medias** | **v5.0 NOVO!** |
| **Calendario de competicoes** | **v5.1 NOVO!** |
| **Escudos via TheSportsDB** | **v5.4 NOVO!** |
| **Coeficiente de Variacao (CV)** | **v5.5 NOVO!** |

### O Que Esta Disponivel

- Classificacao de times (tabela completa)
- Estatisticas de gols (marcados/sofridos)
- Forma recente (ultimos 6 jogos)
- Partidas agendadas (schedule dia, semana e mes)
- Dados home/away/primeiro tempo
- Preview de partidas (confrontos diretos, forma)
- Historico de confrontos (H2H)
- **NOVO v4.0:** Estatisticas completas de partidas ja realizadas
- **NOVO v5.2:** MEDIAS AGREGADAS POR EQUIPE NA TEMPORADA!
  - Media de escanteios por jogo (Corners Won)
  - Media de cartoes por jogo (Yellow Cards)
  - Media de finalizacoes (Total Shots, Shots On Target)
  - Media de gols marcados e sofridos
  - Media de faltas, posse de bola, duelos
  - 50+ metricas com valor total e media por jogo
- **NOVO v5.3:** Estatisticas FEITAS vs SOFRIDAS
  - Corners sofridos: disponivel via campo `lostCorners` no get-match-stats (ver secao 7.2)
  - Gols sofridos, chutes sofridos: disponiveis direto na API
  - Penaltis, cartoes vermelhos, defesas: disponiveis por partida
- **NOVO v5.2:** Lista completa de times e elencos
- **NOVO v5.2:** Estatisticas de arbitros com medias
- **NOVO v5.4:** Escudos e logos de equipes via TheSportsDB (ver secao 7.3)
- **NOVO v5.5:** Coeficiente de Variacao (CV) para analise de estabilidade (ver secao 7.4)
  - Calculo de CV para estatisticas FEITAS e SOFRIDAS
  - Escala de interpretacao (Muito Estavel a Muito Instavel)
  - Identificar times consistentes vs imprevisiveis

### O Que NAO Esta Disponivel

- Estatisticas individuais de jogadores agregadas por temporada (apenas por partida)
- Acesso ao scanner de oportunidades (requer login premium)
- Algumas estatisticas "sofridas" agregadas na temporada (disponivel apenas por partida - ver 7.2)
- Escudos/logos de equipes (NAO fornecido pela VStats - usar TheSportsDB, ver 7.3)

---

## 2. Informacoes da API

### Endpoint Base

```
https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/
```

### Credenciais e Autenticacao

**Credenciais encontradas no codigo-fonte (chunk-K2DR4PV4.js):**
```
client_id: partners-74a1df8722c701b44fbc684b391b1a83
client_secret: hHEig5mhezdGbefyo6MzE#VTbUuuMphiqHfEoVQi9uPlePuQptQb!H0K!xg%eq5T
```

**Endpoints de Autenticacao Descobertos:**
```
POST /auth/v1/login          - Login com email/password
POST /auth/v1/refresh-token  - Renovar token
POST /auth/v1/send-reset-email/{email} - Recuperar senha
```

**Sistema de Tokens:**
- A API usa Bearer tokens para autenticacao
- Tokens sao armazenados no navegador com tempo de expiracao
- O frontend obtem token via login e o renova automaticamente

**IMPORTANTE:** Os endpoints de estatisticas (`/stats/*`) funcionam SEM autenticacao!
- Nao e necessario token para acessar dados de partidas, classificacao, etc.
- A autenticacao parece ser usada apenas para funcionalidades de usuario (scanner, favoritos, etc.)

**Modelo Freemium Identificado:**
```javascript
// Descoberto no codigo-fonte:
matchesForFree = []  // Lista de partidas gratuitas
oddtoken = "..."     // Token separado para funcionalidades de odds/apostas
```

| Recurso | Acesso |
|---------|--------|
| Endpoints `/stats/*` | **PUBLICO** - sem token |
| Calendario, standings, partidas | **PUBLICO** |
| Scanner de oportunidades | Premium (requer login) |
| Funcionalidades de odds | Premium (oddtoken) |

**Validacao Testada:**
- Sem header `Authorization` → Funciona normalmente
- Sem header `Origin` ou `Referer` → Funciona normalmente
- Acesso direto via curl/codigo → Funciona normalmente
- Nao ha rate limiting detectado

### Informacoes Tecnicas

| Propriedade | Valor |
|-------------|-------|
| Protocolo | HTTPS |
| Formato | JSON |
| Hosting | Heroku |
| CORS | Habilitado |
| Rate Limiting | Nao detectado |
| Versionamento | V1 (`/v1/`) |

### Provedor de Dados: Opta (Stats Perform)

**DESCOBERTA IMPORTANTE:** Os dados da API VStats sao fornecidos pela **Opta**, agora parte da **Stats Perform**, uma das maiores provedoras de dados esportivos do mundo.

**Evidencias encontradas:**
- Campo `optaEventId` presente em eventos (gols, cartoes, substituicoes)
- Campo `coverageLevel` (sistema de classificacao Opta)
- Estrutura de IDs alfanumericos de 26 caracteres (padrao Opta)
- Formato de dados e nomenclatura consistente com API Opta

**Sobre a Opta/Stats Perform:**

| Info | Detalhe |
|------|---------|
| Empresa | Stats Perform (anteriormente Opta Sports) |
| Sede | Reino Unido / EUA |
| Fundacao | 1996 |
| Clientes | Premier League, La Liga, UEFA, ESPN, Sky Sports, Bet365 |
| Cobertura | 400+ competicoes, dados em tempo real |
| Reputacao | Considerada o "padrao ouro" em dados de futebol |

**Implicacoes para Descoberta de Endpoints:**

Como a Opta fornece APIs padronizadas para seus clientes, os endpoints do VStats provavelmente seguem a estrutura da Opta API. Isso significa que:

1. Endpoints podem seguir padroes documentados da Opta
2. Estrutura de parametros (Fx, Tmcl, Ctst) sao padroes Opta
3. Novos endpoints podem ser descobertos baseados na documentacao publica da Opta

**Padroes de Parametros Opta:**

| Parametro | Significado | Exemplo |
|-----------|-------------|---------|
| Fx | Fixture ID (Match ID) | `2yuulrtp37mbqe9rok936lslw` |
| Tmcl | Tournament Calendar ID | `51r6ph2woavlbbpk8f29nynf8` |
| Ctst | Contestant ID (Team ID) | `4dsgumo7d4zupm2ugsvm4zm4d` |
| Prsn | Person ID (Player/Referee) | `3st0eqq19bhwgt404iy9xrqol` |

**Referencia:** Para explorar mais endpoints, consultar documentacao publica da Opta/Stats Perform API.

---

## 3. Competicoes Disponiveis

> **IMPORTANTE (v5.5):** Os IDs de competicoes (`tournamentCalendarId`) mudam a cada temporada!
> Para producao, use o endpoint `/stats/tournament/v1/calendar` para obter dinamicamente todos os IDs atuais.
> Veja secao 4.17 para implementacao completa.

### Brasil

| Competicao | Tournament Calendar ID | Periodo |
|------------|------------------------|---------|
| Brasileirao Serie A | `752zalnunu0zkdfbbm915kys4` | 2026-01-28 a 2026-12-02 |
| Brasileirao Serie B | `7sqy8euxzlb9qj7f6gt47cmxg` | 2025-04-05 a 2025-11-23 |
| Copa do Brasil | `7owam6thtzfmxox48uwh6j47o` | 2025-02-18 a 2025-12-21 |

### Europa - Top 5 Ligas

| Competicao | Tournament Calendar ID | Periodo |
|------------|------------------------|---------|
| Premier League | `51r6ph2woavlbbpk8f29nynf8` | 2025-08-15 a 2026-05-24 |
| La Liga | `80zg2v1cuqcfhphn56u4qpyqc` | 2025-08-15 a 2026-05-24 |
| Serie A (Italia) | `emdmtfr1v8rey2qru3xzfwges` | 2025-08-23 a 2026-05-24 |
| Bundesliga | `2bchmrj23l9u42d68ntcekob8` | 2025-08-22 a 2026-05-16 |
| Ligue 1 | `dbxs75cag7zyip5re0ppsanmc` | 2025-08-15 a 2026-05-16 |

### Competicoes Internacionais

| Competicao | Tournament Calendar ID |
|------------|------------------------|
| UEFA Champions League | `2mr0u0l78k2gdsm79q56tb2fo` |
| UEFA Europa League | `7ttpe5jzya3vjhjadiemjy7mc` |
| CONMEBOL Libertadores | `dk8bg66qizwked9etonwaaln8` |
| CONMEBOL Sudamericana | `cup6pcsd1c7669pbvoptcmlg4` |

**Total:** 33+ competicoes catalogadas

---

## 4. Endpoints Funcionais

### 4.1 Standings (Classificacao)

**Endpoint:**
```
GET /stats/standings/v1/standings?tmcl={tournamentCalendarId}&detailed=false
```

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| tmcl | string | SIM | Tournament Calendar ID |
| detailed | boolean | SIM | Flag para dados detalhados (sem efeito real) |

**Exemplo:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/standings/v1/standings?tmcl=51r6ph2woavlbbpk8f29nynf8&detailed=false"
```

**Categorias Retornadas:**

| Categoria | Descricao |
|-----------|-----------|
| `total` | Classificacao geral |
| `home` | Jogos em casa |
| `away` | Jogos fora |
| `firstHalfTotal` | Estatisticas do 1 tempo (geral) |
| `firstHalfHome` | 1 tempo em casa |
| `fistHalfAway` | 1 tempo fora (ATENCAO: typo na API) |

---

### 4.2 Schedule (Partidas do Dia)

**Endpoint:**
```
GET /stats/tournament/v1/schedule/day?tmcl={tournamentCalendarId}&detailed=false
```

**Descricao:** Retorna partidas agendadas para uma competicao

**Resposta:**
```json
{
  "matches": [
    {
      "id": "f4vscquffy37afgv0arwcbztg",
      "date": "2025-12-23T00:00:00+00:00",
      "localTime": "17:00:00",
      "localDate": "2025-12-23",
      "homeContestantId": "4dsgumo7d4zupm2ugsvm4zm4d",
      "awayContestantId": "1c8m2ko0wxq1asfkuykurdr0y",
      "homeContestantName": "Arsenal",
      "awayContestantName": "Crystal Palace",
      "awayContestantOfficialName": "Crystal Palace FC",
      "homeContestantOfficialName": "Arsenal FC",
      "awayContestantShortName": "Crystal Palace",
      "homeContestantShortName": "Arsenal",
      "awayContestantCode": "CRY",
      "homeContestantCode": "ARS",
      "numberOfPeriods": "2",
      "periodLength": "45"
    }
  ]
}
```

**Campos Retornados (16 campos):**

| Campo | Descricao |
|-------|-----------|
| id | Match ID unico |
| date | Data/hora UTC |
| localTime | Horario local |
| localDate | Data local |
| homeContestantId | ID do time mandante |
| awayContestantId | ID do time visitante |
| homeContestantName | Nome do mandante |
| awayContestantName | Nome do visitante |
| homeContestantOfficialName | Nome oficial mandante |
| awayContestantOfficialName | Nome oficial visitante |
| homeContestantShortName | Nome curto mandante |
| awayContestantShortName | Nome curto visitante |
| homeContestantCode | Codigo mandante (3 letras) |
| awayContestantCode | Codigo visitante (3 letras) |
| numberOfPeriods | Quantidade de tempos |
| periodLength | Duracao de cada tempo (min) |

---

### 4.3 Schedule Month (Partidas do Mes)

**Endpoint:**
```
GET /stats/tournament/v1/schedule/month?Tmcl={tournamentCalendarId}
```

**Descricao:** Retorna todas as partidas do mes **ATUAL** para uma competicao

> **ATENCAO (Verificado em 24/12/2025):** Os parametros `month` e `year` sao **IGNORADOS** pela API!
> O endpoint sempre retorna o mes atual, independente de quaisquer parametros adicionais.
> Para buscar datas especificas, use `schedule/month` e filtre client-side.

**Exemplo:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/tournament/v1/schedule/month?Tmcl=51r6ph2woavlbbpk8f29nynf8"
```

**Resposta:** Array de partidas do mes atual com todos os campos de schedule/day

**Alternativa - Schedule Week:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/tournament/v1/schedule/week?tmcl=51r6ph2woavlbbpk8f29nynf8"
```
Retorna partidas da semana atual (util para Boxing Day e rodadas proximas).

---

### 4.4 Match Preview (NOVO - DESCOBERTO!)

**Endpoint:**
```
GET /stats/matchpreview/v1/get-match-preview?Fx={matchId}
```

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| Fx | string | SIM | Match ID (Fixture ID) |

**IMPORTANTE - FUNCIONA PARA PARTIDAS FUTURAS!**

Este endpoint retorna dados para partidas que AINDA NAO ACONTECERAM, ideal para analise preditiva:

| Campo | Descricao |
|-------|-----------|
| matchInfo | Info da partida (times, estadio, data, horario) |
| previousMeetings | H2H na mesma competicao (vitorias, empates, gols totais) |
| previousMeetingsAnyComp | H2H em TODAS competicoes |
| previousMeetings.ids | IDs de partidas passadas (usar para buscar stats detalhadas) |
| form | Forma atual dos times na competicao (ultimos 6: W/L/D) |
| formAnyComp | Forma em todas competicoes |

**Exemplo - Partida Futura (Boxing Day 2025):**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/matchpreview/v1/get-match-preview?Fx=2yuulrtp37mbqe9rok936lslw"
```

Retorna Man United vs Newcastle (26/12/2025):
- H2H: 76 vitorias Man Utd, 40 Newcastle, 40 empates
- Forma Man Utd: LDWDWL (irregular)
- Forma Newcastle: DLWDWW (em alta)
- 160+ IDs de confrontos anteriores para analise

**Exemplo:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/matchpreview/v1/get-match-preview?Fx=f4vscquffy37afgv0arwcbztg"
```

**Resposta:**
```json
{
  "matchInfo": {
    "id": "f4vscquffy37afgv0arwcbztg",
    "localDate": "12/23/2025 00:00:00",
    "localTime": "17:00:00",
    "competitionFormat": "Domestic cup",
    "competitionName": "League Cup",
    "tournamentCalendarId": "6lhltebj0dx79xptn0hyph5as",
    "tournamentCalendarName": "2025/2026",
    "stageName": "Quarter-finals",
    "contestant": [
      {
        "id": "4dsgumo7d4zupm2ugsvm4zm4d",
        "name": "Arsenal",
        "shortName": "Arsenal",
        "officialName": "Arsenal FC",
        "code": "ARS",
        "position": "home",
        "country": "England"
      },
      {
        "id": "1c8m2ko0wxq1asfkuykurdr0y",
        "name": "Crystal Palace",
        "shortName": "Crystal Palace",
        "officialName": "Crystal Palace FC",
        "code": "CRY",
        "position": "away",
        "country": "England"
      }
    ],
    "venueName": "Emirates Stadium"
  },
  "previousMeetings": {
    "homeContestantWins": 1,
    "awayContestantWins": 0,
    "draws": 0,
    "homeContestantGoals": 3,
    "awayContestantGoals": 2,
    "ids": "5c74zzpjweutsteisoxvph1ck"
  },
  "previousMeetingsAnyComp": {
    "homeContestantWins": 32,
    "awayContestantWins": 5,
    "draws": 15,
    "homeContestantGoals": 112,
    "awayContestantGoals": 52,
    "ids": "1wlvabjugecgxexpyqugbo7bo,do5ertwz5kefkxoyelso7xpg4,..."
  },
  "form": [
    {"contestantId": "4dsgumo7d4zupm2ugsvm4zm4d", "lastSix": "WWLLWW"},
    {"contestantId": "1c8m2ko0wxq1asfkuykurdr0y", "lastSix": "WWLWWW"}
  ],
  "formAnyComp": [
    {"contestantId": "4dsgumo7d4zupm2ugsvm4zm4d", "lastSix": "WWWLWD"},
    {"contestantId": "1c8m2ko0wxq1asfkuykurdr0y", "lastSix": "LDLWWW"}
  ]
}
```

**Campos Retornados:**

| Campo | Descricao |
|-------|-----------|
| matchInfo | Informacoes da partida (times, local, competicao) |
| previousMeetings | Confrontos diretos NA MESMA COMPETICAO |
| previousMeetingsAnyComp | Confrontos diretos EM TODAS COMPETICOES |
| form | Forma dos times NA COMPETICAO (ultimos 6 jogos) |
| formAnyComp | Forma dos times EM TODAS COMPETICOES |

---

### 4.5 Player Rankings (Estrutura Valida, Dados Vazios)

**Endpoint:**
```
GET /stats/rankings/v1/player/get-players-by-rank?tmcl={tournamentCalendarId}&detailed=false&RankTypeName={rankType}
```

**RankTypeName Aceitos:**
- `goals` - Artilheiros
- `assists` - Assistencias
- `cards` - Cartoes
- `corners` - Escanteios
- `shots` - Chutes
- `fouls` - Faltas
- `yellowCards` - Cartoes Amarelos
- `redCards` - Cartoes Vermelhos
- `shotOnTarget` - Chutes no Gol
- `shotOffTarget` - Chutes para Fora

**Status:** Endpoints retornam 200 OK, mas com dados vazios: `{"nameRankType":"goals","ranking":[]}`

**Nota:** A estrutura esta preparada para receber dados, mas o backend nao esta populando.

---

### 4.6 Get Game Played Stats (NOVO v4.0 - DESCOBERTA IMPORTANTE!)

**Endpoint:**
```
GET /stats/matchstats/v1/get-game-played-stats?Fx={matchId}
```

**Descricao:** Retorna estatisticas COMPLETAS de uma partida JA REALIZADA, incluindo:
- Finalizacoes, escanteios, cartoes, faltas, impedimentos, defesas
- Escalacoes com formacao tatica
- Timeline completa de eventos

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| Fx | string | SIM | Match ID de uma partida JA REALIZADA |

**IMPORTANTE:** Este endpoint so funciona para partidas que ja foram disputadas. Partidas futuras retornarao erro 500.

**Exemplo:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/matchstats/v1/get-game-played-stats?Fx=1wlvabjugecgxexpyqugbo7bo"
```

**Resposta Completa:**
```json
{
  "homeScore": 1,
  "awayScore": 0,
  "homeId": "4dsgumo7d4zupm2ugsvm4zm4d",
  "awayId": "1c8m2ko0wxq1asfkuykurdr0y",
  "homeKnownName": "Arsenal",
  "awayKnownName": "Crystal Palace",
  "homeOfficialName": "Arsenal FC",
  "awayOfficialName": "Crystal Palace FC",
  "tournamentName": "Premier League",
  "tournamentCalendarId": "51r6ph2woavlbbpk8f29nynf8",
  "matchDate": "2025-10-26T00:00:00",
  "stats": {
    "attempts": ["10", "7", "3", "3", "7", "4"],
    "attemptsOnGoal": ["3", "1", "2", "0", "1", "1"],
    "passes": ["540", "360", "315", "166", "225", "194"],
    "fouls": ["10", "6", "6", "3", "4", "3"],
    "yellowCards": ["0", "0", "0", "0", "0", "0"],
    "redCards": ["0", "0", "0", "0", "0", "0"],
    "offsides": ["2", "1", "2", "1", "0", "0"],
    "corners": ["4", "3", "0", "2", "4", "1"],
    "saves": ["1", "2", "0", "1", "1", "1"]
  },
  "squads": [
    {
      "contestantId": "4dsgumo7d4zupm2ugsvm4zm4d",
      "formationUsed": "433",
      "players": [
        {
          "playerId": "4iijb6llnz28unsz4rirr3umt",
          "firstName": "David",
          "matchName": "David Raya",
          "shirtNumber": 1,
          "position": "Goalkeeper",
          "positionSide": "Centre",
          "formationPlace": "1"
        }
      ],
      "isOfficial": true
    }
  ],
  "timeline": [
    {"eventType": "corner", "comment": "Escanteio, Crystal Palace. Cedido por Gabriel Magalhaes.", "minute": "8"},
    {"eventType": "goal", "comment": "Gol! Arsenal 1, Crystal Palace 0. Eberechi Eze (Arsenal)...", "minute": "38"},
    {"eventType": "substitution", "comment": "Substituicao Arsenal...", "minute": "45"}
  ]
}
```

**Estrutura do Array de Stats:**

Cada array de estatisticas tem 6 elementos com a seguinte ordem:

| Indice | Descricao |
|--------|-----------|
| 0 | Home - Full Time (Tempo Total) |
| 1 | Away - Full Time (Tempo Total) |
| 2 | Home - 1o Tempo |
| 3 | Away - 1o Tempo |
| 4 | Home - 2o Tempo |
| 5 | Away - 2o Tempo |

**Exemplo de Leitura:**
```python
stats = data['stats']

# Escanteios Full Time
corners_home_ft = int(stats['corners'][0])  # 4
corners_away_ft = int(stats['corners'][1])  # 3

# Escanteios 1o Tempo
corners_home_1t = int(stats['corners'][2])  # 0
corners_away_1t = int(stats['corners'][3])  # 2

# Escanteios 2o Tempo
corners_home_2t = int(stats['corners'][4])  # 4
corners_away_2t = int(stats['corners'][5])  # 1
```

**Estatisticas Disponiveis:**

| Campo | Descricao |
|-------|-----------|
| attempts | Finalizacoes totais |
| attemptsOnGoal | Finalizacoes no gol |
| passes | Passes totais |
| fouls | Faltas cometidas |
| yellowCards | Cartoes amarelos |
| redCards | Cartoes vermelhos |
| offsides | Impedimentos |
| corners | Escanteios |
| saves | Defesas do goleiro |

**Tipos de Eventos na Timeline:**

| eventType | Descricao |
|-----------|-----------|
| corner | Escanteio |
| goal | Gol |
| miss | Finalizacao para fora |
| attempt saved | Finalizacao defendida |
| substitution | Substituicao |

---

### 4.7 Get Match Stats (NOVO v5.0!)

**Endpoint:**
```
GET /stats/matchstats/v1/get-match-stats?Fx={matchId}
```

**Descricao:** Retorna informacoes detalhadas da partida incluindo ARBITRAGEM. Funciona para partidas FUTURAS (apenas metadados/arbitragem).
**Nota:** Stats por time via `liveData.lineUp[].stat[]` so aparecem quando a partida ja foi disputada. Para estatisticas agregadas por time, usar `get-game-played-stats`.

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| Fx | string | SIM | Match ID (Fixture ID) |

**Exemplo - Partida Futura (Boxing Day 2025):**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/matchstats/v1/get-match-stats?Fx=2yuulrtp37mbqe9rok936lslw"
```

**Resposta:**
```json
{
  "matchInfo": {
    "id": "2yuulrtp37mbqe9rok936lslw",
    "coverageLevel": "13",
    "date": "2025-12-26T00:00:00Z",
    "localTime": "20:00:00",
    "description": "Manchester United vs Newcastle United",
    "venue": {
      "id": "4zn9oeubcog5ol4cb9zm635ni",
      "longName": "Old Trafford"
    }
  },
  "liveData": {
    "matchDetails": {
      "matchStatus": "Fixture"
    },
    "matchDetailExtra": {
      "matchOfficials": [
        {"type": "Main", "firstName": "Anthony", "lastName": "Taylor"},
        {"type": "Video Assistant Referee", "firstName": "Stuart", "lastName": "Attwell"},
        {"type": "Assistant referee 1", "firstName": "Gary", "lastName": "Beswick"},
        {"type": "Assistant referee 2", "firstName": "Marc", "lastName": "Perry"},
        {"type": "Fourth official", "firstName": "Samuel", "lastName": "Barrott"},
        {"type": "Assistant VAR Official", "firstName": "Craig", "lastName": "Taylor"}
      ]
    }
  }
}
```

**Tipos de Arbitros Retornados:**

| Tipo | Descricao |
|------|-----------|
| Main | Arbitro principal |
| Video Assistant Referee | VAR |
| Assistant referee 1 | Bandeirinha 1 |
| Assistant referee 2 | Bandeirinha 2 |
| Fourth official | Quarto arbitro |
| Assistant VAR Official | Assistente do VAR |

**Uso para Analise Preditiva:** Conhecer o arbitro permite analisar historico de cartoes, penaltis marcados, etc.

---

**IMPORTANTE: Para partidas JA REALIZADAS, este endpoint retorna MUITO mais dados!**

**Exemplo - Partida Passada (Newcastle 4x1 Man Utd - 13/04/2025):**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/matchstats/v1/get-match-stats?Fx=dhye4d4eup5xqnshzarodz5zo"
```

**Dados Extras Retornados para Partidas Passadas:**

| Secao | Descricao |
|-------|-----------|
| matchDetails.scores | Placar HT e FT |
| matchDetails.period[] | Duracao de cada tempo, acrescimos |
| goal[] | Cada gol: marcador, assistencia, minuto, timestamp |
| card[] | Cada cartao: jogador, tipo (YC/RC), razao, minuto |
| substitute[] | Substituicoes: quem entrou/saiu, razao, minuto |
| lineUp[].player[].stat[] | **STATS INDIVIDUAIS POR JOGADOR** |

**Estrutura de Gols:**
```json
{
  "goal": [
    {
      "contestantId": "7vn2i2kd35zuetw6b38gw9jsz",
      "periodId": 1,
      "timeMin": 24,
      "timeMinSec": "23:18",
      "type": "G",
      "scorerId": "9sxg58hszjq17avxgumftdu22",
      "scorerName": "S. Tonali",
      "assistPlayerId": "7x6mnev1ob4u5ffmdsvusb4rt",
      "assistPlayerName": "A. Isak",
      "homeScore": 1,
      "awayScore": 0
    }
  ]
}
```

**Estrutura de Cartoes:**
```json
{
  "card": [
    {
      "contestantId": "6eqit8ye8aomdsrrq0hk3v7gh",
      "periodId": 1,
      "timeMin": 16,
      "type": "YC",
      "playerId": "8jfjglichcg0py57hhri5v0fd",
      "playerName": "M. Ugarte",
      "cardReason": "Foul"
    }
  ]
}
```

**Estatisticas Individuais por Jogador (lineUp[].player[].stat[]):**

| Tipo | Descricao |
|------|-----------|
| goals | Gols marcados |
| goalAssist | Assistencias |
| totalPass | Passes totais |
| accuratePass | Passes certos |
| totalScoringAtt | Finalizacoes totais |
| ontargetScoringAtt | Finalizacoes no gol |
| shotOnTarget | Chutes no gol |
| shotOffTarget | Chutes para fora |
| blockedScoringAtt | Chutes bloqueados |
| wonCorners | Escanteios ganhos |
| lostCorners | Escanteios perdidos |
| cornerTaken | Escanteios cobrados |
| saves | Defesas (goleiro) |
| goalsConceded | Gols sofridos |
| fouls | Faltas cometidas |
| wasFouled | Faltas sofridas |
| totalTackle | Desarmes tentados |
| wonTackle | Desarmes certos |
| totalClearance | Cortes |
| totalOffside | Impedimentos |
| minsPlayed | Minutos jogados |
| gameStarted | Titular (1) ou reserva (0) |
| totalSubOn | Entrou como substituto |
| totalSubOff | Saiu substituido |

**Exemplo de Stats de Jogador:**
```json
{
  "playerId": "65z99j774kjnbf7vm0u2q0jit",
  "matchName": "K. Trippier",
  "position": "Defender",
  "stat": [
    {"type": "cornerTaken", "value": "7"},
    {"type": "accuratePass", "value": "41"},
    {"type": "totalPass", "value": "49"},
    {"type": "minsPlayed", "value": "78"},
    {"type": "wasFouled", "value": "3"},
    {"type": "totalTackle", "value": "3"}
  ]
}
```

**Comparacao: get-match-stats vs get-game-played-stats**

| Recurso | get-match-stats | get-game-played-stats |
|---------|-----------------|----------------------|
| Stats por TIME | ❌ | ✅ (array 6 elementos) |
| Stats por JOGADOR | ✅ | ❌ |
| Detalhes de gols | ✅ (marcador, assist) | ❌ |
| Detalhes de cartoes | ✅ (jogador, razao) | ❌ |
| Substituicoes | ✅ | ❌ |
| Timeline eventos | ❌ | ✅ |
| Arbitragem | ✅ | ❌ |
| Funciona partida futura | ✅ (parcial) | ❌ |

**Recomendacao:** Use `get-match-stats` para analises detalhadas por jogador e `get-game-played-stats` para stats agregadas por time.

---

### 4.8 Player Career (NOVO v5.0!)

**Endpoint:**
```
GET /stats/playercareer/v1/player-teams-career?Prsn={playerId}
```

**Descricao:** Retorna a carreira COMPLETA de um jogador, incluindo todos os times, selecoes e estatisticas por temporada.

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| Prsn | string | SIM | Player ID (Person ID) |

**Exemplo - Sandro Tonali:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/playercareer/v1/player-teams-career?Prsn=9sxg58hszjq17avxgumftdu22"
```

**Resposta:**
```json
{
  "id": "9sxg58hszjq17avxgumftdu22",
  "firstName": "Sandro",
  "lastName": "Tonali",
  "position": "Midfielder",
  "dateOfBirth": "2000-05-08",
  "countryOfBirth": "Italy",
  "height": "181",
  "weight": "79",
  "foot": "right",
  "currentTeamId": "7vn2i2kd35zuetw6b38gw9jsz",
  "currentTeamName": "Newcastle United FC",
  "teamStats": [
    {
      "contestantId": "7vn2i2kd35zuetw6b38gw9jsz",
      "contestantName": "Newcastle United FC",
      "seasons": "2023 - Atual",
      "goals": 7,
      "games": 83,
      "assists": 7,
      "yellowCards": 10,
      "redCards": 0,
      "minutesPlayed": 5851
    }
  ]
}
```

**Campos Retornados:**

| Campo | Descricao |
|-------|-----------|
| id | Player ID |
| firstName/lastName | Nome do jogador |
| position | Posicao (Midfielder, Striker, etc.) |
| dateOfBirth | Data de nascimento |
| height/weight | Altura (cm) e peso (kg) |
| foot | Pe preferido (right/left) |
| currentTeamId/Name | Time atual |
| teamStats[] | Historico por time/selecao |

**Estatisticas por Time (teamStats):**

| Campo | Descricao |
|-------|-----------|
| contestantId/Name | ID e nome do time |
| seasons | Periodo no time |
| goals | Gols marcados |
| games | Partidas disputadas |
| assists | Assistencias |
| yellowCards | Cartoes amarelos |
| redCards | Cartoes vermelhos |
| minutesPlayed | Minutos jogados |

---

### 4.9 Referee Stats (NOVO v5.0!)

**Endpoint:**
```
GET /stats/referees/v1/get-by-prsn?Prsn={refereeId}
```

**Descricao:** Retorna estatisticas COMPLETAS de um arbitro por competicao. MUITO UTIL para analise preditiva de cartoes!

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| Prsn | string | SIM | Referee ID (Person ID) - obtido via get-match-stats |

**Exemplo - Anthony Taylor:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/referees/v1/get-by-prsn?Prsn=3st0eqq19bhwgt404iy9xrqol"
```

**Resposta:**
```json
{
  "name": "A. Taylor",
  "tournamentStats": [
    {
      "tmcl": "51r6ph2woavlbbpk8f29nynf8",
      "competitionName": "Premier League",
      "matches": "14",
      "yellowCards": "56",
      "redCards": "1",
      "offsides": "50",
      "fouls": "286",
      "penalties": "4",
      "averageCards": "4.0",
      "averageFouls": "20.00",
      "foulsByCard": "5.0"
    }
  ]
}
```

**Estatisticas do Arbitro:**

| Campo | Descricao |
|-------|-----------|
| matches | Partidas apitadas na competicao |
| yellowCards | Total de amarelos dados |
| redCards | Total de vermelhos dados |
| offsides | Impedimentos marcados |
| fouls | Faltas marcadas |
| penalties | Penaltis marcados |
| **averageCards** | **Media de cartoes por jogo** |
| averageFouls | Media de faltas por jogo |
| foulsByCard | Faltas por cartao (frequencia) |

**Uso para Analise Preditiva:**

Conhecendo o arbitro da partida (via `get-match-stats`), voce pode prever:
- Tendencia de cartoes (averageCards alto = mais cartoes)
- Rigidez (foulsByCard baixo = arbitro rigido)
- Penaltis (historico de penaltis marcados)

**Exemplo de Fluxo:**
```python
# 1. Obter arbitro da partida futura
match_stats = get_match_stats(match_id)
referee_id = match_stats['liveData']['matchDetailExtra']['matchOfficials'][0]['id']

# 2. Buscar estatisticas do arbitro
referee_stats = get_referee_stats(referee_id)
avg_cards = referee_stats['tournamentStats'][0]['averageCards']

print(f"Arbitro: {referee_stats['name']}")
print(f"Media de cartoes: {avg_cards} por jogo")
```

#### 4.11.2 Listar Todos os Arbitros de uma Competicao

**Endpoint:**
```
GET /stats/referees/v1/get-all?tmcl={tournamentCalendarId}
```

**Descricao:** Retorna TODOS os arbitros de uma competicao com suas estatisticas completas. Ideal para criar ranking de arbitros ou pre-carregar dados.

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| tmcl | string | SIM | Tournament Calendar ID |

**Exemplo - Todos arbitros da Premier League:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/referees/v1/get-all?tmcl=51r6ph2woavlbbpk8f29nynf8"
```

**Resposta (array de arbitros):**
```json
[
  {
    "id": "3st0eqq19bhwgt404iy9xrqol",
    "name": "A. Taylor",
    "matches": "14",
    "yellowCards": "56",
    "redCards": "1",
    "averageCards": "4.0",
    "averageFouls": "20.00",
    "foulsByCard": "5.0"
  },
  {
    "id": "abc123...",
    "name": "M. Oliver",
    "matches": "12",
    "yellowCards": "48",
    "redCards": "2",
    "averageCards": "4.17",
    "averageFouls": "18.50",
    "foulsByCard": "4.4"
  }
]
```

**Uso Pratico - Ranking de Arbitros por Cartoes:**
```python
# Buscar todos arbitros da Premier League
referees = requests.get(f"{BASE_URL}/stats/referees/v1/get-all?tmcl={PL_ID}").json()

# Ordenar por media de cartoes (mais rigidos primeiro)
ranking = sorted(referees, key=lambda x: float(x['averageCards']), reverse=True)

print("Arbitros mais rigidos da Premier League:")
for i, ref in enumerate(ranking[:5], 1):
    print(f"{i}. {ref['name']} - {ref['averageCards']} cartoes/jogo")
```

---

### 4.10 Get Lineups (NOVO v4.0!)

**Endpoint:**
```
GET /stats/matchstats/v1/get-lineups?Fx={matchId}
```

**Descricao:** Retorna apenas as escalacoes de uma partida ja realizada.

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| Fx | string | SIM | Match ID de uma partida JA REALIZADA |

**Exemplo:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/matchstats/v1/get-lineups?Fx=1wlvabjugecgxexpyqugbo7bo"
```

**Resposta:**
```json
[
  {
    "contestantId": "4dsgumo7d4zupm2ugsvm4zm4d",
    "formationUsed": "433",
    "players": [
      {
        "playerId": "4iijb6llnz28unsz4rirr3umt",
        "firstName": "David",
        "matchName": "David Raya",
        "shirtNumber": 1,
        "position": "Goalkeeper",
        "positionSide": "Centre",
        "formationPlace": "1"
      }
    ],
    "isOfficial": true
  }
]
```

**Campos do Jogador:**

| Campo | Descricao |
|-------|-----------|
| playerId | ID unico do jogador |
| firstName | Primeiro nome |
| knownName | Apelido (se existir) |
| matchName | Nome mostrado na partida |
| shirtNumber | Numero da camisa |
| position | Posicao (Goalkeeper, Defender, Midfielder, Striker) |
| positionSide | Lado do campo (Left, Centre, Right, Left/Centre, etc.) |
| formationPlace | Posicao na formacao (1-11) |

---

### 4.11 Schedule por Data Especifica

> **ATENCAO (Verificado em 24/12/2025):** O parametro `date` frequentemente retorna array vazio!
> **RECOMENDACAO:** Usar `schedule/month` ou `schedule/week` e filtrar client-side.

**Endpoint:**
```
GET /stats/tournament/v1/schedule/day?tmcl={tournamentCalendarId}&date={YYYY-MM-DD}
```

**Descricao:** Deveria retornar partidas para uma data especifica, mas na pratica geralmente retorna vazio.

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| tmcl | string | SIM | Tournament Calendar ID |
| date | string | SIM | Data no formato YYYY-MM-DD |

**PROBLEMA:** Mesmo para datas validas com partidas (ex: Boxing Day 26/12), retorna `{"matches":[]}`.

**Exemplo - Buscar partidas de 27/12/2025 (Premier League):**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/tournament/v1/schedule/day?tmcl=51r6ph2woavlbbpk8f29nynf8&date=2025-12-27"
```

**Resposta:**
```json
{
  "matches": [
    {
      "id": "2wehv0cptselv086q8jud4hec",
      "date": "2025-12-27T00:00:00+00:00",
      "localTime": "12:00:00",
      "localDate": "2025-12-27",
      "homeContestantId": "4dsgumo7d4zupm2ugsvm4zm4d",
      "awayContestantId": "e5p0ehyguld7egzhiedpdnc3w",
      "homeContestantName": "Arsenal",
      "awayContestantName": "Brighton & Hove Albion",
      "homeContestantCode": "ARS",
      "awayContestantCode": "BHA"
    }
  ]
}
```

**Uso Pratico - Buscar partidas do dia seguinte:**
```python
from datetime import datetime, timedelta

# Data de amanha
amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

# Buscar partidas da Premier League para amanha
url = f"https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/tournament/v1/schedule/day?tmcl=51r6ph2woavlbbpk8f29nynf8&date={amanha}"
```

**Nota:** Para buscar partidas de TODAS as competicoes de um dia, e necessario iterar sobre os IDs de todas as competicoes listadas no endpoint `/calendar`.

**FALLBACK OBRIGATORIO:** O parametro `date` quase sempre retorna vazio (verificado 24/12/2025). Use `schedule/month` ou `schedule/week` como fonte principal:

```bash
# Se schedule/day?date= retornar vazio, use:
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/tournament/v1/schedule/month?Tmcl=51r6ph2woavlbbpk8f29nynf8"
```

Depois filtre as partidas pela data desejada no seu codigo:

```python
from datetime import datetime

def get_matches_by_date(tournament_id: str, target_date: str) -> list:
    """
    Busca partidas de uma data especifica.
    Tenta schedule/day primeiro, fallback para schedule/month.
    """
    import requests

    BASE_URL = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"

    # Tentar endpoint direto
    url = f"{BASE_URL}/stats/tournament/v1/schedule/day"
    response = requests.get(url, params={"tmcl": tournament_id, "date": target_date})
    data = response.json()

    if data.get("matches"):
        return data["matches"]

    # Fallback: buscar mes inteiro e filtrar
    url = f"{BASE_URL}/stats/tournament/v1/schedule/month"
    response = requests.get(url, params={"Tmcl": tournament_id})
    data = response.json()

    # Filtrar por data
    return [m for m in data.get("matches", []) if m["localDate"] == target_date]

# Exemplo: partidas da Premier League em 27/12/2025
matches = get_matches_by_date("51r6ph2woavlbbpk8f29nynf8", "2025-12-27")
for m in matches:
    print(f"{m['localTime']} - {m['homeContestantName']} vs {m['awayContestantName']}")
```

---

### 4.12 Season Stats - Estatisticas Agregadas por Equipe (DESCOBERTA CRUCIAL v5.2!)

**Endpoint:**
```
GET /stats/seasonstats/v1/team?ctst={contestantId}&tmcl={tournamentCalendarId}&detailed=yes
```

**Descricao:** Retorna TODAS as estatisticas agregadas de uma equipe na temporada COM MEDIAS PRE-CALCULADAS! Este e o endpoint mais importante para analise preditiva.

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| ctst | string | SIM | Contestant ID (Team ID) |
| tmcl | string | SIM | Tournament Calendar ID |
| detailed | string | SIM | Deve ser "yes" (NAO "true") |

**Exemplo - Stats do Arsenal na Premier League:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/seasonstats/v1/team?ctst=4dsgumo7d4zupm2ugsvm4zm4d&tmcl=51r6ph2woavlbbpk8f29nynf8&detailed=yes"
```

**Resposta (exemplo parcial):**
```json
{
  "id": "4dsgumo7d4zupm2ugsvm4zm4d",
  "name": "Arsenal FC",
  "stat": [
    {"name": "Corners Won", "value": "100", "average": 5.88},
    {"name": "Yellow Cards", "value": "22", "average": 1.29},
    {"name": "Total Shots", "value": "184", "average": 10.82},
    {"name": "Goals", "value": "31", "average": 1.82},
    {"name": "Goals Conceded", "value": "10", "average": 0.59},
    {"name": "Clean Sheets", "value": "9", "average": 0.53},
    {"name": "Total Fouls Conceded", "value": "166", "average": 9.76},
    {"name": "Possession Percentage", "value": "59.5", "average": 3.5}
  ]
}
```

**Estatisticas Disponiveis (50+ metricas):**

| Categoria | Estatisticas |
|-----------|--------------|
| **Gols** | Goals, Goals Conceded, Headed Goals, Penalty Goals, Own Goals, Home Goals, Away Goals |
| **Finalizacoes** | Total Shots, Shots On Target, Shots Off Target, Blocked Shots |
| **Escanteios** | Corners Won, Corners Taken, Successful Corners into Box |
| **Cartoes** | Yellow Cards, Red Cards |
| **Faltas** | Total Fouls Conceded, Total Fouls Won |
| **Passes** | Total Successful Passes, Total Unsuccessful Passes, Crossing Accuracy |
| **Defesa** | Clean Sheets, Blocks, Catches, Saves |
| **Duelos** | Duels, Duels Won, Duels Lost, Aerial Duels |
| **Posse** | Possession Percentage |

**Uso para Analise Preditiva:**
```python
def get_team_averages(team_id, tmcl_id):
    url = f"{BASE_URL}/stats/seasonstats/v1/team"
    params = {"ctst": team_id, "tmcl": tmcl_id, "detailed": "yes"}
    data = requests.get(url, params=params).json()

    stats = {s['name']: s['average'] for s in data['stat']}

    return {
        'corners_avg': stats.get('Corners Won', 0),
        'cards_avg': stats.get('Yellow Cards', 0),
        'shots_avg': stats.get('Total Shots', 0),
        'goals_avg': stats.get('Goals', 0),
        'goals_conceded_avg': stats.get('Goals Conceded', 0),
        'clean_sheets': stats.get('Clean Sheets', 0),
        'fouls_avg': stats.get('Total Fouls Conceded', 0)
    }

# Arsenal: 5.88 corners/jogo, 1.29 cards/jogo, 10.82 shots/jogo
arsenal = get_team_averages("4dsgumo7d4zupm2ugsvm4zm4d", "51r6ph2woavlbbpk8f29nynf8")
```

---

### 4.13 Teams - Lista de Times (NOVO v5.2!)

**Endpoint:**
```
GET /stats/team/v1/teams?tmcl={tournamentCalendarId}&detailed=yes
```

**Descricao:** Retorna lista de todos os times de uma competicao com informacoes basicas.

**Exemplo:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/team/v1/teams?tmcl=51r6ph2woavlbbpk8f29nynf8&detailed=yes"
```

**Resposta:**
```json
[
  {
    "id": "4dsgumo7d4zupm2ugsvm4zm4d",
    "name": "Arsenal",
    "shortName": "Arsenal",
    "officialName": "Arsenal FC",
    "code": "ARS",
    "country": "England",
    "city": "London",
    "founded": "1886"
  }
]
```

---

### 4.14 Squads - Elenco Completo (NOVO v5.2!)

**Endpoint:**
```
GET /stats/squads/v1/get-squads?ctst={contestantId}&tmcl={tournamentCalendarId}&detailed=yes
```

**Descricao:** Retorna o elenco completo de um time com informacoes de cada jogador.

**Exemplo - Elenco do Arsenal:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/squads/v1/get-squads?ctst=4dsgumo7d4zupm2ugsvm4zm4d&tmcl=51r6ph2woavlbbpk8f29nynf8&detailed=yes"
```

**Resposta:**
```json
[
  {
    "id": "2lt2tw1qypl9hmlz529bo0sus",
    "firstName": "Ethan Chidiebere",
    "lastName": "Nwaneri",
    "shortFirstName": "Ethan",
    "shortLastName": "Nwaneri",
    "position": "Midfielder",
    "dateOfBirth": "2007-03-21",
    "countryOfBirth": "England",
    "height": 176,
    "weight": 70,
    "foot": "left",
    "teamShortName": "Arsenal",
    "teamOfficialName": "Arsenal FC"
  }
]
```

---

### 4.15 Schedule Week - Agenda Semanal (NOVO v5.2!)

**Endpoint:**
```
GET /stats/tournament/v1/schedule/week?tmcl={tournamentCalendarId}
```

**Descricao:** Retorna todas as partidas da semana atual para uma competicao.

**Exemplo:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/tournament/v1/schedule/week?tmcl=51r6ph2woavlbbpk8f29nynf8"
```

**Resposta:**
```json
{
  "matches": [
    {
      "id": "2yuulrtp37mbqe9rok936lslw",
      "date": "2025-12-26T00:00:00+00:00",
      "localTime": "17:00:00",
      "localDate": "2025-12-26",
      "homeContestantId": "6eqit8ye8aomdsrrq0hk3v7gh",
      "awayContestantId": "7vn2i2kd35zuetw6b38gw9jsz",
      "homeContestantName": "Manchester United",
      "awayContestantName": "Newcastle United",
      "homeContestantCode": "MUN",
      "awayContestantCode": "NEW"
    }
  ]
}
```

---

### 4.16 Team Form - Forma Recente (NOVO v5.2!)

**Endpoint:**
```
GET /stats/matchpreview/v1/get-team-form?Fx={matchId}&CtstId={contestantId}
```

**Descricao:** Retorna a forma recente de um time (ultimos 6 jogos) no formato WDLWWL.

**Exemplo:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/matchpreview/v1/get-team-form?Fx=2yuulrtp37mbqe9rok936lslw&CtstId=6eqit8ye8aomdsrrq0hk3v7gh"
```

**Resposta:**
```json
{
  "form": "LDWDWL"
}
```

Legenda: W=Win, D=Draw, L=Loss (mais recente primeiro)

---

### 4.17 Tournament Calendar - Lista de Competicoes (NOVO v5.1!)

**Endpoint:**
```
GET /stats/tournament/v1/calendar
```

**Descricao:** Retorna TODAS as competicoes disponiveis na API com seus IDs. Endpoint essencial para descobrir os tournament calendar IDs de cada liga.

**Parametros:** Nenhum obrigatorio.

**Exemplo:**
```bash
curl "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/tournament/v1/calendar"
```

**Resposta (parcial - 32 competicoes disponiveis):**
```json
[
  {
    "competitionId": "581t4mywybx21wcpmpykhyzr3",
    "translatedName": "Campeonato Argentino",
    "name": "Liga Profesional Argentina",
    "competitionCode": "LPA",
    "competitionFormat": "Domestic league",
    "country": "Argentina",
    "tournamentCalendarId": "8v84l9nq3d5t0j4gb781i3llg",
    "startDate": "2026-01-25Z",
    "endDate": "2026-12-14Z",
    "includeStandings": "yes"
  },
  {
    "competitionId": "bgsqmfpjfpt1sqp0s1aav6nrk",
    "knownName": "Premier League",
    "name": "Premier League",
    "competitionCode": "EPL",
    "competitionFormat": "Domestic league",
    "country": "England",
    "tournamentCalendarId": "51r6ph2woavlbbpk8f29nynf8",
    "startDate": "2025-08-16Z",
    "endDate": "2026-05-24Z",
    "includeStandings": "yes"
  }
]
```

**Campos Importantes:**

| Campo | Descricao |
|-------|-----------|
| competitionId | ID unico da competicao |
| name | Nome oficial da competicao |
| knownName | Nome popular (quando existe) |
| competitionCode | Codigo abreviado (EPL, UCL, etc) |
| country | Pais da competicao |
| **tournamentCalendarId** | **ID usado em todos os outros endpoints!** |
| startDate / endDate | Periodo da temporada |
| includeStandings | Se possui tabela de classificacao |

**Lista Completa de Competicoes (v5.1):**

| Pais | Competicao | Tournament Calendar ID |
|------|------------|------------------------|
| Argentina | Liga Profesional | 8v84l9nq3d5t0j4gb781i3llg |
| Brazil | Copa do Brasil | 7owam6thtzfmxox48uwh6j47o |
| Brazil | Serie A | 752zalnunu0zkdfbbm915kys4 |
| Brazil | Serie B | 7sqy8euxzlb9qj7f6gt47cmxg |
| England | Championship | bmmk637l2a33h90zlu36kx8no |
| England | FA Cup | 461lceqlslg7w32yc4w0ogems |
| England | League Cup | 6lhltebj0dx79xptn0hyph5as |
| England | **Premier League** | **51r6ph2woavlbbpk8f29nynf8** |
| Europe | Champions League | 2mr0u0l78k2gdsm79q56tb2fo |
| Europe | Conference League | 7x2zp2hm4p6wuijwdw3h7a8t0 |
| + 22 outras competicoes... | | |

---

### 4.18 Mapa Completo de Endpoints (Atualizado v5.2!)

A partir da analise do codigo-fonte do VStats (`chunk-SQZ4MXU4.js`), todos os endpoints disponiveis foram catalogados:

**Endpoints Funcionais TESTADOS (v5.2):**

| Modulo | Endpoint | Descricao | Parametros | Status |
|--------|----------|-----------|------------|--------|
| tournament | `/v1/calendar` | Lista 32 competicoes | - | **OK** |
| tournament | `/v1/schedule/month` | Agenda mensal | Tmcl | **OK** |
| tournament | `/v1/schedule/week` | Agenda semanal | tmcl | **OK** |
| tournament | `/v1/schedule/day` | Partidas por data | tmcl, date | **OK** |
| standings | `/v1/standings` | Classificacao | tmcl, detailed | **OK** |
| **team** | `/v1/teams` | **Lista times** | tmcl, detailed=yes | **OK v5.2** |
| **squads** | `/v1/get-squads` | **Elenco completo** | ctst, tmcl, detailed=yes | **OK v5.2** |
| **seasonstats** | `/v1/team` | **MEDIAS DA TEMPORADA!** | ctst, tmcl, detailed=yes | **OK v5.2** |
| matchpreview | `/v1/get-match-preview` | Preview + H2H | Fx | **OK** |
| matchpreview | `/v1/get-team-form` | Forma do time | Fx, CtstId | **OK** |
| matchstats | `/v1/get-match-stats` | Stats de partida | Fx | **OK** |
| matchstats | `/v1/get-game-played-stats` | Stats detalhadas | Fx | **OK** |
| matchstats | `/v1/get-lineups` | Escalacoes | Fx | **OK** |
| playercareer | `/v1/player-teams-career` | Carreira jogador | Prsn | **OK** |
| referees | `/v1/get-by-prsn` | Stats arbitro | Prsn | **OK** |
| referees | `/v1/get-all` | Todos arbitros | tmcl | **OK** |

**Endpoints de Rankings (Retornam estrutura mas dados podem estar vazios):**

| Modulo | Endpoint | Parametros |
|--------|----------|------------|
| rankings | `/v1/player/get-players-by-rank` | tmcl, RankTypeName |
| rankings | `/v1/player/get-players-by-teamrank` | tmcl, RankTypeName, Ctst |
| rankings | `/v1/player/get-rank-by-player` | Prsn |
| rankings | `/v1/team/get-teams-by-rank` | tmcl, RankTypeName |
| rankings | `/v1/team/get-rank-by-team` | Ctst |

**Endpoints Premium (Requerem Autenticacao - 401):**

| Modulo | Endpoint | Descricao |
|--------|----------|-----------|
| bankroll-management | `/v1/get-all-bankrolls` | Gestao de banca |
| bankroll-management | `/v1/create-bankroll` | Criar banca |
| bet | `/v1/get-all-bets` | Listar apostas |
| bet | `/v1/create-bet` | Criar aposta |
| scanner | `/v1/get-opportunities` | Scanner de oportunidades |

**IMPORTANTE - Parametro `detailed`:**
- Use `detailed=yes` (string) NAO `detailed=true` (boolean)
- Sem este parametro, endpoints como teams, squads, seasonstats retornam vazio

---

## 5. Endpoints com Erro

### 5.1 Erro 500 - Internal Server Error

| Endpoint | Descricao | Nota |
|----------|-----------|------|
| `/stats/team/v1/teams` | Lista de times | |
| `/stats/matchstats/v1/get-games-stats` | Estatisticas de jogos | |
| `/stats/matchstats/v1/get-game-played-stats` | Stats de jogo disputado | **FUNCIONA** com partidas ja realizadas! Ver 4.8 |
| `/stats/matchstats/v1/get-detailed-stats` | Stats detalhadas | |
| `/stats/matchstats/v1/get-lineups` | Escalacoes | **FUNCIONA** com partidas ja realizadas! Ver 4.9 |
| `/stats/matchstats/v1/get-player-stats` | Stats de jogadores | |
| `/stats/matchstats/v1/get-games-stats-versus` | Confronto direto | |
| `/stats/squads/v1/get-squads` | Elencos | |
| `/stats/referees/v1/get-all` | Arbitros | |
| `/stats/seasonstats/v1/team` | Stats de temporada | |
| `/stats/rankings/v1/team/get-rank-by-team` | Ranking por time | |

**Nota importante sobre matchstats:** Os endpoints `get-game-played-stats` e `get-lineups` funcionam corretamente quando passado o ID de uma partida que **ja foi disputada**. O erro 500 ocorre apenas para partidas futuras ou IDs invalidos.

### 5.2 Erro 400 - Bad Request

| Endpoint | Parametros Faltantes | Status |
|----------|---------------------|--------|
| `/stats/matchpreview/v1/get-match-preview` | Requer "Fx" | RESOLVIDO - Ver secao 4.5 |
| `/stats/matchpreview/v1/get-team-form` | Requer "Fx" e "CtstId" | RESOLVIDO - Ver secao 4.6 |
| `/stats/seasonstats/v1/team` | Requer "detailed" | Retorna 500 mesmo com parametro |

### 5.3 Erro 404 - Not Found

| Endpoint | Observacao |
|----------|------------|
| `/stats/match/v1/details` | Nao existe |
| `/stats/rankings/v1/shots` | Nao existe nesse formato |
| `/stats/rankings/v1/corners` | Nao existe nesse formato |
| `/stats/rankings/v1/cards` | Nao existe nesse formato |
| `/stats/rankings/v1/discipline` | Nao existe nesse formato |
| `/stats/rankings/v1/attack` | Nao existe nesse formato |
| `/stats/rankings/v1/all` | Nao existe nesse formato |

### 5.4 Endpoints com Estrutura OK mas Dados Vazios

| Endpoint | Status | Resposta |
|----------|--------|----------|
| `/stats/rankings/v1/team/get-teams-by-rank?RankTypeName=corners` | 200 | `{"rank":[]}` |
| `/stats/rankings/v1/team/get-teams-by-rank?RankTypeName=cards` | 200 | `{"rank":[]}` |
| `/stats/rankings/v1/team/get-teams-by-rank?RankTypeName=shots` | 200 | `{"rank":[]}` |
| `/stats/rankings/v1/team/get-teams-by-rank?RankTypeName=goals` | 200 | `{"rank":[]}` |
| `/stats/rankings/v1/team/get-teams-by-rank?RankTypeName=attack` | 200 | `{"rank":[]}` |
| `/stats/rankings/v1/team/get-teams-by-rank?RankTypeName=defense` | 200 | `{"rank":[]}` |
| `/stats/rankings/v1/player/get-players-by-teamrank?RankTypeName=*` | 200 | `{"ranking":[]}` |

**Nota:** Os endpoints existem e aceitam os tipos (corners, cards, shots, etc.), mas o backend NAO esta populando os dados. Possiveis causas:
1. Feature desabilitada no backend
2. Requer autenticacao Premium
3. Dados ainda nao processados para a temporada atual

### 5.5 Endpoints Descobertos no JavaScript (Testar)

| Endpoint | Descricao |
|----------|-----------|
| `/stats/fixtures/v1/get-fixtures?tmcl=...&Live=true/false` | Lista fixtures (retorna 500) |
| `/stats/scanner/v1/get-opportunities?Fixtures=...` | Oportunidades (requer Fixtures) |
| `/stats/rankings/v1/team/get-rank-by-team` | Ranking por time (retorna 500) |
| `/stats/playercareer/v1/player-teams-career` | Carreira do jogador |
| `/stats/referees/v1/get-by-fx` | Arbitro por fixture |
| `/stats/referees/v1/get-by-prsn` | Arbitro por pessoa |

---

## 6. Estrutura de Dados

### 6.1 Campos por Time (15 campos)

| Campo | Tipo | Descricao | Exemplo |
|-------|------|-----------|---------|
| rank | integer | Posicao na tabela | `1` |
| rankStatus | string | Status (Champions League, Relegation) | `"UEFA Champions League"` |
| contestantId | string | ID unico do time | `"4dsgumo7d4zupm2ugsvm4zm4d"` |
| contestantName | string | Nome completo | `"Arsenal FC"` |
| contestantShortName | string | Nome curto | `"Arsenal"` |
| contestantCode | string | Codigo (3 letras) | `"ARS"` |
| points | integer | Pontos totais | `39` |
| matchesPlayed | integer | Jogos disputados | `17` |
| matchesWon | integer | Vitorias | `12` |
| matchesLost | integer | Derrotas | `2` |
| matchesDrawn | integer | Empates | `3` |
| goalsFor | integer | Gols marcados | `31` |
| goalsAgainst | integer | Gols sofridos | `10` |
| goaldifference | string | Saldo de gols (com sinal) | `"+21"` |
| lastSix | string | Ultimos 6 jogos (W/L/D) | `"WWLWDW"` |

### 6.2 Observacoes Importantes

**1. goaldifference e STRING, nao integer**
```python
# ERRADO
saldo = data['total']['goaldifference'] + 5  # TypeError!

# CORRETO
saldo = int(data['total']['goaldifference'])
```

**2. rankStatus pode estar ausente**
```python
status = team.get('rankStatus', 'Normal')  # Use .get()
```

**3. lastSix so existe em "total"**
```python
forma = data['total']['ranking'][0]['lastSix']  # OK
forma = data['home']['ranking'][0]['lastSix']   # KeyError!
```

**4. Typo na API:** `fistHalfAway` ao inves de `firstHalfAway`

---

## 7. Limitacoes e Solucoes

### Estatisticas AGORA Disponiveis (v4.0!)

Apos investigacao profunda, descobrimos que as estatisticas detalhadas **ESTAO DISPONIVEIS** atraves do endpoint `get-game-played-stats`:

**Escanteios (Corners)** - DISPONIVEL!
- corners por tempo (1T, 2T, FT) para cada time

**Cartoes (Cards)** - DISPONIVEL!
- yellowCards e redCards por tempo para cada time

**Chutes (Shots)** - DISPONIVEL!
- attempts (finalizacoes totais)
- attemptsOnGoal (finalizacoes no gol)

**Outras Estatisticas** - DISPONIVEIS!
- passes, fouls, offsides, saves

### Limitacao Principal

As estatisticas estao disponiveis **APENAS POR PARTIDA**, nao agregadas por equipe na temporada.

Para obter medias de uma equipe, e necessario:
1. Buscar IDs de partidas passadas via `get-match-preview` (campo `previousMeetingsAnyComp.ids`)
2. Iterar sobre cada partida chamando `get-game-played-stats`
3. Calcular as medias manualmente

### Estatisticas NAO Disponiveis

- Posse de bola
- Estatisticas agregadas por equipe na temporada (precisa calcular)
- Rankings de corners/cards/shots (endpoints vazios)

---

### 7.1 Calculando Medias de Equipes (Workaround) - NOVO v5.0!

Como a API NAO fornece medias pre-calculadas de estatisticas por equipe, e necessario calcular manualmente agregando dados de partidas individuais.

**Fluxo Completo para Analise Preditiva:**

```
┌─────────────────────────────────────────────────────────────┐
│  PASSO 1: Obter partida futura                              │
│                                                             │
│  schedule/month?Tmcl={id}                                   │
│  schedule/day?tmcl={id}&date=YYYY-MM-DD                     │
│     → Retorna Match ID da partida futura                    │
├─────────────────────────────────────────────────────────────┤
│  PASSO 2: Obter dados da partida e historico                │
│                                                             │
│  get-match-preview?Fx={matchId}                             │
│     → H2H (vitorias, empates, gols)                         │
│     → Forma atual (ultimos 6 jogos)                         │
│     → IDs de partidas anteriores (previousMeetingsAnyComp)  │
│                                                             │
│  get-match-stats?Fx={matchId}                               │
│     → Arbitragem (principal, VAR, assistentes)              │
├─────────────────────────────────────────────────────────────┤
│  PASSO 3: Buscar estatisticas de partidas passadas          │
│                                                             │
│  Para cada ID em previousMeetingsAnyComp.ids:               │
│                                                             │
│  get-game-played-stats?Fx={id}  →  Stats por TIME           │
│     corners, cards, shots, fouls, passes, saves             │
│     (array 6 elementos: Home FT, Away FT, H 1T, A 1T, ...)  │
│                                                             │
│  get-match-stats?Fx={id}  →  Stats por JOGADOR              │
│     22+ metricas individuais por jogador                    │
├─────────────────────────────────────────────────────────────┤
│  PASSO 4: Calcular medias                                   │
│                                                             │
│  Agregar dados das ultimas N partidas e calcular:           │
│     - Media de escanteios (corners)                         │
│     - Media de cartoes (yellowCards, redCards)              │
│     - Media de finalizacoes (attempts, attemptsOnGoal)      │
│     - Media de gols (marcados, sofridos)                    │
│     - Outras metricas conforme necessidade                  │
└─────────────────────────────────────────────────────────────┘
```

**Medias Disponiveis:**

| Por TIME (get-game-played-stats) | Por JOGADOR (get-match-stats) |
|----------------------------------|-------------------------------|
| Escanteios (corners) | Escanteios cobrados (cornerTaken) |
| Cartoes amarelos/vermelhos | Gols e assistencias |
| Finalizacoes (attempts) | Finalizacoes (totalScoringAtt) |
| Finalizacoes no gol (attemptsOnGoal) | Chutes no gol (shotOnTarget) |
| Passes totais | Passes (totalPass/accuratePass) |
| Faltas (fouls) | Faltas (fouls/wasFouled) |
| Impedimentos (offsides) | Desarmes (totalTackle/wonTackle) |
| Defesas (saves) | Minutos jogados (minsPlayed) |

**Metodologia Resumida:**

1. Obter IDs de partidas passadas via `get-match-preview`
2. Para cada partida, chamar `get-game-played-stats` (stats time) ou `get-match-stats` (stats jogador)
3. Agregar e calcular medias

**Exemplo Completo em Python:**

```python
import requests
from typing import Dict, List

BASE_URL = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"

def get_previous_match_ids(match_id: str, limit: int = 10) -> List[str]:
    """Obtem IDs de partidas anteriores de um confronto."""
    url = f"{BASE_URL}/stats/matchpreview/v1/get-match-preview"
    response = requests.get(url, params={"Fx": match_id})
    data = response.json()

    # IDs de todas as competicoes
    ids_str = data.get('previousMeetingsAnyComp', {}).get('ids', '')
    if not ids_str:
        return []

    all_ids = ids_str.split(',')
    return all_ids[:limit]

def get_match_stats(match_id: str) -> Dict:
    """Obtem estatisticas de uma partida realizada."""
    url = f"{BASE_URL}/stats/matchstats/v1/get-game-played-stats"
    response = requests.get(url, params={"Fx": match_id})

    if response.status_code != 200:
        return None

    return response.json()

def calculate_team_averages(match_ids: List[str], team_id: str) -> Dict:
    """Calcula medias de estatisticas para uma equipe."""
    stats_list = []

    for mid in match_ids:
        stats = get_match_stats(mid)
        if not stats:
            continue

        # Determinar se o time e home ou away
        is_home = stats.get('homeId') == team_id
        idx = 0 if is_home else 1  # Indice no array de stats

        match_stats = {
            'corners': int(stats['stats']['corners'][idx]),
            'yellowCards': int(stats['stats']['yellowCards'][idx]),
            'redCards': int(stats['stats']['redCards'][idx]),
            'attempts': int(stats['stats']['attempts'][idx]),
            'attemptsOnGoal': int(stats['stats']['attemptsOnGoal'][idx]),
            'fouls': int(stats['stats']['fouls'][idx]),
            'passes': int(stats['stats']['passes'][idx])
        }
        stats_list.append(match_stats)

    if not stats_list:
        return {}

    # Calcular medias
    n = len(stats_list)
    averages = {}
    for key in stats_list[0].keys():
        total = sum(s[key] for s in stats_list)
        averages[f'avg_{key}'] = round(total / n, 2)

    averages['matches_analyzed'] = n
    return averages

# Exemplo de uso:
# Arsenal vs Brighton (27/12/2025) - Match ID: 2wehv0cptselv086q8jud4hec
# Arsenal ID: 4dsgumo7d4zupm2ugsvm4zm4d

match_id = "2wehv0cptselv086q8jud4hec"
arsenal_id = "4dsgumo7d4zupm2ugsvm4zm4d"

# Obter ultimas 10 partidas do confronto
previous_ids = get_previous_match_ids(match_id, limit=10)

# Calcular medias do Arsenal
averages = calculate_team_averages(previous_ids, arsenal_id)

print("Medias do Arsenal (ultimas 10 partidas):")
print(f"  Escanteios: {averages.get('avg_corners', 'N/A')}")
print(f"  Cartoes Amarelos: {averages.get('avg_yellowCards', 'N/A')}")
print(f"  Finalizacoes: {averages.get('avg_attempts', 'N/A')}")
print(f"  Finalizacoes no Gol: {averages.get('avg_attemptsOnGoal', 'N/A')}")
```

**Estatisticas Calculaveis:**

| Estatistica | Campo no Array | Descricao |
|-------------|----------------|-----------|
| Escanteios | `corners` | Media de escanteios por partida |
| Cartoes Amarelos | `yellowCards` | Media de amarelos por partida |
| Cartoes Vermelhos | `redCards` | Media de vermelhos por partida |
| Finalizacoes | `attempts` | Media de chutes por partida |
| Finalizacoes no Gol | `attemptsOnGoal` | Media de chutes no gol por partida |
| Faltas | `fouls` | Media de faltas cometidas |
| Passes | `passes` | Media de passes por partida |
| Defesas | `saves` | Media de defesas do goleiro |

**Filtros Possiveis:**

- **Ultimas N partidas:** Limitar a lista de IDs
- **Por tempo:** Usar indices 2-3 (1T) ou 4-5 (2T) ao inves de 0-1 (FT)
- **Casa/Fora:** Verificar se `homeId` ou `awayId` corresponde ao time

**Nota Importante:** Este metodo requer multiplas chamadas a API (1 + N, onde N e o numero de partidas). Para evitar sobrecarga, recomenda-se implementar cache local dos resultados.

---

### 7.2 Estatisticas FEITAS vs SOFRIDAS - ATUALIZADO v5.3!

**DESCOBERTA CRUCIAL:** O campo `lostCorners` (corners sofridos) **EXISTE** no endpoint `get-match-stats`!

#### Estatisticas Disponiveis via seasonstats/v1/team (AGREGADO)

| Categoria | Estatistica FEITA | Estatistica SOFRIDA |
|-----------|-------------------|---------------------|
| **Corners** | Corners Won: 100 (avg: 5.88) ✅ | **NAO AGREGADO** (ver abaixo) |
| **Gols** | Goals: 31 (avg: 1.82) ✅ | Goals Conceded: 10 (avg: 0.59) ✅ |
| **Finalizacoes** | Total Shots: 184 (avg: 10.82) ✅ | Total Shots Conceded: 124 (avg: 7.29) ✅ |
| **Faltas** | Total Fouls Won: 178 (avg: 10.47) ✅ | Total Fouls Conceded: 166 (avg: 9.76) ✅ |

#### DESCOBERTA: Campo `lostCorners` no get-match-stats!

O endpoint `get-match-stats` retorna **diretamente** os corners sofridos atraves do campo `lostCorners`!

**Endpoint:**
```
GET /stats/matchstats/v1/get-match-stats?Fx={matchId}
```

**Localizacao:** `liveData.lineUp[].stat[]` onde `type = "lostCorners"`

**Exemplo de resposta:**
```json
{
  "liveData": {
    "lineUp": [
      {
        "contestantId": "e5p0ehyguld7egzhiedpdnc3w",  // Brighton
        "stat": [
          {"type": "wonCorners", "value": 2},
          {"type": "lostCorners", "value": 5},       // Corners SOFRIDOS!
          {"type": "cornerTaken", "value": 2}
        ]
      },
      {
        "contestantId": "4dsgumo7d4zupm2ugsvm4zm4d",  // Arsenal
        "stat": [
          {"type": "wonCorners", "value": 5},
          {"type": "lostCorners", "value": 2},       // Corners SOFRIDOS!
          {"type": "cornerTaken", "value": 5}
        ]
      }
    ]
  }
}
```

**Estatisticas por TIME disponiveis em get-match-stats:**

| Campo | Descricao |
|-------|-----------|
| `wonCorners` | Corners ganhos/forcados |
| `lostCorners` | **Corners SOFRIDOS** (cedidos ao adversario) |
| `cornerTaken` | Corners cobrados |
| `goals` | Gols marcados |
| `goalsConceded` | Gols sofridos |
| `totalScoringAtt` | Finalizacoes totais |
| `ontargetScoringAtt` | Finalizacoes no gol |
| `totalYellowCard` | Cartoes amarelos |
| `possessionPercentage` | Posse de bola |
| `totalPass` | Passes totais |
| `accuratePass` | Passes certos |
| `totalTackle` | Desarmes totais |
| `wonTackle` | Desarmes certos |
| `saves` | Defesas do goleiro |
| `totalClearance` | Afastamentos |

#### Como Calcular Corners Sofridos AGREGADOS

O `lostCorners` esta disponivel **por partida**, nao agregado na temporada. Para obter a media:

**Metodo 1: Via get-match-stats (RECOMENDADO - usa campo `lostCorners` direto)**

```python
import requests
from typing import List, Dict

BASE_URL = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"

def get_team_match_stats(match_id: str, team_id: str) -> Dict:
    """
    Obtem estatisticas de um time em uma partida via get-match-stats.
    Inclui lostCorners, wonCorners, goals, shots, etc.
    """
    url = f"{BASE_URL}/stats/matchstats/v1/get-match-stats?Fx={match_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()
    lineup = data.get('liveData', {}).get('lineUp', [])

    for team in lineup:
        if team.get('contestantId') == team_id:
            # Converter lista de stats para dicionario
            stats = {s.get('type'): s.get('value') for s in team.get('stat', [])}
            return stats

    return None


def calcular_corners_agregados(team_id: str, match_ids: List[str]) -> Dict:
    """
    Calcula corners FEITOS e SOFRIDOS de um time usando lostCorners.
    """
    won_total = 0
    lost_total = 0
    matches_count = 0

    for match_id in match_ids:
        stats = get_team_match_stats(match_id, team_id)
        if not stats:
            continue

        won = int(stats.get('wonCorners', 0))
        lost = int(stats.get('lostCorners', 0))  # CAMPO DIRETO!

        won_total += won
        lost_total += lost
        matches_count += 1

        print(f"Partida {matches_count}: wonCorners={won}, lostCorners={lost}")

    if matches_count > 0:
        return {
            'corners_won_total': won_total,
            'corners_won_avg': won_total / matches_count,
            'corners_lost_total': lost_total,
            'corners_lost_avg': lost_total / matches_count,
            'matches_analyzed': matches_count
        }

    return None


# Exemplo de uso:
ARSENAL_ID = "4dsgumo7d4zupm2ugsvm4zm4d"
match_ids = ["adxx1ue4e7h0i93pwl7xucr2s", "c3azlvd97gyv7x0unm43czw9g", "a5sr0ba7amh9cuylpfu6pev4k"]

result = calcular_corners_agregados(ARSENAL_ID, match_ids)
if result:
    print(f"\n=== TOTAIS Arsenal ({result['matches_analyzed']} partidas) ===")
    print(f"Corners Ganhos: {result['corners_won_total']} (media: {result['corners_won_avg']:.2f})")
    print(f"Corners Sofridos: {result['corners_lost_total']} (media: {result['corners_lost_avg']:.2f})")
```

**Saida esperada:**
```
Partida 1: wonCorners=8, lostCorners=2
Partida 2: wonCorners=5, lostCorners=2
Partida 3: wonCorners=3, lostCorners=7

=== TOTAIS Arsenal (3 partidas) ===
Corners Ganhos: 16 (media: 5.33)
Corners Sofridos: 11 (media: 3.67)
```

**Metodo 2: Via get-game-played-stats (alternativo - inferir do adversario)**

Caso o campo `lostCorners` nao esteja disponivel, pode-se inferir corners sofridos pegando os corners do adversario:

```
corners_sofridos = corners_do_adversario
```

Estrutura do array `corners` em get-game-played-stats:
```
["home_total", "away_total", "home_1T", "away_1T", "home_2T", "away_2T"]
```

#### Resumo COMPLETO: Campos Disponiveis por Endpoint

**CATEGORIA: CORNERS**
| Campo | seasonstats (agregado) | get-match-stats (por partida) |
|-------|------------------------|-------------------------------|
| Corners Ganhos | `Corners Won` | `wonCorners` |
| **Corners Sofridos** | NAO EXISTE* | **`lostCorners`** |

> **(Investigado 24/12/2025):** A Opta possui o campo `lost_corners` ("Corner conceded") na fonte original.
> A VStats expõe como `lostCorners` por partida, mas **NÃO agrega** no seasonstats.
> Diferente de `Total Shots Conceded` que é agregado, `Corners Conceded` foi omitido.
> **Solução:** Agregar manualmente via get-match-stats ou usar `wonCorners` do adversário.

**CATEGORIA: GOLS**
| Campo | seasonstats (agregado) | get-match-stats (por partida) |
|-------|------------------------|-------------------------------|
| Gols Marcados | `Goals` | `goals` |
| Gols Sofridos | `Goals Conceded` | `goalsConceded` |
| **Gols Sofridos Dentro Area** | `Goals Conceded Inside Box` | calcular |
| **Gols Sofridos Fora Area** | `Goals Conceded Outside Box` | calcular |

**CATEGORIA: FINALIZACOES**
| Campo | seasonstats (agregado) | get-match-stats (por partida) |
|-------|------------------------|-------------------------------|
| Finalizacoes | `Total Shots` | `totalScoringAtt` |
| **Finalizacoes Sofridas** | `Total Shots Conceded` ✅ | `totalScoringAtt` (adversario) |
| Finalizacoes no Gol | `Shots On Target` | `ontargetScoringAtt` |
| **Chutes no Gol Sofridos (dentro area)** | `Shots On Conceded Inside Box` ✅ | calcular |
| **Chutes no Gol Sofridos (fora area)** | `Shots On Conceded Outside Box` ✅ | calcular |

**CATEGORIA: FALTAS**
| Campo | seasonstats (agregado) | get-match-stats (por partida) |
|-------|------------------------|-------------------------------|
| Faltas Ganhas | `Total Fouls Won` | `fkFoulWon` |
| Faltas Cometidas | `Total Fouls Conceded` | `fkFoulLost` |
| **Maos na Bola** | `Handballs conceded` | NAO EXISTE |

**CATEGORIA: CARTOES**
| Campo | seasonstats (agregado) | get-match-stats (por partida) |
|-------|------------------------|-------------------------------|
| Cartoes Amarelos (do time) | `Yellow Cards` | `totalYellowCard` |
| **Cartoes Vermelhos** | NAO EXISTE | **`totalRedCard`** |
| **Segundo Amarelo** | NAO EXISTE | **`secondYellow`** |
| Cartoes Amarelos do Adversario | NAO EXISTE | calcular* |

*Para cartoes do adversario: agregar `totalYellowCard` do oponente em cada partida.

**CATEGORIA: PENALTIS**
| Campo | seasonstats (agregado) | get-match-stats (por partida) |
|-------|------------------------|-------------------------------|
| **Penaltis Ganhos** | NAO EXISTE | **`penaltyWon`** |
| **Penaltis Cometidos** | NAO EXISTE | **`penaltyConceded`** |
| **Penaltis Enfrentados** | NAO EXISTE | **`penaltyFaced`** |
| **Gols Penalti Sofridos** | NAO EXISTE | **`penGoalsConceded`** |

**CATEGORIA: DUELOS**
| Campo | seasonstats (agregado) | get-match-stats (por partida) |
|-------|------------------------|-------------------------------|
| Duelos Totais | `Duels` | NAO EXISTE |
| Duelos Ganhos | `Duels won` | NAO EXISTE |
| Duelos Perdidos | `Duels lost` | NAO EXISTE |
| Duelos Aereos | `Aerial Duels` | NAO EXISTE |
| Duelos Aereos Ganhos | `Aerial Duels won` | NAO EXISTE |
| Duelos Aereos Perdidos | `Aerial Duels lost` | NAO EXISTE |
| **Duelos Terrestres** | `Ground Duels` | NAO EXISTE |
| **Duelos Terrestres Ganhos** | `Ground Duels won` | NAO EXISTE |
| **Duelos Terrestres Perdidos** | `Ground Duels lost` | NAO EXISTE |

**CATEGORIA: DESARMES**
| Campo | seasonstats (agregado) | get-match-stats (por partida) |
|-------|------------------------|-------------------------------|
| Desarmes Ganhos | `Tackles Won` | `wonTackle` |
| Desarmes Perdidos | `Tackles Lost` | NAO EXISTE |
| Desarmes Total | NAO EXISTE | `totalTackle` |

**CATEGORIA: DEFESA**
| Campo | seasonstats (agregado) | get-match-stats (por partida) |
|-------|------------------------|-------------------------------|
| **Defesas Goleiro** | NAO EXISTE | **`saves`** |
| Cortes/Afastamentos | `Total Clearances` | `totalClearance` |
| Clean Sheets | `Clean Sheets` | `cleanSheet` |

**CATEGORIA: POSSE/PASSES**
| Campo | seasonstats (agregado) | get-match-stats (por partida) |
|-------|------------------------|-------------------------------|
| Posse de Bola | `Possession Percentage` | `possessionPercentage` |
| Passes Totais | `Total Passes` | `totalPass` |
| Passes Certos | NAO EXISTE | `accuratePass` |

#### Script Completo para Estatisticas Sofridas

Ver arquivo `scripts/utilitarios/calcular_estatisticas_sofridas.py`.

---

### 7.3 Escudos e Logos de Equipes (TheSportsDB)

A API VStats **NAO fornece** URLs de escudos/logos das equipes. A Opta/Stats Perform oferece imagens como servico separado (contrato adicional).

**Solucao:** Usar a API gratuita [TheSportsDB](https://www.thesportsdb.com/api.php) para obter escudos.

#### Endpoint

```
GET https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={nome_time}
```

#### Campos Disponiveis

| Campo | Descricao |
|-------|-----------|
| `strBadge` | URL do escudo (PNG) |
| `strLogo` | URL do logo |
| `strTeamJersey` | URL da camisa |
| `strTeam` | Nome oficial |
| `strLeague` | Liga |
| `strStadium` | Estadio |

#### Exemplo de Resposta

```json
{
  "teams": [{
    "strTeam": "Arsenal",
    "strLeague": "English Premier League",
    "strBadge": "https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png",
    "strLogo": "https://r2.thesportsdb.com/images/media/team/logo/q2mxlz1512644512.png",
    "strStadium": "Emirates Stadium"
  }]
}
```

#### Exemplo de Uso (Python)

```python
import requests

def get_team_badge(team_name: str) -> str:
    """Obtem URL do escudo via TheSportsDB"""
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        teams = data.get('teams', [])
        if teams:
            return teams[0].get('strBadge', '')
    return ''

# Uso com dados da VStats
team_name = "Arsenal"  # Obtido via VStats (contestantName)
badge_url = get_team_badge(team_name)
print(f"Escudo: {badge_url}")
```

#### Integracao com VStats

```python
def get_standings_with_badges(tournament_id: str):
    """Obtem classificacao com escudos"""
    # 1. Buscar standings via VStats
    url = f"{BASE_URL}/stats/standings/v1/standings"
    params = {"tmcl": tournament_id, "detailed": "false"}
    standings = requests.get(url, params=params).json()

    # 2. Adicionar escudos via TheSportsDB
    for team in standings.get('total', {}).get('ranking', []):
        team_name = team.get('contestantName', '')
        team['badge'] = get_team_badge(team_name)

    return standings
```

#### Limitacoes

- Busca por nome (pode haver ambiguidade)
- API gratuita (sem SLA)
- Recomendado: cachear URLs dos escudos

---

### 7.4 Coeficiente de Variacao (CV) - Estabilidade de Times

A API VStats **NAO fornece** Coeficiente de Variacao. E necessario calcular manualmente usando dados por partida.

#### O Que e o CV?

O **Coeficiente de Variacao** mede a estabilidade/consistencia de uma estatistica.
- **CV proximo de 0**: Time muito estavel e previsivel
- **CV proximo de 1+**: Time instavel e imprevisivel

**Formula:** `CV = Desvio Padrao / Media`

#### Escala de Interpretacao

| CV | Classificacao | Significado |
|----|---------------|-------------|
| 0.00 - 0.15 | Muito Estavel | Time muito consistente |
| 0.15 - 0.30 | Estavel | Time consistente |
| 0.30 - 0.50 | Moderado | Variacao normal |
| 0.50 - 0.75 | Instavel | Time inconsistente |
| 0.75+ | Muito Instavel | Resultados imprevisiveis |

#### Estatisticas Analisadas (FEITOS e SOFRIDOS)

| Categoria | FEITOS | SOFRIDOS |
|-----------|--------|----------|
| Corners | `wonCorners` | `lostCorners` |
| Gols | `goals` | `goalsConceded` |
| Finalizacoes | `totalScoringAtt` | (via adversario) |
| Finalizacoes Gol | `ontargetScoringAtt` | (via adversario) |
| Cartoes Amarelos | `totalYellowCard` | (adversario) |
| Cartoes Vermelhos | `totalRedCard` | (adversario) |
| Faltas | `fkFoulLost` (cometidas) | `fkFoulWon` (sofridas) |
| Penaltis | (a favor) | `penaltyConceded` |
| Defesas | `saves` | - |

#### Como Calcular

1. Obter IDs de partidas anteriores via `get-match-preview`
2. Para cada partida, obter estatisticas via `get-match-stats`
3. Calcular media e desvio padrao
4. CV = desvio padrao / media

#### Exemplo de Uso (Python)

```python
import statistics

def calculate_cv(values: list) -> dict:
    """Calcula CV para uma lista de valores por partida"""
    if len(values) < 2:
        return None

    mean = statistics.mean(values)
    std_dev = statistics.stdev(values)
    cv = std_dev / mean if mean > 0 else 0

    # Classificar
    if cv < 0.15:
        classification = "Muito Estavel"
    elif cv < 0.30:
        classification = "Estavel"
    elif cv < 0.50:
        classification = "Moderado"
    elif cv < 0.75:
        classification = "Instavel"
    else:
        classification = "Muito Instavel"

    return {
        "mean": mean,
        "std_dev": std_dev,
        "cv": cv,
        "classification": classification
    }

# Exemplo: Corners do Arsenal em 5 partidas
corners_feitos = [8, 5, 3, 6, 7]
corners_sofridos = [2, 5, 4, 3, 8]

cv_feitos = calculate_cv(corners_feitos)
cv_sofridos = calculate_cv(corners_sofridos)

print(f"Corners Feitos: CV={cv_feitos['cv']:.3f} ({cv_feitos['classification']})")
print(f"Corners Sofridos: CV={cv_sofridos['cv']:.3f} ({cv_sofridos['classification']})")
```

#### Exemplo de Saida (Arsenal - 3 partidas)

```
Estatistica                  Media   Desvio       CV   Classificacao
----------------------------------------------------------------------
goalsConceded                 1.00     0.00    0.000   Muito Estavel
totalYellowCard               3.00     0.00    0.000   Muito Estavel
fkFoulLost                   11.67     2.52    0.216         Estavel
totalScoringAtt              12.00     3.61    0.300        Moderado
goals                         1.33     0.58    0.433        Moderado
wonCorners                    5.33     2.52    0.472        Moderado
lostCorners                   3.67     2.89    0.787  Muito Instavel
```

#### Uso para Analise Preditiva

- **Times com CV baixo**: Mais previsiveis, apostas mais seguras
- **Times com CV alto**: Podem surpreender (positiva ou negativamente)
- **Comparar CV entre times**: Indica qual e mais confiavel
- **CV de gols sofridos alto**: Defesa inconsistente
- **CV de gols feitos alto**: Ataque inconsistente

#### Script Completo

Ver arquivo `scripts/utilitarios/calcular_coeficiente_variacao.py`.

---

### 7.5 Scripts de Validacao (Testados 24/12/2025)

Scripts criados para validar a disponibilidade de todos os campos necessarios para o sistema de analise.

#### 7.5.1 scripts/validacao/validar_seasonstats_geral.py

**Objetivo:** Validar campos do Filtro "Geral" (seasonstats)

**Resultado:** 10/10 campos CONFIRMADOS (100%)

| Campo API | Estatistica | Status |
|-----------|-------------|--------|
| `Corners Won` | Escanteios Feitos | OK |
| `Goals` | Gols Feitos | OK |
| `Goals Conceded` | Gols Sofridos | OK |
| `Total Shots` | Finalizacoes | OK |
| `Total Shots Conceded` | Finalizacoes Sofridas | OK |
| `Shots On Target ( inc goals )` | Finalizacoes ao Gol | OK |
| `Shots On Conceded Inside Box` | Finalizacoes ao Gol Sofridas (Dentro) | OK |
| `Shots On Conceded Outside Box` | Finalizacoes ao Gol Sofridas (Fora) | OK |
| `Yellow Cards` | Cartoes Amarelos | OK |
| `Red Cards` | Cartoes Vermelhos | OK (opcional) |

> **Nota:** `Corners Conceded` (escanteios sofridos) NAO existe no seasonstats. Usar `lostCorners` via get-match-stats.

**Uso:**
```bash
python scripts/validacao/validar_seasonstats_geral.py
```

#### 7.5.2 scripts/validacao/validar_get_match_stats.py

**Objetivo:** Validar campos dos Filtros "5" e "10 Partidas" (get-match-stats)

**Resultado:** Todos os campos obrigatorios presentes

| Campo API | Estatistica | Presenca |
|-----------|-------------|----------|
| `wonCorners` | Escanteios Feitos | 100% |
| `lostCorners` | Escanteios Sofridos | **100% CONFIRMADO!** |
| `goals` | Gols Feitos | 100% |
| `goalsConceded` | Gols Sofridos | 75% (condicional) |
| `totalScoringAtt` | Finalizacoes | 100% |
| `ontargetScoringAtt` | Finalizacoes ao Gol | 100% |
| `totalYellowCard` | Cartoes Amarelos | 75% (condicional) |
| `totalRedCard` | Cartoes Vermelhos | 25% (raro) |

**Validacoes Adicionais Confirmadas:**
- Calculo via adversario (finalizacoes sofridas): VALIDADO
- CV calculado corretamente para todas as metricas
- Classificacao de estabilidade funcionando

**Uso:**
```bash
python scripts/validacao/validar_get_match_stats.py
```

#### 7.5.3 Resumo da Validacao

| Filtro | Script | Resultado |
|--------|--------|-----------|
| Geral (temporada) | `scripts/validacao/validar_seasonstats_geral.py` | 10/10 (100%) |
| 5 Partidas | `scripts/validacao/validar_get_match_stats.py` | Todos OK |
| 10 Partidas | `scripts/validacao/validar_get_match_stats.py` | Todos OK |

**Conclusao:** Sistema validado e pronto para implementacao!

---

## 8. Exemplos de Uso

### 8.1 Python - Obter Classificacao de um Time

```python
import requests

BASE_URL = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"

def get_team_stats(tournament_id, team_code):
    url = f"{BASE_URL}/stats/standings/v1/standings"
    params = {"tmcl": tournament_id, "detailed": "false"}

    response = requests.get(url, params=params)
    data = response.json()

    # Buscar time em todos os rankings
    team_stats = {}
    for ranking_type in ['total', 'home', 'away']:
        for team in data[ranking_type]['ranking']:
            if team['contestantCode'] == team_code:
                team_stats[ranking_type] = team
                break

    return team_stats

# Exemplo: Arsenal na Premier League
arsenal = get_team_stats("51r6ph2woavlbbpk8f29nynf8", "ARS")

print(f"Posicao: {arsenal['total']['rank']}")
print(f"Pontos: {arsenal['total']['points']}")
print(f"Saldo: {arsenal['total']['goaldifference']}")
print(f"Forma: {arsenal['total']['lastSix']}")
```

---

### 8.2 JavaScript - Listar Competicoes por Pais

```javascript
const axios = require('axios');

const BASE_URL = 'https://vstats-back-bbdfdf0bfd16.herokuapp.com/api';

async function getCompetitionsByCountry(country) {
    const response = await axios.get(
        `${BASE_URL}/stats/tournament/v1/calendar`,
        { params: { detailed: 'false' } }
    );

    return response.data.filter(comp => comp.country === country);
}

// Exemplo
(async () => {
    const brazil = await getCompetitionsByCountry('Brazil');
    brazil.forEach(comp => {
        console.log(`${comp.translatedName} - ${comp.tournamentCalendarId}`);
    });
})();
```

---

### 8.3 Bash - Obter Top 5

```bash
curl -s "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/stats/standings/v1/standings?tmcl=51r6ph2woavlbbpk8f29nynf8&detailed=false" \
  | jq '.total.ranking[0:5] | .[] | {rank, team: .contestantShortName, points}'
```

---

### 8.4 PHP - Wrapper Simples

```php
class VStatsAPI {
    private $baseUrl = 'https://vstats-back-bbdfdf0bfd16.herokuapp.com/api';

    public function getStandings($tournamentId) {
        $url = $this->baseUrl . '/stats/standings/v1/standings';
        $url .= '?tmcl=' . $tournamentId . '&detailed=false';

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);

        return json_decode($response, true);
    }
}

$api = new VStatsAPI();
$standings = $api->getStandings('51r6ph2woavlbbpk8f29nynf8');
echo "Lider: " . $standings['total']['ranking'][0]['contestantShortName'];
```

---

## 9. Caso de Uso: Arsenal vs Crystal Palace

### Informacoes da Partida

| Campo | Valor |
|-------|-------|
| Data | 23 de Dezembro de 2025 |
| Horario | 17:00 (UK) / 14:00 (BRT) |
| Competicao | English League Cup (Quartas de Final) |
| Match ID | f4vscquffy37afgv0arwcbztg |
| Tournament ID | 6lhltebj0dx79xptn0hyph5as |

### Times

| Time | ID | Codigo |
|------|-----|--------|
| Arsenal FC (Mandante) | 4dsgumo7d4zupm2ugsvm4zm4d | ARS |
| Crystal Palace FC (Visitante) | 1c8m2ko0wxq1asfkuykurdr0y | CRY |

---

### Estatisticas da Premier League 2025/26

#### Arsenal FC (Mandante)

**Classificacao Geral:**
- Posicao: 1 lugar - LIDER DA PREMIER LEAGUE
- Status: Classificado para UEFA Champions League
- Pontos: 39 (12V-3E-2D)
- Gols: 31 marcados, 10 sofridos (Saldo: +21)
- Forma Recente: WWLWDW (4 vitorias, 1 empate, 1 derrota nos ultimos 6)
- Aproveitamento: 76.5%

**Desempenho em Casa (Emirates Stadium):**
- Posicao no Ranking Casa: 2 lugar
- Pontos: 22 em 24 possiveis
- Jogos: 8 (7V-1E-0D)
- INVICTO EM CASA (0 derrotas)
- Gols: 20 marcados, 3 sofridos (Saldo: +17)
- Media de Gols: 2.50 marcados / 0.38 sofridos por jogo
- Aproveitamento: 91.7%

**Primeiro Tempo - Casa:**
- Posicao: 2 lugar
- Pontos no 1 Tempo: 19
- Gols no 1 Tempo: 8 marcados, 1 sofrido
- Desempenho: 6V-1E-1D

---

#### Crystal Palace FC (Visitante)

**Classificacao Geral:**
- Posicao: 8 lugar
- Pontos: 26 (7V-5E-5D)
- Gols: 21 marcados, 19 sofridos (Saldo: +2)
- Forma Recente: LLWWLW (3 vitorias, 3 derrotas nos ultimos 6)
- Aproveitamento: 51.0%

**Desempenho Fora de Casa:**
- Posicao no Ranking Fora: 2 lugar
- Pontos: 16 em 27 possiveis
- Jogos: 9 (5V-1E-3D)
- Gols: 12 marcados, 9 sofridos (Saldo: +3)
- Media de Gols: 1.33 marcados / 1.00 sofridos por jogo
- Aproveitamento: 59.3%

**Primeiro Tempo - Fora:**
- Posicao: 2 lugar
- Pontos no 1 Tempo: 15
- Gols no 1 Tempo: 5 marcados, 4 sofridos
- Desempenho: 4V-3E-2D

---

### Analise Comparativa

| Metrica | Arsenal | Crystal Palace | Vantagem |
|---------|---------|----------------|----------|
| Posicao Geral | 1 | 8 | Arsenal (+7) |
| Pontos (Geral) | 39 | 26 | Arsenal (+13) |
| Gols Marcados | 31 | 21 | Arsenal (+10) |
| Gols Sofridos | 10 | 19 | Arsenal (-9) |
| Saldo de Gols | +21 | +2 | Arsenal (+19) |
| Aproveitamento % | 76.5% | 51.0% | Arsenal (+25.5%) |

### Arsenal Casa vs Palace Fora

| Metrica | Arsenal Casa | Palace Fora | Diferenca |
|---------|--------------|-------------|-----------|
| Pontos/Jogo | 2.75 | 1.78 | Arsenal (+0.97) |
| Vitorias % | 87.5% | 55.6% | Arsenal (+31.9%) |
| Gols Marcados/Jogo | 2.50 | 1.33 | Arsenal (+1.17) |
| Gols Sofridos/Jogo | 0.38 | 1.00 | Arsenal (-0.62) |
| Saldo/Jogo | +2.13 | +0.33 | Arsenal (+1.80) |

---

### Pontos Fortes

**Arsenal:**
- Lider invicto da Premier League
- Invicto em casa (7V-1E-0D)
- Melhor defesa da liga (10 gols sofridos em 17 jogos)
- Defesa impenetravel em casa (apenas 3 gols sofridos em 8 jogos)
- Alta eficiencia ofensiva (2.50 gols/jogo em casa)
- Aproveitamento de 91.7% em casa

**Crystal Palace:**
- 2 melhor visitante da Premier League
- Boa forma fora (5V em 9 jogos)
- Equilibrio defensivo fora (1.00 gol sofrido/jogo)
- 3 vitorias nos ultimos 6 jogos

---

### Ranking Comparativo Premier League

| Categoria | Arsenal | Crystal Palace |
|-----------|---------|----------------|
| Classificacao Geral | 1 | 8 |
| Classificacao Casa | 2 | 15 |
| Classificacao Fora | 1 | 2 |
| Primeiro Tempo Geral | 2 | 3 |
| Primeiro Tempo Casa | 2 | 10 |
| Primeiro Tempo Fora | 4 | 2 |

**Destaque:** Crystal Palace e o 2 melhor time fora da Premier League.

---

## 10. Metodologia de Descoberta

### 10.1 Analise Frontend

- **Site:** Angular SPA (https://vstats.com.br)
- **Framework Backend:** Express.js
- **Chunks analisados:** `chunk-SQZ4MXU4.js`, `chunk-K2DR4PV4.js`

### 10.2 Extracao de URLs

- Regex em JavaScript minificado
- Padroes: `/stats/[resource]/v1/[action]`
- URLs hardcodeadas com configuracoes

### 10.3 Validacao

- 37+ testes de endpoints
- Validacao com dados reais (Arsenal FC, Premier League)
- Documentacao de erros (500, vazios)

### 10.4 Limitacoes Identificadas

- Endpoints quebrados (erro 500)
- Dados faltantes (corners, cards, shots)
- Parametro `detailed` sem efeito

---

## 11. Guia para Descoberta de Novos Endpoints

### Objetivo

Identificar endpoints da API VStats que retornam estatisticas detalhadas (chutes, escanteios, cartoes).

### Passo 1: Navegar ate o Site

Acesse: **https://vstats.com.br**

### Passo 2: Encontrar Pagina com Estatisticas Detalhadas

Navegue para uma pagina que mostre as estatisticas de chutes, escanteios e cartoes de um time.

**Sugestoes de navegacao:**
1. Procure por "Premier League" ou "Brasileirao"
2. Clique em um time (ex: Arsenal, Flamengo, Palmeiras)
3. Procure por abas/secoes como:
   - "Estatisticas"
   - "Stats"
   - "Analise"
   - "Desempenho"

### Passo 3: Monitorar Requisicoes HTTP

Quando encontrar a pagina com as estatisticas detalhadas, monitore as requisicoes de rede.

**Procure por:**
- Requisicoes para o dominio: `vstats-back-bbdfdf0bfd16.herokuapp.com`
- URLs contendo `/stats/` ou `/api/stats/`
- Requisicoes que retornem JSON com dados numericos

**Ignore:**
- Requisicoes para analytics/tracking
- Requisicoes para CDNs (cloudflare, etc.)
- Arquivos CSS/JS/imagens

### Passo 4: Capturar Dados da Requisicao

Para CADA requisicao relevante encontrada, capture:

1. **URL Completa**
2. **Metodo HTTP** (GET, POST, etc.)
3. **Parametros da Query String**
4. **Headers importantes** (Authorization, Content-Type)
5. **Resposta JSON**

---

### Evidencias no Codigo JavaScript

Encontramos referencias no codigo minificado do site:

**Escanteios:**
- `corners`, `cornersFT`, `cornersHT`, `totalCorners`
- `wonCorners`, `lostCorners`
- `firstCorner`, `raceCorners`, `moreCornersFirstHalf`

**Cartoes:**
- `yellowCard`, `redCard`

**Chutes:**
- `shotOffTarget`, `shotOnTarget`

**Medias:**
- `avgFirstHalf`, `avgSecondHalf`, `avgValue`

---

## 12. IDs de Referencia

### Tournament Calendar IDs (tmcl)

| Competicao | ID |
|------------|-----|
| Premier League | `51r6ph2woavlbbpk8f29nynf8` |
| La Liga | `80zg2v1cuqcfhphn56u4qpyqc` |
| Bundesliga | `2bchmrj23l9u42d68ntcekob8` |
| Serie A (Italy) | `emdmtfr1v8rey2qru3xzfwges` |
| Brasileirao Serie A | `752zalnunu0zkdfbbm915kys4` |
| English League Cup | `6lhltebj0dx79xptn0hyph5as` |

### Contestant IDs (ctst) - Exemplos

| Time | ID |
|------|-----|
| Arsenal FC | `4dsgumo7d4zupm2ugsvm4zm4d` |
| Manchester City | `a3nyxabgsqlnqfkeg41m6tnpp` |
| Liverpool FC | `c8h9bw1l82s06h77xxrelzhur` |
| Crystal Palace FC | `1c8m2ko0wxq1asfkuykurdr0y` |

---

## 13. Erros Comuns e Solucoes

### 400 - Bad Request

```json
{
  "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
  "title": "One or more validation errors occurred.",
  "status": 400,
  "errors": {
    "Tmcl": ["The Tmcl field is required."]
  }
}
```

**Solucao:** Incluir parametro `tmcl` valido

### 500 - Internal Server Error

**Endpoints afetados:** teams, matchstats, squads, referees, seasonstats

**Motivo:** Erro na implementacao backend

### 404 - Not Found

**Endpoints afetados:** match/v1/details

**Motivo:** Endpoint nao existe ou foi removido

---

## 14. Licenca e Uso

**AVISO:** API descoberta atraves de analise de codigo frontend publico.

Antes de usar em producao:
1. Verificar termos de servico do vstats.com.br
2. Obter permissao explicita dos proprietarios
3. Respeitar rate limits
4. Usar apenas para fins educacionais/pesquisa

---

## Resumo de Status

| Recurso | Status | Dados Disponiveis |
|---------|--------|-------------------|
| Classificacao | Funcional | 15 campos completos |
| Competicoes | Funcional | 33+ competicoes |
| Schedule (dia) | Funcional | 16 campos |
| Schedule (mes) | Funcional | Partidas do mes |
| **Schedule por Data** | **NOVO v5.0 FUNCIONAL!** | Partidas de data especifica |
| Match Preview | Funcional | Confrontos, forma, venue |
| Team Form | Funcional | Forma por time |
| H2H (Confrontos) | Funcional | Via Match Preview |
| Gols/Pontos | Disponivel | Total, casa, fora |
| Forma recente | Disponivel | Ultimos 6 jogos |
| Rankings jogadores | Estrutura OK | Dados vazios |
| Escanteios | Funcional | Por partida (FT, 1T, 2T) |
| Cartoes | Funcional | Por partida (amarelos, vermelhos) |
| Chutes | Funcional | Por partida (total, no gol) |
| Escalacoes | Funcional | Por partida realizada |
| Match stats | Funcional | Estatisticas completas por partida |
| Timeline | Funcional | Eventos da partida (gols, escanteios, etc.) |
| **Medias por Equipe (feitos)** | **DISPONIVEL v5.2!** | Via seasonstats/v1/team |
| **Medias por Equipe (sofridos)** | **DISPONIVEL v5.3!** | Via get-match-stats por partida (lostCorners, saves, etc.) |
| **Arbitragem** | **NOVO v5.0 FUNCIONAL!** | Via get-match-stats (partidas futuras!) |
| **Stats por Jogador** | **NOVO v5.0 FUNCIONAL!** | Via get-match-stats (partidas passadas) |

---

## Referencias

- **Frontend:** https://vstats.com.br
- **API Backend:** https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/
- **Documentacao Completa:** 23/12/2025
- **Metodo:** Analise de JavaScript minificado + Testes HTTP

---

**Documentacao gerada:** 23 de Dezembro de 2025
**Versao:** 5.0 - Analise Preditiva: Schedule por Data + Calculo de Medias
**Status:** Completa e Validada

---

## Changelog

### Versao 5.5 (24/12/2025) - NOVO: Coeficiente de Variacao (CV)
- **NOVO:** Secao 7.4 - Coeficiente de Variacao (CV) para analise de estabilidade
- **NOVO:** Script `scripts/utilitarios/calcular_coeficiente_variacao.py` para calcular CV de estatisticas
- **FORMULA:** CV = Desvio Padrao / Media (quanto mais proximo de 0, mais estavel)
- **ESCALA:** 0.00-0.15 (Muito Estavel), 0.15-0.30 (Estavel), 0.30-0.50 (Moderado), 0.50-0.75 (Instavel), 0.75+ (Muito Instavel)
- **ESTATISTICAS:** CV para FEITOS e SOFRIDOS (wonCorners/lostCorners, goals/goalsConceded, etc.)
- **CATEGORIAS:** Corners, Gols, Finalizacoes, Cartoes, Faltas, Penaltis, Passes, Defesas
- **USO:** Identificar times consistentes vs imprevisiveis para apostas
- **DESCOBERTA:** VStats API NAO fornece CV/variancia - calculo manual via get-match-stats

### Versao 5.4 (24/12/2025) - NOVO: Escudos via TheSportsDB
- **INVESTIGACAO:** VStats API NAO fornece URLs de escudos/logos de equipes
- **SOLUCAO:** Integracao com TheSportsDB (API gratuita) para obter escudos
- **NOVO:** Secao 7.3 - Escudos e Logos de Equipes
- **TESTADO:** Arsenal, Man City, Crystal Palace - URLs funcionando (HTTP 200, image/png)
- **ENDPOINT:** `https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={nome}`
- **CAMPOS:** strBadge (escudo), strLogo (logo), strTeamJersey (camisa)
- **EXEMPLO:** Codigo Python para integracao VStats + TheSportsDB

### Versao 5.3 (23/12/2025) - DESCOBERTA: Estatisticas Defensivas Completas!
- **DESCOBERTA CRUCIAL:** O campo `lostCorners` (corners sofridos) **EXISTE** no endpoint `get-match-stats`!
- **CONFIRMADO:** Endpoint `get-match-stats` retorna `lostCorners` por time em `liveData.lineUp[].stat[]`
- **NOVO:** Secao 7.2 - Estatisticas FEITAS vs SOFRIDAS completa por categoria
- **NOVO:** Script `scripts/utilitarios/calcular_estatisticas_sofridas.py` com TODAS as estatisticas defensivas
- **NOVO:** Tabelas comparativas por categoria: Corners, Gols, Finalizacoes, Faltas, Cartoes, Penaltis, Duelos, Desarmes, Defesa, Posse
- **DESCOBERTA:** Campos EXCLUSIVOS do get-match-stats (NAO existem no seasonstats):
  - `lostCorners` - corners sofridos
  - `penaltyConceded` - penaltis cometidos
  - `penaltyFaced` - penaltis enfrentados
  - `penGoalsConceded` - gols de penalti sofridos
  - `totalRedCard` - cartoes vermelhos
  - `secondYellow` - segundo amarelo
  - `saves` - defesas do goleiro
- **DESCOBERTA:** Campos EXCLUSIVOS do seasonstats (NAO existem no get-match-stats):
  - Duels lost, Aerial Duels lost
  - Tackles Lost
  - Total Shots Conceded (agregado)
- **TABELA:** Comparativo completo de 30+ campos entre seasonstats e get-match-stats
- **EXEMPLO:** Script `scripts/utilitarios/calcular_corners_sofridos.py` atualizado com metodo lostCorners
- **ATUALIZADO:** Resumo de Status com medias feitos/sofridos

### Versao 5.2 (24/12/2025) - DESCOBERTA CRUCIAL: Medias Pre-Calculadas!
- **DESCOBERTA CRUCIAL:** Endpoint `seasonstats/v1/team` com `detailed=yes` retorna MEDIAS PRE-CALCULADAS!
- **NOVO:** Secao 4.15 - Season Stats com 50+ metricas agregadas (corners, cards, shots, goals, etc.)
- **NOVO:** Secao 4.16 - Teams endpoint lista todos times com info (id, name, code, city, founded)
- **NOVO:** Secao 4.17 - Squads endpoint retorna elenco completo (jogadores, posicao, altura, peso, pe)
- **NOVO:** Secao 4.18 - Schedule Week retorna agenda semanal
- **NOVO:** Secao 4.19 - Team Form retorna forma recente (WDLWWL)
- **CORRECAO:** Parametro `detailed` deve ser "yes" (string) NAO "true" (boolean)
- **DESCOBERTA:** Endpoints de bankroll/bet requerem autenticacao (401 Unauthorized)
- **DESCOBERTA:** Rankings retornam estrutura mas dados podem estar vazios
- **ATUALIZADO:** Modelo freemium identificado (matchesForFree, oddtoken)
- **ATUALIZADO:** Mapa de endpoints v5.2 com status de todos os testes
- **ANALISE:** API VStats NAO requer token para endpoints /stats/* (publicos!)

### Versao 5.1 (24/12/2025) - Mapa Completo de Endpoints!
- **DESCOBERTA IMPORTANTE:** Analise do codigo-fonte revelou TODOS os endpoints da API VStats!
- **NOVO:** Endpoint `tournament/v1/calendar` retorna lista de TODAS as 32 competicoes com IDs (secao 4.13)
- **NOVO:** Endpoint `referees/v1/get-all` retorna todos arbitros de uma competicao (secao 4.11.2)
- **NOVO:** Mapa completo de endpoints documentado (secao 4.14)
- **DESCOBERTA:** Endpoints adicionais identificados: fixtures, seasonstats, squads, rankings, etc.
- **DESCOBERTA:** Varios endpoints requerem parametros especificos (Live, detailed, ctst, etc.)
- **ATUALIZADO:** Lista de competicoes agora vem direto da API, nao hardcoded
- **ATUALIZADO:** Status da descoberta com novos recursos
- **CONFIRMADO:** Opta (Stats Perform) e o provedor de dados (via optaEventId)

### Versao 5.0 (23/12/2025) - Analise Preditiva!
- **NOVO:** Endpoint `schedule/day?date=YYYY-MM-DD` para buscar partidas de data especifica (secao 4.11)
- **NOVO:** Endpoint `get-match-stats` retorna ARBITRAGEM para partidas FUTURAS! (secao 4.9)
- **NOVO:** Endpoint `get-match-stats` retorna STATS INDIVIDUAIS POR JOGADOR para partidas passadas
- **NOVO:** 22+ tipos de estatisticas por jogador documentados (goals, assists, corners, tackles, etc.)
- **NOVO:** Estrutura de gols, cartoes e substituicoes detalhada
- **NOVO:** Metodologia para calculo de medias de equipes documentada (secao 7.1)
- **DESCOBERTA:** API NAO fornece medias pre-calculadas (corners, cards, shots por temporada)
- **DESCOBERTA:** `get-match-stats` e mais completo que `get-game-played-stats` para analise por jogador
- **WORKAROUND:** Agregar dados de partidas individuais via `get-game-played-stats` ou `get-match-stats`
- **FALLBACK:** Documentado fallback de `schedule/day` para `schedule/month` quando parametro date falha
- **ATUALIZADO:** Resumo de Status com novos recursos (arbitragem, stats por jogador)
- **ATUALIZADO:** Secao de Limitacoes com workaround para medias
- **EXEMPLO:** Codigo Python completo para calcular medias de uma equipe
- **EXEMPLO:** Boxing Day 2025 (Man Utd vs Newcastle) como caso de teste

### Versao 4.0 (23/12/2025) - DESCOBERTA IMPORTANTE!
- **DESCOBERTA CRUCIAL:** Endpoint `get-game-played-stats` FUNCIONA para partidas ja realizadas!
- **NOVO:** Estatisticas de escanteios disponiveis (corners por tempo: FT, 1T, 2T)
- **NOVO:** Estatisticas de cartoes disponiveis (yellowCards, redCards)
- **NOVO:** Estatisticas de finalizacoes disponiveis (attempts, attemptsOnGoal)
- **NOVO:** Estatisticas de passes, faltas (fouls), impedimentos (offsides), defesas (saves)
- **NOVO:** Escalacoes completas com formacao tatica (squads)
- **NOVO:** Timeline de eventos da partida (gols, escanteios, substituicoes, etc.)
- **NOVO:** Endpoint `get-lineups` documentado (secao 4.9)
- **ATUALIZADO:** Secao 7 (Limitacoes) reflete as novas descobertas
- **ATUALIZADO:** Resumo de Status com todos os recursos funcionais
- **DESCOBERTA:** Arrays de stats tem 6 elementos: [Home FT, Away FT, Home 1T, Away 1T, Home 2T, Away 2T]

### Versao 3.0 (23/12/2025)
- **NOVO:** Endpoint Match Preview descoberto e documentado
- **NOVO:** Endpoint Team Form descoberto e documentado
- **NOVO:** Endpoint Schedule Month documentado
- **ATUALIZADO:** Player Rankings aceita multiplos tipos (corners, cards, shots, etc.)
- **ATUALIZADO:** Lista de endpoints 404 expandida
- **CORRIGIDO:** Parametros Fx e CtstId documentados corretamente

### Versao 2.0 (23/12/2025)
- Documentacao unificada de 4 arquivos
- Caso de uso Arsenal vs Crystal Palace adicionado

### Versao 1.0 (23/12/2025)
- Documentacao inicial da API
