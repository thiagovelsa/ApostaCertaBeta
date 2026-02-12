# Especificação da API Própria

**Versão:** 1.2
**Data:** 11 de fevereiro de 2026
**Base URL:** `http://localhost:8000/api` (desenvolvimento)
**OpenAPI:** `/docs` (Swagger UI) e `/redoc` (ReDoc)

---

## 1. Overview

API RESTful para análise de estatísticas de futebol. Integra dados da **VStats API** e **TheSportsDB** para fornecer análises detalhadas de partidas e desempenho de times.

### 1.1 Características

- ✅ Endpoints totalmente documentados com exemplos
- ✅ Respostas em JSON
- ✅ Validação automática de inputs
- ✅ CORS habilitado para frontend
- ✅ Caching de respostas (veja TTLs)

### 1.2 Autenticação

**Nota:** Os endpoints públicos não requerem autenticação. A API VStats é chamada com credenciais server-side.

### 1.3 Status Codes

| Status | Significado | Exemplo |
|--------|-------------|---------|
| **200** | OK - Requisição bem-sucedida | Partidas encontradas |
| **400** | Bad Request - Parâmetro inválido | Data no formato errado |
| **404** | Not Found - Recurso não existe | Partida não encontrada |
| **500** | Server Error - Erro interno | VStats API indisponível |

---

## 2. Endpoints

### 2.1 GET /api/partidas

Lista partidas agendadas para uma data específica.

#### Request

**Parâmetros:**

| Nome | Tipo | Localização | Obrigatório | Descrição |
|------|------|-------------|-------------|-----------|
| `data` | string | query | ✅ Sim | Data no formato `YYYY-MM-DD` |

**Exemplos:**

```http
GET /api/partidas?data=2025-12-27
GET /api/partidas?data=2025-12-25
```

#### Response

**Status 200 - OK**

```json
{
  "data": "2025-12-27",
  "total_partidas": 2,
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
        "escudo": "https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png"
      },
      "visitante": {
        "id": "1c8m2ko0wxq1asfkuykurdr0y",
        "nome": "Crystal Palace",
        "codigo": "CRY",
        "escudo": "https://r2.thesportsdb.com/images/media/team/badge/ia6i3m1656014992.png"
      }
    }
  ]
}
```

**Status 400 - Bad Request**

```json
{
  "detail": "Data inválida: 2025-13-01 (formato deve ser YYYY-MM-DD)"
}
```

**Status 500 - Server Error**

```json
{
  "detail": "Erro ao buscar partidas da VStats API"
}
```

#### Comportamento

- Busca partidas de **todas as competições** para a data especificada
- Retorna array vazio se nenhuma partida encontrada
- Cache: **1 hora** (partidas não mudam frequentemente)
- Timeout: **10 segundos** para resposta

#### Fluxo Interno

```
1. Valida formato da data (YYYY-MM-DD)
2. Busca schedule do mês via VStats API
3. Filtra por data (client-side)
4. Para cada partida:
   - Busca escudos via TheSportsDB
   - Mapeia para PartidaResumo
5. Armazena em cache por 1h
6. Retorna PartidaListResponse
```

#### Exemplos com cURL

```bash
# Partidas de 27/12/2025
curl -X GET "http://localhost:8000/api/partidas?data=2025-12-27" \
  -H "Accept: application/json"

# Data inválida (erro)
curl -X GET "http://localhost:8000/api/partidas?data=27-12-2025" \
  -H "Accept: application/json"
```

---

### 2.2 GET /api/partida/{matchId}/stats

Obtém estatísticas detalhadas de uma partida específica com filtros de período.

#### Request

**Parâmetros:**

| Nome | Tipo | Localização | Obrigatório | Descrição | Valores |
|------|------|-------------|-------------|-----------|---------|
| `matchId` | string | path | ✅ Sim | ID da partida | ex: `f4vscquffy37afgv0arwcbztg` |
| `filtro` | string | query | ❌ Não (default: geral) | Quantidade máxima de jogos disputados por time | `geral` (até 50), `5` (até 5), `10` (até 10) |
| `periodo` | string | query | ❌ Não (default: integral) | Recorte do jogo | `integral`, `1T`, `2T` |
| `home_mando` | string | query | ❌ Não | Subfiltro de mando do mandante | `casa`, `fora` |
| `away_mando` | string | query | ❌ Não | Subfiltro de mando do visitante | `casa`, `fora` |

**Exemplos:**

```http
GET /api/partida/f4vscquffy37afgv0arwcbztg/stats
GET /api/partida/f4vscquffy37afgv0arwcbztg/stats?filtro=5
GET /api/partida/f4vscquffy37afgv0arwcbztg/stats?filtro=10
GET /api/partida/f4vscquffy37afgv0arwcbztg/stats?filtro=10&periodo=1T
GET /api/partida/f4vscquffy37afgv0arwcbztg/stats?filtro=5&periodo=integral&home_mando=casa&away_mando=fora
```

#### Response

**Status 200 - OK**

```json
{
  "partida": {
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
  },
  "filtro_aplicado": "5",
  "partidas_analisadas": 5,
  "partidas_analisadas_mandante": 5,
  "partidas_analisadas_visitante": 5,
  "mandante": {
    "id": "4dsgumo7d4zupm2ugsvm4zm4d",
    "nome": "Arsenal",
    "escudo": "https://...",
    "estatisticas": {
      "escanteios": {
        "feitos": {"media": 5.88, "cv": 0.32, "classificacao": "Moderado"},
        "sofridos": {"media": 3.50, "cv": 0.28, "classificacao": "Estável"}
      },
      "gols": {
        "feitos": {"media": 1.82, "cv": 0.41, "classificacao": "Moderado"},
        "sofridos": {"media": 0.59, "cv": 0.65, "classificacao": "Instável"}
      },
      "finalizacoes": {
        "feitos": {"media": 10.82, "cv": 0.25, "classificacao": "Estável"},
        "sofridos": {"media": 8.20, "cv": 0.35, "classificacao": "Moderado"}
      },
      "finalizacoes_gol": {
        "feitos": {"media": 4.50, "cv": 0.30, "classificacao": "Moderado"},
        "sofridos": {"media": 2.80, "cv": 0.40, "classificacao": "Moderado"}
      },
      "cartoes_amarelos": {"media": 1.29, "cv": 0.55, "classificacao": "Instável"},
      "faltas": {"media": 12.4, "cv": 0.40, "classificacao": "Moderado"}
    }
  },
  "visitante": {
    "id": "1c8m2ko0wxq1asfkuykurdr0y",
    "nome": "Crystal Palace",
    "escudo": "https://...",
    "estatisticas": {
      "escanteios": {
        "feitos": {"media": 4.20, "cv": 0.45, "classificacao": "Moderado"},
        "sofridos": {"media": 5.10, "cv": 0.52, "classificacao": "Instável"}
      },
      "gols": {
        "feitos": {"media": 1.20, "cv": 0.55, "classificacao": "Instável"},
        "sofridos": {"media": 1.40, "cv": 0.48, "classificacao": "Moderado"}
      },
      "finalizacoes": {
        "feitos": {"media": 8.50, "cv": 0.38, "classificacao": "Moderado"},
        "sofridos": {"media": 9.80, "cv": 0.42, "classificacao": "Moderado"}
      },
      "finalizacoes_gol": {
        "feitos": {"media": 3.20, "cv": 0.45, "classificacao": "Moderado"},
        "sofridos": {"media": 3.50, "cv": 0.38, "classificacao": "Moderado"}
      },
      "cartoes_amarelos": {"media": 1.80, "cv": 0.62, "classificacao": "Instável"},
      "faltas": {"media": 11.1, "cv": 0.42, "classificacao": "Moderado"}
    }
  }
}
```

**Status 400 - Bad Request**

```json
{
  "detail": "filtro inválido: deve ser 'geral', '5' ou '10'"
}
```

**Status 404 - Not Found**

```json
{
  "detail": "Partida com ID 'abc123xyz' não encontrada"
}
```

**Status 500 - Server Error**

```json
{
  "detail": "Erro ao calcular estatísticas"
}
```

#### Behavior

- **Período `geral`**: Até 50 partidas disputadas (com placar) **de cada time**
- **Período `5`**: Últimas 5 partidas **de cada time** (mandante e visitante)
- **Período `10`**: Últimas 10 partidas **de cada time** (mandante e visitante)
- **Observação:** se houver menos jogos do que o limite (5/10/50), o backend calcula com as partidas disponíveis.
- **Subfiltro `periodo` (integral/1T/2T):** quando a VStats fornece estatísticas por tempo, o backend recorta 1T/2T; caso contrário, faz fallback para o total do jogo (integral) e registra `periodo_fallback_integral` em `contexto.ajustes_aplicados`.
- **Fallback `seasonstats` (agregado):** se não houver partidas individuais suficientes (ou a VStats falhar ao retornar stats por partida), o backend usa agregados da temporada e registra `seasonstats_fallback` em `contexto.ajustes_aplicados`. Nesse modo, `partidas_analisadas_*` e `partidas_analisadas` podem refletir `matchesPlayed` da temporada e, portanto, podem ser maiores do que `5`/`10` (o filtro solicitado continua sendo útil como “intenção”, mas o payload deixa explícito que a fonte virou agregado).
- **Regras de seleção de partidas (base do filtro):** entram apenas partidas com `localDate` válida e **placar disponível** (já disputadas). Isso inclui jogos de hoje que já terminaram e evita que jogos adiados/sem placar “roubem” slots do “últimos N”.
- **Amostra no payload:**
  - `partidas_analisadas_mandante` e `partidas_analisadas_visitante` refletem a amostra real por lado (pode divergir por subfiltros/erros best-effort).
  - `partidas_analisadas` é o **n efetivo** (menor lado) usado para previsões/intervalos.
- Cache: **6 horas** por combinação de `matchId` + `filtro` + `periodo` + `home_mando` + `away_mando`

#### Fluxo Interno

```
1. Valida matchId (não vazio)
2. Valida filtro (geral/5/10)
3. Verifica cache: "stats:{matchId}:{filtro}:{periodo}:{home_mando}:{away_mando}"
4. Se não encontrado:
   a. Busca metadados da partida (preferencialmente a partir do cache criado em `/api/partidas`)
   b. Busca schedule do torneio (com cache)
   c. Busca histórico do time mandante (últimas até N ou até 50, conforme filtro)
   d. Busca histórico do time visitante (últimas até N ou até 50, conforme filtro)
   e. Calcula CV e médias para cada categoria (por partida quando disponível)
   f. Armazena em cache por 6h
5. Retorna StatsResponse
```

#### Exemplos com cURL

```bash
# Estatísticas com período geral (default)
curl -X GET "http://localhost:8000/api/partida/f4vscquffy37afgv0arwcbztg/stats" \
  -H "Accept: application/json"

# Últimas 5 partidas
curl -X GET "http://localhost:8000/api/partida/f4vscquffy37afgv0arwcbztg/stats?filtro=5" \
  -H "Accept: application/json"

# Últimas 10 partidas
curl -X GET "http://localhost:8000/api/partida/f4vscquffy37afgv0arwcbztg/stats?filtro=10" \
  -H "Accept: application/json"
```

---

### 2.3 GET /api/partida/{matchId}/analysis

Retorna uma análise consolidada em um único payload:
- estatísticas (`/stats`)
- previsões (expected values)
- probabilidades over/under

#### Request

**Parâmetros:**

| Nome | Tipo | Localização | Obrigatório | Descrição | Valores |
|------|------|-------------|-------------|-----------|---------|
| `matchId` | string | path | ✅ Sim | ID da partida | ex: `f4vscquffy37afgv0arwcbztg` |
| `filtro` | string | query | ❌ Não (default: geral) | Quantidade máxima de jogos disputados por time | `geral` (até 50), `5` (até 5), `10` (até 10) |
| `periodo` | string | query | ❌ Não (default: integral) | Recorte do jogo | `integral`, `1T`, `2T` |
| `home_mando` | string | query | ❌ Não | Subfiltro de mando do mandante | `casa`, `fora` |
| `away_mando` | string | query | ❌ Não | Subfiltro de mando do visitante | `casa`, `fora` |
| `debug` | boolean | query | ❌ Não (default: false) | Quando `true`/`1`, inclui `debug_amostra` (IDs/datas/pesos usados no recorte). Útil para auditoria/envio para IA. | `0/1`, `false/true` |

**Exemplos:**

```http
GET /api/partida/f4vscquffy37afgv0arwcbztg/analysis
GET /api/partida/f4vscquffy37afgv0arwcbztg/analysis?filtro=5&periodo=integral
GET /api/partida/f4vscquffy37afgv0arwcbztg/analysis?filtro=10&periodo=2T&home_mando=casa&away_mando=fora
GET /api/partida/f4vscquffy37afgv0arwcbztg/analysis?filtro=10&debug=1
```

#### Response

**Status 200 - OK**

Retorna tudo que o endpoint `/stats` retorna, mais:
- `previsoes` - Valores esperados para cada métrica
- `over_under` - Probabilidades over/under por linha

Quando `debug=1`, também inclui:
- `debug_amostra` (por lado: mandante/visitante)
  - `match_ids`, `match_dates` e `weights` usados no cálculo

**Nota de performance:** com `debug=1` o backend evita cache para não inflar payload/cache keys.

**Exemplo de Response:**

```json
{
  "partida": { ... },
  "filtro_aplicado": "5",
  "partidas_analisadas": 5,
  "mandante": { ... },
  "visitante": { ... },
  "previsoes": {
    "gols": {
      "home": { "valor": 1.8, "confianca": 0.75, "confiancaLabel": "Alta" },
      "away": { "valor": 0.9, "confianca": 0.68, "confiancaLabel": "Média" },
      "total": { "valor": 2.7, "confianca": 0.72, "confiancaLabel": "Alta" }
    },
    "escanteios": { ... },
    "finalizacoes": { ... },
    "finalizacoes_gol": { ... },
    "cartoes_amarelos": { ... },
    "faltas": { ... }
  },
  "over_under": {
    "gols": {
      "label": "Gols",
      "icon": "goal",
      "lambda": 2.7,
      "lambdaHome": 1.8,
      "lambdaAway": 0.9,
      "predMin": 1.2,
      "predMax": 4.2,
      "intervalLevel": 0.9,
      "distribution": "poisson",
      "lines": [
        { "line": 1.5, "over": 0.72, "under": 0.28, "ci_lower": 0.65, "ci_upper": 0.79, "uncertainty": 0.07 },
        { "line": 2.5, "over": 0.45, "under": 0.55, "ci_lower": 0.38, "ci_upper": 0.52, "uncertainty": 0.07 }
      ],
      "confidence": 0.72,
      "confidenceLabel": "Alta"
    },
    "escanteios": { ... },
    ...
  }
}
```

#### Modelos Estatísticos

| Métrica | Distribuição | Parâmetros |
|---------|--------------|------------|
| Gols | Poisson + Dixon-Coles | λ_home, λ_away, ρ (correlação) |
| Escanteios | Negative Binomial | μ, α (overdispersion) |
| Finalizações | Negative Binomial | μ, α |
| Finalizações no Gol | Negative Binomial | μ, α |
| Cartões Amarelos | Negative Binomial | μ, α (+ ajuste árbitro) |
| Faltas | Negative Binomial | μ, α |

**Dixon-Coles:** Ajusta a subestimação de placares baixos (0-0, 1-0, 0-1, 1-1) com fator de correlação ρ negativo.

**Negative Binomial:** Melhor que Poisson para métricas com overdispersion (variância > média), comum em escanteios e cartões.

**Intervalos de Confiança:** Calculados via simulação Monte Carlo (3000 iterações) amostrando da distribuição posterior.

---

### 2.4 GET /api/competicoes

Lista todas as competições disponíveis.

#### Request

**Parâmetros:** Nenhum

**Exemplo:**

```http
GET /api/competicoes
```

#### Response

**Status 200 - OK**

```json
{
  "total": 2,
  "competicoes": [
    {
      "id": "51r6ph2woavlbbpk8f29nynf8",
      "nome": "Premier League 2025/26",
      "pais": "Inglaterra",
      "tipo": "Liga"
    },
    {
      "id": "tournament_id_2",
      "nome": "La Liga 2025/26",
      "pais": "Espanha",
      "tipo": "Liga"
    }
  ]
}
```

**Status 500 - Server Error**

```json
{
  "detail": "Erro ao buscar lista de competições"
}
```

#### Comportamento

- Retorna todas as competições suportadas
- Cache: **12 horas**
- Timeout: **10 segundos**

---

### 2.5 GET /api/time/{teamId}/escudo

Obtém escudo/logo de um time.

#### Request

**Parâmetros:**

| Nome | Tipo | Localização | Obrigatório | Descrição |
|------|------|-------------|-------------|-----------|
| `teamId` | string | path | ✅ Sim | ID do time |
| `nome` | string | query | ❌ Não | Nome do time (fallback se teamId não funcionar) |

**Exemplos:**

```http
GET /api/time/4dsgumo7d4zupm2ugsvm4zm4d/escudo
GET /api/time/4dsgumo7d4zupm2ugsvm4zm4d/escudo?nome=Arsenal
```

#### Response

**Status 200 - OK**

```json
{
  "team_id": "4dsgumo7d4zupm2ugsvm4zm4d",
  "team_name": "Arsenal",
  "escudo_url": "https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png",
  "fonte": "TheSportsDB"
}
```

**Status 404 - Not Found**

```json
{
  "detail": "Escudo não encontrado para time '4dsgumo7d4zupm2ugsvm4zm4d'"
}
```

**Status 500 - Server Error**

```json
{
  "detail": "Erro ao buscar escudo do time"
}
```

#### Comportamento

- Busca escudo via TheSportsDB
- Fallback: se `teamId` não encontrado, tenta buscar por `nome`
- Cache: **7 dias** (escudos não mudam)
- Timeout: **5 segundos**

---

## 3. Headers HTTP

### 3.1 Request Headers Recomendados

```http
Accept: application/json
Content-Type: application/json (se enviando body)
User-Agent: Frontend/1.0
```

### 3.2 Response Headers

```http
Content-Type: application/json; charset=utf-8
Cache-Control: max-age=3600  (varia por endpoint)
```

---

## 4. CORS (Cross-Origin Resource Sharing)

**Origens Permitidas:**
- `http://localhost:3000` (dev frontend)
- `http://localhost:5173` (Vite dev server)
- `http://localhost:5174` (Vite dev server alt)
- `http://localhost:5175` (Vite dev server alt)

**Métodos Permitidos:** GET

**Headers Permitidos:** Content-Type, Authorization

---

## 5. Estratégia de Cache

| Endpoint | TTL | Cache Key |
|----------|-----|-----------|
| `/api/partidas` | 1 hora | `v{cache_version}:partidas:{data}` |
| `/api/partida/{id}/stats` | 6 horas | `v{cache_version}:stats:{matchId}:{filtro}:{periodo}:{home_mando}:{away_mando}` |
| `/api/partida/{id}/analysis` | (indireto) | usa o mesmo cache do `/stats` (exceto `debug=1`, que evita cache) |
| `/api/competicoes` | 12 horas | `v{cache_version}:competicoes:list` |
| `/api/time/{id}/escudo` | 7 dias | `v{cache_version}:escudo:{teamId}` |

**Invalidação Manual:**
- Limpar cache de partida ao editar dados
- Invalidar escudos ao atualizar TheSportsDB

---

## 6. Tratamento de Erros

### 7.1 Código de Erro Padrão

```json
{
  "detail": "Descrição do erro"
}
```

### 7.2 Tratamento Recomendado no Frontend

```javascript
async function fetchAPI(endpoint, params = {}) {
  try {
    const response = await fetch(endpoint, { method: 'GET' });

    if (response.status === 200) {
      return await response.json();
    } else if (response.status === 400) {
      throw new Error('Parâmetro inválido');
    } else if (response.status === 404) {
      throw new Error('Recurso não encontrado');
    } else {
      throw new Error('Erro no servidor');
    }
  } catch (error) {
    console.error('Erro na API:', error);
  }
}
```

---

## 8. Exemplos de Fluxo Completo

### 8.1 Buscar partidas e estatísticas

```javascript
// 1. Buscar partidas
const partidas = await fetch('http://localhost:8000/api/partidas?data=2025-12-27')
  .then(r => r.json());

// 2. Para cada partida, buscar estatísticas
const stats = await Promise.all(
  partidas.partidas.map(p =>
    fetch(`http://localhost:8000/api/partida/${p.id}/stats?filtro=5`)
      .then(r => r.json())
  )
);

// 3. Renderizar na UI
stats.forEach(s => {
  console.log(`${s.partida.mandante.nome} vs ${s.partida.visitante.nome}`);
  console.log(`Mandante - Gols: ${s.mandante.estatisticas.gols.feitos.media}`);
  console.log(`Visitante - Gols: ${s.visitante.estatisticas.gols.feitos.media}`);
});
```

---

## 9. Documentação Interativa

A documentação interativa (Swagger UI) está disponível em:

```
http://localhost:8000/docs
```

Requer servidor rodando em `uvicorn app.main:app --reload`

---

## 10. Versionamento

**Versão Atual:** 1.0 (sem prefixo de versão na URL)

**Plano Futuro:**
- v2 com autenticação
- v2 com histórico de previsões
- v2 com estatísticas customizadas

---

## Referências

- OpenAPI 3.0 Spec: https://spec.openapis.org/oas/v3.0.3
- HTTP Status Codes: https://httpwg.org/specs/rfc7231.html#status.codes
- REST API Best Practices: https://restfulapi.net/

---

## Ver Também

Para implementar e testar esses endpoints, consulte:

- **[MODELOS_DE_DADOS.md](MODELOS_DE_DADOS.md)** - Definição completa de todos os schemas de request/response
- **[ARQUITETURA_BACKEND.md](ARQUITETURA_BACKEND.md)** - Como a API é estruturada internamente em camadas
- **[ENDPOINTS_EXTERNOS_COMPLETO.md](ENDPOINTS_EXTERNOS_COMPLETO.md)** - TODOS endpoints externos (VStats, TheSportsDB, Opta, Wikidata)
- **[openapi.yaml](../openapi.yaml)** - Contrato OpenAPI exportado do projeto (o `/docs` do FastAPI é gerado em runtime)
- **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)** - Como testar os endpoints com integration tests
- **[LOCAL_SETUP.md](LOCAL_SETUP.md)** - Como rodar a API localmente para testar
- **[tests/README.md](../tests/README.md)** - Exemplos práticos de testes para endpoints HTTP
- **[AGENTS.md](../AGENTS.md)** - Diretrizes do repositório (workflow e padrões)

**Próximos Passos Recomendados:**
1. Entenda a estrutura interna consultando [ARQUITETURA_BACKEND.md](ARQUITETURA_BACKEND.md)
2. Implemente os schemas segundo [MODELOS_DE_DADOS.md](MODELOS_DE_DADOS.md)
3. Configure seu ambiente com [LOCAL_SETUP.md](LOCAL_SETUP.md)
4. Implemente os endpoints e teste usando padrões em [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
5. Verifique a documentação interativa em http://localhost:8000/docs (gerada pelo FastAPI em runtime)
