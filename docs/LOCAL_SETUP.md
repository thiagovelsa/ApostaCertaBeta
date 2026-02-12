# Setup Local - Guia Completo

**Versão:** 1.1
**Data:** 11 de fevereiro de 2026
**Plataformas:** Windows, macOS, Linux

Guia passo-a-passo para configurar o ambiente de desenvolvimento localmente.

---

## 1. Pré-requisitos

### 1.1 Python

**Verificar versão instalada:**

```bash
python --version
# ou
python3 --version
```

**Requerido:** Python 3.11+

**Instalar:**
- **Windows:** https://www.python.org/downloads/ (baixar 3.11+)
- **macOS:** `brew install python@3.11`
- **Linux:** `sudo apt-get install python3.11`

### 1.2 Git (Opcional)

Você pode trabalhar sem Git (por exemplo, baixando o projeto como `.zip`).
Se quiser clonar/atualizar via linha de comando:

```bash
git --version
```

**Instalar:** https://git-scm.com/downloads

### 1.3 Redis (Opcional mas Recomendado)

**Verificar instalação:**

```bash
redis-cli --version
```

**Instalar:**

- **Windows:**
  - Opção 1: Windows Subsystem for Linux (WSL) + `sudo apt-get install redis-server`
  - Opção 2: Docker (mais fácil): `docker run -d -p 6379:6379 redis:latest`

- **macOS:** `brew install redis`

- **Linux:** `sudo apt-get install redis-server`

**Verificar se está rodando:**

```bash
redis-cli ping
# Resposta esperada: PONG
```

### 1.4 Docker (Opcional)

**Verificar instalação:**

```bash
docker --version
```

**Instalar:** https://www.docker.com/products/docker-desktop

---

## 2. Setup Backend

### 2.1 Clonar Repositório

```bash
# Clonar
git clone <url-do-repositorio>

# Entrar no diretório
cd ApostaMestre
```

Alternativa sem Git:
- Baixe o repositório como `.zip` e extraia; depois entre na pasta `ApostaMestre`.

### 2.2 Criar Ambiente Virtual Python

```bash
# Ir para o backend
cd backend

# Criar venv
python -m venv .venv

# Ativar venv
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
```

**Verificar se está ativado:**
- Prompt deve mostrar `(venv)` no início
- `which python` deve retornar path do venv

### 2.3 Instalar Dependências Python

```bash
# Atualizar pip (recomendado)
pip install --upgrade pip

# Instalar requirements
pip install -r requirements.txt

# Instalar dev dependencies (testes, linting, type checking)
pip install -r requirements-dev.txt

# Verificar instalação de dependências científicas (para análise)
python -c "import math; print('✓ Math OK')"
python -c "import random; print('✓ Random OK')"
```

**Verificar instalação:**

```bash
# Verificar FastAPI
python -c "import fastapi; print(fastapi.__version__)"

# Verificar Pydantic
python -c "import pydantic; print(pydantic.__version__)"

# Verificar pytest
pytest --version
```

### 2.4 Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp ../.env.example .env

# Editar .env e preencher valores:
# - VSTATS_API_URL (já está correto)
# - REDIS_URL (deixar como localhost:6379 para dev)
```

**Editar `.env` com seu editor favorito:**

```env
VSTATS_API_URL=https://vstats-back-bbdfdf0bfd16.herokuapp.com/api
VSTATS_API_TIMEOUT=30
ENV=development
DEBUG=true
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
CACHE_VERSION=1
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
```

### 2.5 Iniciar Redis (se não estiver rodando)

```bash
# Opção 1: Docker (recomendado)
docker run -d -p 6379:6379 --name redis-dev redis:latest

# Opção 2: Redis local (se instalado)
redis-server

# Verificar
redis-cli ping  # Deve retornar PONG
```

### 2.6 Rodar Servidor Backend

```bash
# Garantir que venv está ativado
# (deve ver (venv) no prompt)

# Rodar FastAPI
uvicorn app.main:app --reload --port 8000
```

**Esperado:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
```

**Acessar:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 3. Setup Frontend (Opcional - mas Recomendado!)

**Importante:** Consulte a [documentação frontend](frontend/) para detalhes arquitetônicos antes de começar.

### 3.1 Pré-requisitos

```bash
node --version   # Requer Node 20.19+ ou 22.12+ (Vite 7)
npm --version    # npm 8+ (vem com Node)
```

Nota: o `frontend/package.json` define `engines.node >= 20.19.0`. Se a versao do Node for menor, o `npm` pode exibir avisos e o build pode falhar em alguns ambientes.

**Instalar Node:** https://nodejs.org/

### 3.2 Instalar Dependências do Frontend

O frontend já existe em `frontend/`.

```bash
cd frontend
npm install
```

Observacao: `frontend/dist/` e apenas o build local (saida do Vite). Nao use como fonte de verdade; para limpar, rode:

```bash
npm run clean
```

### 3.3 Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar .env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
VITE_ENV=development
```

### 3.4 Rodar Servidor de Desenvolvimento

```bash
npm run dev
```

**Esperado:**

```
  VITE v5.0.0  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

**Acessar:**
- Frontend: http://localhost:5173
- Backend (Swagger): http://localhost:8000/docs (deve estar rodando em paralelo)

### 3.5 Rodar Testes (Frontend)

```bash
# Testes ainda não configurados no frontend
# npm run test  # Não disponível ainda
```

**Nota:** Testes do frontend estão planejados para futura implementação. O backend possui cobertura completa de testes com pytest.

### 3.6 Build Produção

```bash
# Build otimizado
npm run build

# Output em: ./dist/
# Pronto para deploy em Vercel, Netlify, etc
```

### 3.7 Preview Build Local

```bash
npm run preview
# Simula produção em http://localhost:4173
```

### 3.8 Linting e Formatação

```bash
# ESLint (verificar erros)
npm run lint
```

---

## 4. Usando Docker (Alternativa)

No estado atual do repositório, não há `Dockerfile`/`docker-compose.yml` prontos para uso.

---

## 5. Rodar Testes

### 5.1 Unit Tests

```bash
# Todos os testes
pytest

# Específico
pytest tests/unit/test_cv_calculator.py

# Com output verboso
pytest -v -s

# Com coverage
pytest --cov=app --cov-report=html
# Abrir: htmlcov/index.html
```

### 5.2 Integration Tests

```bash
# Rodar integration tests
pytest tests/integration/

# Com servidor rodando
pytest tests/integration/test_partidas_route.py -v
```

### 5.3 Testes Específicos

```bash
# Apenas um arquivo
pytest tests/unit/test_models.py

# Apenas uma função
pytest tests/unit/test_models.py::test_time_info_valido

# Com pattern
pytest -k "cv" -v  # Testa tudo com "cv" no nome
```

---

## 6. Linting e Formatação

### 6.1 Black (Formatação)

```bash
# Checar
black --check app/

# Formatar
black app/

# Linha por linha
black --diff app/
```

### 6.2 Ruff (Linter)

```bash
# Checar
ruff check app/

# Corrigir automaticamente
ruff check --fix app/
```

### 6.3 Mypy (Type Checking)

```bash
# Checar tipos
mypy app/
```

### 6.4 Tudo Junto (Pre-commit)

```bash
# Instalar pre-commit hooks
pre-commit install

# Rodar manualmente
pre-commit run --all-files
```

---

## 7. Estrutura de Pastas

Após setup, você terá:

```
ApostaMestre/
├── venv/                          # Ambiente virtual (criar)
├── app/
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Configuração
│   ├── api/
│   ├── models/
│   ├── services/
│   └── utils/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── frontend/                       # (Se clonado)
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── docs/                          # Documentação
├── scripts/
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── openapi.yaml
```

---

## 8. Verificação Completa do Setup

### Checklist

```bash
# 1. Python
python --version            # ✓ 3.11+

# 2. Venv ativado
which python                # ✓ Aponta para venv

# 3. Dependências
pip list | grep fastapi     # ✓ FastAPI instalado

# 4. Redis
redis-cli ping              # ✓ PONG

# 5. Backend
curl http://localhost:8000/docs  # ✓ Swagger UI

# 6. API funcionando
curl "http://localhost:8000/api/competicoes"  # ✓ JSON response

# 7. Testes
pytest tests/ -q            # ✓ Testes passando

# 8. Frontend (opcional)
npm run dev                 # ✓ Servidor em 5173

# 9. Docker (opcional)
docker ps                   # ✓ Containers rodando
```

---

## 9. Troubleshooting

### Problema: "python: command not found"

**Solução:**
```bash
# Windows/macOS/Linux
which python3
# Use python3 em vez de python
cd backend
python3 -m venv .venv
python3 -m pip install -r requirements.txt
```

### Problema: "No module named 'fastapi'"

**Solução:**
```bash
# Verificar se venv está ativado (deve ver (venv) no prompt)
cd backend
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate      # Windows

# Reinstalar
pip install -r requirements.txt
```

### Problema: "Redis connection refused"

**Solução:**
```bash
# Option 1: Docker
docker run -d -p 6379:6379 redis:latest

# Option 2: Verificar se está rodando
redis-cli ping

# Option 3: Desabilitar cache no .env
CACHE_ENABLED=false
```

### Problema: "ModuleNotFoundError: No module named 'app'"

**Solução:**
```bash
# Garantir que está no diretório do backend (onde app/ está)
cd backend
ls app/  # Deve listar arquivos do app

uvicorn app.main:app --reload
```

### Problema: "Port 8000 already in use"

**Solução:**
```bash
# Matar processo usando a porta
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>

# Ou usar porta diferente:
uvicorn app.main:app --reload --port 8001
```

### Problema: "CORS error no frontend"

**Solução:**
1. Verificar `.env`:
   ```env
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

2. Verificar URL do frontend:
   ```bash
   # Frontend em http://localhost:5173?
   # Adicionar em ALLOWED_ORIGINS
   ```

3. Reiniciar backend:
   ```bash
   # Parar (Ctrl+C)
   # Rodar novamente: uvicorn app.main:app --reload
   ```

### Problema: "Tests falhando"

**Solução:**
```bash
# 1. Limpar cache pytest
pytest --cache-clear

# 2. Reinstalar requirements-dev
pip install -r requirements-dev.txt

# 3. Rodar com verbose
pytest -v -s tests/

# 4. Verificar fixtures
pytest --fixtures | grep redis
```

---

## 10. Variáveis de Ambiente por Ambiente

### Development (.env)

```env
ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Staging

```env
ENV=staging
DEBUG=false
LOG_LEVEL=INFO
CACHE_ENABLED=true
REDIS_URL=redis://staging-redis:6379/0
ALLOWED_ORIGINS=https://staging.palpitremestre.com
```

### Production

```env
ENV=production
DEBUG=false
LOG_LEVEL=WARNING
CACHE_ENABLED=true
REDIS_URL=redis://prod-redis:6379/0
ALLOWED_ORIGINS=https://palpitremestre.com
```

---

## 11. IDEs Recomendadas

### VS Code

```bash
# Extensões recomendadas:
# - Python (Microsoft)
# - Pylance
# - FastAPI
# - REST Client
# - Thunder Client
```

### PyCharm

```bash
# Professional Edition recomendada para FastAPI
# Community Edition também funciona
```

### Vim/Neovim

```bash
# Configurar LSP para Python/FastAPI
# Usar coc-python ou pyright
```

---

## 12. Comandos Rápidos

```bash
# Iniciar desenvolvimento completo
cd backend && source .venv/bin/activate && \
redis-server & \
uvicorn app.main:app --reload

# Rodar testes
pytest --cov=app --cov-report=html

# Formatar código
black app/ && ruff check --fix app/

# Checklist de qualidade
black --check app/ && ruff check app/ && pytest
```

---

## 13. Próximos Passos

1. ✅ Setup local completado
2. 📖 Ler [ARQUITETURA_BACKEND.md](ARQUITETURA_BACKEND.md)
3. 🧪 Explorar exemplos em `tests/`
4. 🚀 Começar a implementar features
5. 📝 Consultar [API_SPECIFICATION.md](API_SPECIFICATION.md) para endpoints

---

## 📞 Suporte

Se encontrar problemas:

1. Verificar [Troubleshooting](#9-troubleshooting)
2. Consultar logs (verificar output do servidor)
3. Abrir issue no GitHub
4. Contatar suporte: contato@palpitremestre.com

---

**[⬆ Voltar ao topo](#setup-local---guia-completo)**

---

## Ver Também

Para aprofundar sua compreensão do projeto após a configuração local:

- **[ARQUITETURA_BACKEND.md](ARQUITETURA_BACKEND.md)** - Entenda a estrutura de camadas que você acabou de rodar
- **[MODELOS_DE_DADOS.md](MODELOS_DE_DADOS.md)** - Schemas Pydantic usados na API
- **[API_SPECIFICATION.md](API_SPECIFICATION.md)** - Documentação dos 4 endpoints principais
- **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)** - Como rodar testes (seção 5)
- **[../tests/README.md](../tests/README.md)** - Exemplos práticos de testes
- **[../openapi.yaml](../openapi.yaml)** - Contrato OpenAPI exportado do projeto (o `/docs` do FastAPI é gerado em runtime)
- **[../AGENTS.md](../AGENTS.md)** - Diretrizes do repositório (workflow e padrões)
- **[DOCUMENTACAO_VSTATS_COMPLETA.md](DOCUMENTACAO_VSTATS_COMPLETA.md)** - API externa VStats

**Próximos Passos Recomendados:**
1. Acesse http://localhost:8000/docs para ver a documentação interativa da API
2. Estude [ARQUITETURA_BACKEND.md](ARQUITETURA_BACKEND.md) para entender as camadas
3. Implemente seu primeiro endpoint seguindo exemplos em [MODELOS_DE_DADOS.md](MODELOS_DE_DADOS.md)
4. Escreva testes seguindo [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
5. Consulte [../AGENTS.md](../AGENTS.md) para o fluxo de trabalho
