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
- ✅ **Filtros Flexíveis** - Análise por período (temporada completa, últimas 5 ou 10 partidas)
- ✅ **Métricas de Estabilidade** - Coeficiente de Variação (CV) para avaliar consistência
- ✅ **API RESTful Completa** - Endpoints bem documentados com Swagger/OpenAPI
- ✅ **Caching Inteligente** - Redis para performance (TTLs otimizados)
- ✅ **CORS Configurado** - Pronto para frontend em produção
- ✅ **Testes Automatizados** - Unit tests + integration tests com pytest

---

## 🚀 Quick Start

### Pré-requisitos

- **Python 3.11+**
- **Node.js 18+** (para frontend)
- **Docker** (opcional, recomendado)
- **Redis** (opcional se usar cache)

### 1. Clonar Repositório

```bash
git clone https://github.com/thiagovelsa/ApostaCertaBeta.git
cd ApostaCertaBeta
```

### 2. Configurar Backend

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate      # Windows

# Instalar dependências
pip install -r requirements.txt

# Copiar arquivo de configuração
cp .env.example .env

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
```

Frontend em: **http://localhost:5173** ou **http://localhost:3000**

### 4. Com Docker (Recomendado)

```bash
# Build e run
docker-compose up -d

# Verificar logs
docker-compose logs -f backend
```

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
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Guia de contribuição (workflow, padrões) |

### Frontend (React + TypeScript)
| Documento | Descrição |
|-----------|-----------|
| **[docs/frontend/DESIGN_SYSTEM.md](docs/frontend/DESIGN_SYSTEM.md)** | Design tokens, cores, tipografia, componentes visuais |
| **[docs/frontend/COMPONENTES_REACT.md](docs/frontend/COMPONENTES_REACT.md)** | Catálogo de 19 componentes (Atomic Design) |
| **[docs/frontend/INTEGRACAO_API.md](docs/frontend/INTEGRACAO_API.md)** | Services, React Query hooks, type mappings |
| **[docs/frontend/ARQUITETURA_FRONTEND.md](docs/frontend/ARQUITETURA_FRONTEND.md)** | Folder structure, Zustand stores, React Router |
| **[docs/frontend/RESPONSIVIDADE_E_ACESSIBILIDADE.md](docs/frontend/RESPONSIVIDADE_E_ACESSIBILIDADE.md)** | Mobile-first design, WCAG AA, PWA |

### Sistema e APIs Externas
| Documento | Descrição |
|-----------|-----------|
| **[DOCUMENTACAO_VSTATS_COMPLETA.md](DOCUMENTACAO_VSTATS_COMPLETA.md)** | Referência completa da API VStats (fornecedor) |
| **[PROJETO_SISTEMA_ANALISE.md](PROJETO_SISTEMA_ANALISE.md)** | Requisitos, design, fluxos, cálculos |

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
| **Frontend** | React 18 + TypeScript 5 + Vite 5 + TailwindCSS + Zustand + React Query |
| **Backend** | Python 3.11+ + FastAPI + Pydantic |
| **Cache** | Redis |
| **APIs Externas** | VStats + TheSportsDB |
| **Tests** | Pytest (backend) + Vitest/React Testing Library (frontend) |
| **Container** | Docker + Docker Compose |

---

## 📊 Endpoints da API

### Partidas
- `GET /api/partidas?data=2025-12-27` - Lista partidas por data

### Estatísticas
- `GET /api/partida/{matchId}/stats?filtro=5` - Estatísticas detalhadas (geral/5/10)

### Competições
- `GET /api/competicoes` - Lista todas as competições

### Times
- `GET /api/time/{teamId}/escudo` - Escudo/logo do time

**Documentação Interativa:** http://localhost:8000/docs (Swagger UI)

---

## ⚙️ Configuração

Copie `.env.example` para `.env` e preencha:

```bash
# VStats API
VSTATS_API_URL=https://vstats-back-bbdfdf0bfd16.herokuapp.com/api
VSTATS_CLIENT_ID=seu_client_id
VSTATS_CLIENT_SECRET=seu_client_secret

# Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SCHEDULE=3600        # 1h
CACHE_TTL_SEASONSTATS=21600    # 6h
CACHE_TTL_BADGES=604800        # 7 dias

# Application
LOG_LEVEL=INFO
ENV=development
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
FRONTEND_URL=http://localhost:3000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

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

```bash
# Build
docker build -t palpitremestre-backend .

# Run
docker run -p 8000:8000 \
  -e VSTATS_API_URL=... \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  palpitremestre-backend

# Compose (completo)
docker-compose up -d
docker-compose logs -f backend
docker-compose down
```

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

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes detalhadas.

---

## 📞 Suporte

- **Issues:** [GitHub Issues](https://github.com/thiagovelsa/ApostaCertaBeta/issues)
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

### Setup e Contribuição
- **[LOCAL_SETUP.md](docs/LOCAL_SETUP.md)** → Configuração ambiente completa + troubleshooting
  - Referencia: [ARQUITETURA_BACKEND.md](docs/ARQUITETURA_BACKEND.md), [TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)

- **[CONTRIBUTING.md](CONTRIBUTING.md)** → Guia de contribuição (workflow, padrões de código)
  - Referencia: Todos os docs acima

### APIs Externas e Sistema
- **[DOCUMENTACAO_VSTATS_COMPLETA.md](DOCUMENTACAO_VSTATS_COMPLETA.md)** → Referência da API VStats (fornecedor)
- **[PROJETO_SISTEMA_ANALISE.md](PROJETO_SISTEMA_ANALISE.md)** → Requisitos e design do sistema

**💡 Engenharia de Contexto:** Todos os 9 documentos técnicos são interconectados. Comece em qualquer lugar e navegue através das referências "Ver Também" para entender melhor o contexto.

---

## 📊 Status do Projeto

- ✅ **Documentação técnica** (✓ 14+ docs completamente interconectadas)
  - ✅ Backend: 6 documentações + arquitetura profissional
  - ✅ Frontend: 5 documentações + design system completo
  - ✅ Cross-references: 10/10 engenharia de contexto
- 🔄 Backend (Em desenvolvimento)
- 🔄 Frontend (Pronto para implementação - specs completas)
- 🔄 Deploy em produção (Próximo)

**Última atualização:** 24 de dezembro de 2025

---

**[⬆ Voltar ao topo](#-sistema-de-análise-de-estatísticas-de-futebol)**
