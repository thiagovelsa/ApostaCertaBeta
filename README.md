# ⚽ Sistema de Análise de Estatísticas de Futebol

Sistema web completo para análise detalhada de estatísticas de futebol, integrando dados da **VStats API** e **TheSportsDB** para fornecer insights sobre desempenho de times, estabilidade e previsões.

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009933)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Features Principais

- ✅ **Visualização de Partidas** - Liste todas as partidas agendadas para uma data específica
- ✅ **Análise Comparativa** - Compare estatísticas do time mandante vs visitante
- ✅ **Filtros Flexíveis** - Análise por período (até 50 jogos, últimas até 5 ou 10 partidas)
- ✅ **Métricas de Estabilidade** - Coeficiente de Variação (CV) para avaliar consistência
- ✅ **Sequência de Resultados** - Race badges (V/E/D) mostrando forma recente dos times
- ✅ **Previsões Inteligentes** - Análise preditiva baseada em médias e tendências
- ✅ **Análise Automática** - Análise automática de todas as partidas destacando o que considerar e o que evitar
- ✅ **Exportar JSON (IA)** - Baixe um `.json` completo da partida (recorte atual + 10 corridos + 5 casa/fora), com opção de debug (amostra usada)
- ✅ **Dados do Árbitro** - Estatísticas de cartões por árbitro na competição
- ✅ **API RESTful Completa** - Endpoints bem documentados com Swagger/OpenAPI
- ✅ **Caching Inteligente** - Redis para performance (TTLs otimizados)
- ✅ **CORS Configurado** - Pronto para frontend em produção
- ✅ **Testes Automatizados** - Unit tests + integration tests com pytest

---

## 🚀 Quick Start

### Pré-requisitos

- **Python 3.11+**
- **Node.js 20.19+ ou 22.12+** (Vite 7; para frontend)
- **Redis** (opcional se usar cache)

### 1. Obter o Projeto

Opções:
- Baixar como `.zip` (GitHub/GitLab) e extrair
- Clonar com Git (opcional)

```bash
# Exemplo (opcional)
git clone <url-do-repositorio>
cd ApostaMestre
```

### 2. Configurar Backend

```bash
# (Recomendado) criar venv dentro de /backend
cd backend
python -m venv .venv

# Ativar venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate      # Windows

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# A API lê ".env" do diretório atual.
# Rodando de /backend, crie backend/.env a partir do template da raiz:
cp ../.env.example .env

# Rodar servidor de desenvolvimento
uvicorn app.main:app --reload --port 8000
```

Servidor rodando em: **http://localhost:8000**
Swagger UI em: **http://localhost:8000/docs**

### 3. Configurar Frontend (Opcional)

```bash
cd frontend

# Instalar dependências
npm install

# Rodar desenvolvimento
npm run dev

# (Opcional) Limpar build local
npm run clean
```

Frontend em: **http://localhost:5173** ou **http://localhost:3000**

---

## 📚 Documentação

**Documentação técnica completa** em `/docs` (14+ documentos):

### Backend (FastAPI)
| Documento | Descrição |
|-----------|-----------|
| **[ARQUITETURA_BACKEND.md](docs/ARQUITETURA_BACKEND.md)** | Arquitetura em camadas, padrões, estrutura de pastas |
| **[MODELOS_DE_DADOS.md](docs/MODELOS_DE_DADOS.md)** | Schemas Pydantic, validações, exemplos |
| **[API_SPECIFICATION.md](docs/API_SPECIFICATION.md)** | Endpoints, request/response, exemplos |
| **[LOCAL_SETUP.md](docs/LOCAL_SETUP.md)** | Setup local passo-a-passo, troubleshooting |
| **[TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)** | Estratégia de testes, fixtures, mocks |

### Frontend (React + TypeScript)
| Documento | Descrição |
|-----------|-----------|
| **[docs/frontend/DESIGN_SYSTEM.md](docs/frontend/DESIGN_SYSTEM.md)** | Design tokens, cores, tipografia, componentes visuais |
| **[docs/frontend/COMPONENTES_REACT.md](docs/frontend/COMPONENTES_REACT.md)** | Catálogo de 25 componentes (Atomic Design) |
| **[docs/frontend/INTEGRACAO_API.md](docs/frontend/INTEGRACAO_API.md)** | Services, React Query hooks, type mappings |
| **[docs/frontend/ARQUITETURA_FRONTEND.md](docs/frontend/ARQUITETURA_FRONTEND.md)** | Folder structure, Zustand stores, React Router |
| **[docs/frontend/RESPONSIVIDADE_E_ACESSIBILIDADE.md](docs/frontend/RESPONSIVIDADE_E_ACESSIBILIDADE.md)** | Mobile-first design, WCAG AA, PWA |

### Sistema e APIs Externas
| Documento | Descrição |
|-----------|-----------|
| **[docs/DOCUMENTACAO_VSTATS_COMPLETA.md](docs/DOCUMENTACAO_VSTATS_COMPLETA.md)** | Referência completa da API VStats (fornecedor) |

---

## 🏗️ Arquitetura

```
API Backend (FastAPI)
├── Routes (Validação HTTP)
├── Services (Lógica de Negócio)
├── Repositories (Acesso a APIs Externas)
├── Models (Pydantic Schemas)
└── Utils (Helpers, Cálculos)
     │
     ├─→ VStats API (Estatísticas)
     ├─→ TheSportsDB API (Escudos)
     └─→ Redis Cache (Performance)
```

**Tech Stack:**

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18 + TypeScript 5 + Vite 7 + TailwindCSS + Zustand + React Query |
| **Backend** | Python 3.11+ + FastAPI + Pydantic |
| **Cache** | Redis |
| **APIs Externas** | VStats + TheSportsDB |
| **Tests** | Pytest (backend) |

---

## 📊 Endpoints da API

### Endpoints VStats Utilizados

| Endpoint | Uso |
|----------|-----|
| `/stats/tournament/v1/calendar` | Lista dinâmica de competições (32+) |
| `/stats/tournament/v1/schedule` | **Partidas da temporada completa** (preferido) |
| `/stats/matchstats/v1/get-match-stats` | **Stats por partida** (`liveData.lineUp[].stat[]`) |
| `/stats/seasonstats/v1/team` | Agregados da temporada |
| `/stats/referees/v1/get-by-prsn` | Estatísticas do árbitro |

### Estatísticas
- `GET /api/partida/{matchId}/stats?filtro=geral|5|10&periodo=integral|1T|2T&home_mando=casa|fora&away_mando=casa|fora`
- `GET /api/partida/{matchId}/analysis?filtro=geral|5|10&periodo=integral|1T|2T&home_mando=casa|fora&away_mando=casa|fora&debug=0|1`

Notas rápidas:
- `filtro=5|10` busca as últimas N partidas **de cada time** (mandante e visitante). O payload inclui `partidas_analisadas_mandante`/`partidas_analisadas_visitante` e um `partidas_analisadas` (n efetivo = menor lado) para previsões.
- `filtro=geral` usa **até 50** partidas disputadas (com placar) de cada time.
- Se o time não tiver a quantidade do filtro (5/10/50), o backend calcula com o que houver (mais próximo do filtro).
- `periodo=1T|2T` recorta stats do 1º/2º tempo quando disponível; caso contrário faz fallback para `integral` e registra `periodo_fallback_integral` em `contexto.ajustes_aplicados`.
- **Fallback `seasonstats` (agregado):** se não houver partidas individuais suficientes para o recorte (ou a VStats não retornar dados por partida), o backend usa agregados de temporada e registra `seasonstats_fallback` em `contexto.ajustes_aplicados`. Nesse caso, as contagens de amostra podem refletir a temporada (e podem ser > 5/10).
- `home_mando`/`away_mando` segmentam a amostra por casa/fora. Quando qualquer um estiver ativo, o ajuste automático de mando do modelo de previsão é desativado (a amostra já está segmentada).
- `debug=1` (apenas em `/analysis`) inclui `debug_amostra` com IDs/datas/pesos das partidas usadas no cálculo. Observação: `debug=1` evita cache para não inflar o payload.

### Competições
- `GET /api/competicoes` - Lista todas as competições

### Times
- `GET /api/time/{teamId}/escudo` - Escudo/logo do time

**Documentação Interativa:** http://localhost:8000/docs (Swagger UI)

---

## ⚙️ Configuração

O template completo fica em `.env.example`.

Observação importante: o backend lê `.env` do diretório em que você está rodando o `uvicorn` (rodando de `backend/`, use `backend/.env`).

---

## 🧪 Testes

```bash
# Rodar todos os testes
pytest

# Com coverage
pytest --cov=app --cov-report=html

# Apenas unit tests
pytest tests/unit/

# Apenas integration tests
pytest tests/integration/

# Com output detalhado
pytest -v -s
```

**Cobertura Mínima:** 80%

---

## 🐳 Docker

No estado atual do repositório, não há `Dockerfile`/`docker-compose.yml` prontos para uso.

---

## 📈 Métricas Monitoradas

- **Performance:** Tempo de resposta < 2s
- **Disponibilidade:** 99%+ uptime
- **Cache Hit Ratio:** 85%+
- **Test Coverage:** 80%+
- **Code Quality:** Linting com Black/Ruff

---

## 🔄 Workflow de Desenvolvimento

1. **Branch** - Criar feature branch (`git checkout -b feature/novo-endpoint`)
2. **Código** - Implementar seguindo arquitetura em `docs/ARQUITETURA_BACKEND.md`
3. **Testes** - Escrever testes (unit + integration)
4. **Commit** - Mensagens descritivas em português
5. **PR** - Code review antes de merge
6. **Deploy** - Merge em `main` dispara CI/CD

---

## 🚨 Common Issues

| Problema | Solução |
|----------|---------|
| Stats timeout | Frontend `.env` com `VITE_API_TIMEOUT=60000` |
| `/schedule/day?date=` vazio | Usar `/schedule` e filtrar client-side |
| `/schedule/month` só retorna mês atual | Usar `/schedule` (temporada completa) |
| IDs de competição mudam | Usar `/calendar` dinâmico |
| VStats API timeout | Verificar credenciais e URL em `.env` |
| Redis connection error | `docker run -d -p 6379:6379 redis` |
| CORS error no frontend | Adicionar origem em `ALLOWED_ORIGINS` no `.env` |
| Testes falhando | Verificar fixtures em `tests/conftest.py` |

Veja [LOCAL_SETUP.md](docs/LOCAL_SETUP.md) para troubleshooting detalhado.

---

## 📝 Scripts Úteis

```bash
# Validar dados de exemplo
python scripts/validacao/validar_seasonstats_geral.py

# Calcular CV para times
python scripts/utilitarios/calcular_coeficiente_variacao.py

# Extrair campos específicos
python scripts/utilitarios/extract_arsenal_fields.py

# Comparar dados
python scripts/utilitarios/compare_detailed.py
```

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma feature branch (`git checkout -b feature/seu-nome`)
3. Commit suas mudanças (`git commit -m 'Adiciona novo endpoint'`)
4. Push para a branch (`git push origin feature/seu-nome`)
5. Abra um Pull Request

Diretrizes do repositório: veja `AGENTS.md` e `CLAUDE.md`.

---

## 📞 Suporte

- **Issues:** use o tracker do repositório
- **Email:** contato@palpitremestre.com
- **Discord:** [Link do Server]

---

## 📄 Licença

Este projeto está licenciado sob MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **VStats API** - Dados de estatísticas de futebol
- **TheSportsDB** - Logos e informações de times
- **FastAPI Community** - Framework incrível
- **Contadores** - Contribuidores da comunidade

---

## 📚 Documentação Relacionada

**Documentação Técnica Detalhada:** Todos os 9 documentos técnicos formam um sistema interconectado para melhor contexto:

### Arquitetura e Design
- **[ARQUITETURA_BACKEND.md](docs/ARQUITETURA_BACKEND.md)** → Estrutura em camadas, padrões, pastas
  - Referencia: [MODELOS_DE_DADOS.md](docs/MODELOS_DE_DADOS.md), [API_SPECIFICATION.md](docs/API_SPECIFICATION.md)

- **[MODELOS_DE_DADOS.md](docs/MODELOS_DE_DADOS.md)** → Schemas Pydantic completos
  - Referencia: [ARQUITETURA_BACKEND.md](docs/ARQUITETURA_BACKEND.md), [API_SPECIFICATION.md](docs/API_SPECIFICATION.md)

### Implementação e Testing
- **[API_SPECIFICATION.md](docs/API_SPECIFICATION.md)** → Endpoints documentados
  - Referencia: [MODELOS_DE_DADOS.md](docs/MODELOS_DE_DADOS.md), [LOCAL_SETUP.md](docs/LOCAL_SETUP.md)

- **[TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)** → Estratégia de testes (70% unit, 20% integration)
  - Referencia: [tests/README.md](tests/README.md), [LOCAL_SETUP.md](docs/LOCAL_SETUP.md)

- **[tests/README.md](tests/README.md)** → Guia prático de testes com exemplos
  - Referencia: [TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md), [MODELOS_DE_DADOS.md](docs/MODELOS_DE_DADOS.md)

### Setup
- **[LOCAL_SETUP.md](docs/LOCAL_SETUP.md)** → Configuração ambiente completa + troubleshooting
  - Referencia: [ARQUITETURA_BACKEND.md](docs/ARQUITETURA_BACKEND.md), [TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)

### APIs Externas e Sistema
- **[docs/DOCUMENTACAO_VSTATS_COMPLETA.md](docs/DOCUMENTACAO_VSTATS_COMPLETA.md)** → Referência da API VStats (fornecedor)

**💡 Engenharia de Contexto:** Todos os 9 documentos técnicos são interconectados. Comece em qualquer lugar e navegue através das referências "Ver Também" para entender melhor o contexto.

---

## 📊 Status do Projeto

- ✅ **Documentação técnica** (✓ 14+ docs completamente interconectadas)
  - ✅ Backend: 6 documentações + arquitetura profissional
  - ✅ Frontend: 5 documentações + design system completo
  - ✅ Cross-references: 10/10 engenharia de contexte
- ✅ **Backend** (Funcional - FastAPI + Redis cache + Modelos Preditivos)
- ✅ **Frontend** (Funcional - React 19 + TypeScript 5 + Vite 7 + TailwindCSS)
- ✅ **Análise Preditiva** (Poisson + Dixon-Coles + Negative Binomial)
- 🔄 Deploy em produção (Próximo)

**Última atualização:** 11 de fevereiro de 2026

---

## 📝 Changelog Recente

### v1.8 (11/02/2026)
- **feat:** Análise consolidada com previsões e over/under no endpoint `/analysis`
- **feat:** Modelo de previsão com ataque/defesa relativo à média da liga
- **feat:** Ajuste de Dixon-Coles para gols (correção de placares baixos)
- **feat:** Negative Binomial para métricas com overdispersion (escanteios, cartões, etc.)
- **feat:** Intervalos de confiança via simulação Monte Carlo
- **feat:** Contexto pré-jogo (descanso, classificação, H2H) nos responses
- **feat:** Debug mode (`debug=1`) para auditoria de amostras
- **feat:** Subfiltros de mando (casa/fora) para mandante e visitante
- **feat:** Análise automática de oportunidades (Smart Search) no frontend
- **feat:** Exportação JSON completa para IA (recorte + 10 corridos + 5 casa/fora)

### v1.7 (31/12/2025)
- **fix:** Endpoint de stats corrigido - usa `/get-match-stats` com `liveData.lineUp[].stat[]`
- **fix:** Frontend timeout aumentado de 10s para 60s
- **feat:** Cache de 24h para calendário de competições
- **feat:** Fallback com IDs conhecidos caso API `/calendar` falhe
- **fix:** Uso de `/schedule` (temporada completa) para busca de partidas

### v1.6 (28/12/2025)
- **feat:** Time-Weighting no backend (Dixon-Coles decay)
  - Partidas mais recentes têm peso maior no cálculo de médias e CV
  - Decay exponencial: 30 dias = 82%, 60 dias = 68%, 90 dias = 56%
- **feat:** Dixon-Coles adjustment para gols no frontend
  - Corrige subestimação de placares baixos (0-0, 1-0, 0-1, 1-1)
  - Aumenta precisão das probabilidades Over/Under para gols

### v1.5 (28/12/2025)
- **feat:** Filtro de estatísticas na Busca Inteligente (Gols, Escanteios, Chutes, etc.)
- **feat:** Botão direito para abrir partida em nova aba (OpportunityCard usa `<Link>`)
- **perf:** React.memo em 9 componentes (Icon, Badge, RaceDot, TeamBadge, StatsCard, OverUnderCard, PredictionsCard, DisciplineCard, OpportunityCard)
- **fix:** Thresholds de Under ajustados de 70-75% para 65%

### v1.4 (28/12/2025)
- **feat:** Busca Inteligente - análise automática de oportunidades em todas as partidas
- **feat:** Logos locais de times (636+ mapeamentos em 13 ligas)
- **refactor:** Formatação de horário simplificada no Smart Search

### v1.3 (28/12/2025)
- **feat:** Filtro de período nas estatísticas (Até 50, Últimos 5, Últimos 10)
- **feat:** Melhorias no cálculo de probabilidade
- **feat:** Dados do árbitro com estatísticas da temporada

### v1.2 (28/12/2025)
- **perf:** Cache React Query habilitado para estatísticas
  - Trocar filtros (Geral → Últimos 5 → Geral) agora carrega **instantâneo do cache**
  - Cache de 5 minutos por combinação de filtros
  - Funciona para todos os subfiltros (Casa/Fora, 1T/2T)

### v1.1 (28/12/2025)
- **Performance:** Otimização de reutilização de schedule no backend
  - Schedule do torneio agora é buscado **1x** ao invés de 2x por requisição
  - Cache de 1h no schedule beneficia requisições subsequentes
  - Redução estimada de ~500ms por requisição de estatísticas
- **Frontend:** `useMemo` para memoização de cálculos em `StatsPanel`

---

**[⬆ Voltar ao topo](#-sistema-de-análise-de-estatísticas-de-futebol)**
