# Guia de Contribuição

**Versão:** 1.0
**Data:** 24 de dezembro de 2025

Bem-vindo! Obrigado por considerara contribuir para o ApostaCerta. Este guia explica como contribuir de forma consistente e profissional.

---

## 📚 Antes de Contribuir

Leia estas documentações fundamentais para entender o projeto:

1. **[ARQUITETURA_BACKEND.md](docs/ARQUITETURA_BACKEND.md)** - Entenda a estrutura em camadas
   - Arquitetura de pastas
   - Padrões de Design (Clean Architecture)
   - Convenções de código

2. **[MODELOS_DE_DADOS.md](docs/MODELOS_DE_DADOS.md)** - Schemas e validações
   - Pydantic models
   - Validadores customizados
   - Exemplos de uso

3. **[TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)** - Estratégia de testes
   - Testing pyramid (70% unit, 20% integration)
   - Fixtures e mocking
   - Padrões de teste

4. **[API_SPECIFICATION.md](docs/API_SPECIFICATION.md)** - Contrato da API
   - Endpoints documentados
   - Status codes
   - Exemplos de request/response

5. **[LOCAL_SETUP.md](docs/LOCAL_SETUP.md)** - Configuração local
   - Pré-requisitos
   - Setup passo a passo
   - Troubleshooting

---

## 🚀 Setup Local

### Pré-requisitos

- Python 3.11+
- Node 18+ (para frontend)
- Docker (recomendado para Redis)
- Git

### Passos Rápidos

```bash
# 1. Clone o repositório
git clone https://github.com/thiagovelsa/ApostaCertaBeta.git
cd ApostaCertaBeta

# 2. Siga o guia completo em LOCAL_SETUP.md
cat docs/LOCAL_SETUP.md

# 3. Configure ambiente
cp .env.example .env
# Preencha VSTATS_CLIENT_ID e VSTATS_CLIENT_SECRET

# 4. Backend setup
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements-dev.txt

# 5. Inicie Redis (Docker)
docker run -d -p 6379:6379 redis:latest

# 6. Rode servidor
uvicorn app.main:app --reload --port 8000

# 7. Acesse
# Swagger UI: http://localhost:8000/docs
# API: http://localhost:8000/api/...
```

Para detalhes completos, veja **[LOCAL_SETUP.md](docs/LOCAL_SETUP.md)**.

---

## 🔄 Fluxo de Trabalho

### 1. Crie uma Branch

```bash
# Use nomes descritivos
git checkout -b feature/nova-feature
# ou
git checkout -b fix/nome-do-bug
# ou
git checkout -b refactor/melhorias
```

### 2. Implemente Seguindo os Padrões

Consulte **[ARQUITETURA_BACKEND.md](docs/ARQUITETURA_BACKEND.md)** para:

- Estrutura de pastas esperada
- Padrão de nomeação (snake_case, PascalCase, UPPER_SNAKE_CASE)
- Organização de imports
- Convenções de docstring (Google style)
- Exemplos de cada camada (API, Models, Services, Repositories, Utils)

**Exemplo: Novo Endpoint**

1. Criar rota em `app/api/routes/novo_endpoint.py`
2. Definir models em `app/models/novo.py` (veja **[MODELOS_DE_DADOS.md](docs/MODELOS_DE_DADOS.md)**)
3. Implementar lógica em `app/services/novo_service.py`
4. Escrever testes em `tests/unit/test_novo_service.py`
5. Atualizar **[API_SPECIFICATION.md](docs/API_SPECIFICATION.md)**

### 3. Escreva Testes

Todos os novos códigos precisam de testes. Consulte **[TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)**:

```bash
# Rode testes localmente
pytest

# Com coverage (mínimo 80%)
pytest --cov=app --cov-report=html

# Teste específico
pytest tests/unit/test_novo_service.py::TestNovaFuncao::test_caso_sucesso -v
```

**Coverage target:** 80% mínimo para todas as alterações.

### 4. Formatação e Linting

```bash
# Formatação Black
black app/ tests/

# Linting Ruff
ruff check app/ --fix

# Type checking
mypy app/

# Todos junto
black --check app/ && ruff check app/ && mypy app/ && pytest --cov=app
```

### 5. Commit com Mensagens Claras

```bash
# Mensagens descritivas
git commit -m "feat: adicionar novo endpoint de análise

- Novo endpoint GET /api/analise
- Implementar AnalisaService
- Adicionar testes unitários (100% coverage)
- Atualizar API_SPECIFICATION.md"
```

**Padrões de commit (Conventional Commits):**
- `feat:` - Nova feature
- `fix:` - Bug fix
- `refactor:` - Refatoração sem mudança de comportamento
- `docs:` - Mudanças em documentação
- `test:` - Novos testes ou alterações em testes
- `chore:` - Outras mudanças (deps, config, etc)

### 6. Push e Pull Request

```bash
# Push para sua branch
git push origin feature/nova-feature

# Abra PR no GitHub com template:
# - Descrição clara do que mudou
# - Link para issues relacionadas
# - Checklist de testes
# - Screenshots (se UI)
```

**Checklist de PR:**
- [ ] Testes escritos e passando (`pytest`)
- [ ] Coverage >= 80% (`pytest --cov=app`)
- [ ] Código formatado (`black app/`)
- [ ] Linting passou (`ruff check app/`)
- [ ] Documentação atualizada (se necessário)
- [ ] Sem warnings ou erros

---

## 📝 Padrões de Código

### Python

**Estilo:**
- Black (formatação automática)
- Ruff (linting)
- Google-style docstrings
- Type hints (PEP 484)

**Exemplo:**

```python
"""
arquivo: app/services/novo_service.py
"""
from typing import List, Optional
from datetime import date
from app.models.novo import NovoModel
from app.repositories.novo_repository import NovoRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)

class NovoService:
    """Serviço de nova funcionalidade.

    Implementa lógica de negócio para a nova feature.
    Comunica com repositories para acessar dados externos.
    """

    def __init__(self, repository: NovoRepository):
        """Inicializa service com dependency injection.

        Args:
            repository: Acesso aos dados externos
        """
        self.repository = repository

    async def processar_dados(self, ids: List[str]) -> Optional[dict]:
        """Processa dados e retorna resultado.

        Args:
            ids: Lista de IDs para processar

        Returns:
            Dicionário com resultado ou None se falhar

        Raises:
            ValueError: Se ids vazio
            Exception: Se repositório falha

        Example:
            >>> result = await service.processar_dados(["id1", "id2"])
            >>> print(result["status"])
            "sucesso"
        """
        if not ids:
            raise ValueError("IDs não podem estar vazios")

        logger.info(f"Processando {len(ids)} IDs")

        try:
            dados = await self.repository.fetch_dados(ids)
            return {"status": "sucesso", "dados": dados}
        except Exception as e:
            logger.error(f"Erro ao processar: {str(e)}", exc_info=True)
            raise
```

**Imports:**
```python
# 1. Standard library
import os
import asyncio
from typing import List, Optional, Dict

# 2. Third-party
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator

# 3. Local
from app.models.novo import NovoModel
from app.services.novo_service import NovoService
from app.config import settings
```

Veja **[ARQUITETURA_BACKEND.md seção 6](docs/ARQUITETURA_BACKEND.md#6-convenções-de-código)** para mais detalhes.

### Testes

**Estrutura:**
```python
# tests/unit/test_novo_service.py
import pytest
from app.services.novo_service import NovoService
from app.models.novo import NovoModel

class TestNovoService:
    """Testes do NovoService."""

    @pytest.fixture
    def service(self, mocker):
        """Cria service com mock."""
        mock_repo = mocker.MagicMock()
        return NovoService(mock_repo)

    def test_processar_dados_sucesso(self, service):
        """Testa processamento bem-sucedido."""
        # ARRANGE
        ids = ["id1", "id2"]

        # ACT
        resultado = service.processar_dados(ids)

        # ASSERT
        assert resultado["status"] == "sucesso"
        assert len(resultado["dados"]) == 2

    def test_processar_dados_vazio(self, service):
        """Testa com IDs vazios."""
        with pytest.raises(ValueError):
            service.processar_dados([])
```

Veja **[TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)** para padrões completos.

### Documentação

**Se alterar API:**
1. Atualize **[API_SPECIFICATION.md](docs/API_SPECIFICATION.md)**
2. Atualize **[openapi.yaml](openapi.yaml)** (gerado automaticamente)
3. Atualize **[MODELOS_DE_DADOS.md](docs/MODELOS_DE_DADOS.md)** se novos schemas

**Se alterar arquitetura:**
1. Atualize **[ARQUITETURA_BACKEND.md](docs/ARQUITETURA_BACKEND.md)**

**Se alterar testes:**
1. Atualize **[TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)** ou **[tests/README.md](tests/README.md)**

---

## 🧪 Checklist Final

Antes de enviar PR, verifique:

- [ ] Branch criada com nome descritivo
- [ ] Código segue padrões (Black + Ruff)
- [ ] Todos os testes passam: `pytest`
- [ ] Coverage >= 80%: `pytest --cov=app`
- [ ] Sem warnings ou erros no log
- [ ] Docstrings em todas as funções/classes públicas
- [ ] Commit messages são claras e descritivas
- [ ] Documentação atualizada (se necessário)
- [ ] Sem comentários de debug deixados no código
- [ ] Nenhuma senha/secret commitado

---

## 📖 Documentação Relacionada

- **[README.md](README.md)** - Visão geral do projeto
- **[ARQUITETURA_BACKEND.md](docs/ARQUITETURA_BACKEND.md)** - Estrutura backend
- **[MODELOS_DE_DADOS.md](docs/MODELOS_DE_DADOS.md)** - Schemas Pydantic
- **[API_SPECIFICATION.md](docs/API_SPECIFICATION.md)** - Endpoints da API
- **[LOCAL_SETUP.md](docs/LOCAL_SETUP.md)** - Setup do ambiente
- **[TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)** - Estratégia de testes
- **[tests/README.md](tests/README.md)** - Guia prático de testes

---

## 💬 Dúvidas ou Sugestões?

- 📖 Consulte as documentações acima
- 🐛 Abra uma issue no GitHub
- 💌 Entre em contato: suporte@apostacerta.com

---

## 📋 Ver Também

Para contextualizar melhor, leia também:

- **[PROJETO_SISTEMA_ANALISE.md](PROJETO_SISTEMA_ANALISE.md)** - Especificação do sistema
- **[DOCUMENTACAO_VSTATS_COMPLETA.md](DOCUMENTACAO_VSTATS_COMPLETA.md)** - API VStats externa
- **[CLAUDE.md](CLAUDE.md)** - Instruções para Claude Code

---

**[⬆ Voltar ao topo](#guia-de-contribuição)**
