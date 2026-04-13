# Agent Workflow Orchestrator (FastAPI)

Orquestrador de workflow de agentes com FastAPI, persistência em filesystem e execução via runtime Agno.

## Como subir o projeto

### 1) Pré-requisitos
- Python 3.11+

### 2) Instalação
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Variáveis de ambiente

Copie `.env-example` para `.env` e ajuste conforme o backend escolhido:

```bash
cp .env-example .env
```


### 3) Subir a API
```bash
uvicorn src.main:app --reload
```

API disponível em:
- `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

> Para rodar sem chamadas externas ao Agno, use:
```bash
AGNO_MOCK=1 uvicorn src.main:app --reload
```

## Estrutura de pastas

```text
agents/
  1-explorer/agent.md
  ...
  9-definicao/agent.md

src/
  api/routes/
  application/services/
  domain/models/
  infrastructure/agents/
  infrastructure/persistence/
  loaders/

scripts/
  test_full_workflow_integration.py

tests/
  test_workflow_approval.py
  test_workflow_integration.py

data/workflows/
  {workflow_id}/
    state.json
    stages/{stage}/
      input.json
      output_compact.md
      output_full/
      metadata.json
```


## Backend SQLite (opcional)

### Rodando com Docker Compose

```bash
cp .env-example .env
docker compose up --build api
```

Para executar testes dentro do container (sem depender do ambiente local):

```bash
docker compose run --rm test
```


Para reduzir problemas de concorrência e facilitar evolução para banco, o serviço agora suporta backend SQLite via variável de ambiente.

```bash
WORKFLOW_BACKEND=sqlite \
WORKFLOW_SQLITE_PATH=data/workflows/workflows.db \
uvicorn src.main:app --reload
```

### Rodando em Docker (SQLite com volume)

```bash
docker run --rm -p 8000:8000 \
  -e WORKFLOW_BACKEND=sqlite \
  -e WORKFLOW_SQLITE_PATH=/app/data/workflows/workflows.db \
  -v $(pwd)/data:/app/data \
  -w /app python:3.12-slim bash -lc "pip install -r requirements.txt && uvicorn src.main:app --host 0.0.0.0 --port 8000"
```

> Observação: SQLite melhora controle transacional para um deployment single-instance. Para escala horizontal, prefira Postgres.

## Exemplos de curl

### Criar workflow
```bash
curl -X POST "http://127.0.0.1:8000/workflows" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "wf-demo",
    "name": "Workflow Demo"
  }'
```

### Executar stage
```bash
curl -X POST "http://127.0.0.1:8000/workflows/wf-demo/stages/1-explorer/run" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "temas": ["corrida", "saude"]
    }
  }'
```

### Aprovar stage
```bash
curl -X POST "http://127.0.0.1:8000/workflows/wf-demo/stages/1-explorer/approve"
```

### Consultar outputs do stage
```bash
curl "http://127.0.0.1:8000/workflows/wf-demo/stages/1-explorer/outputs"
```

## Endpoints principais
- `GET /health`
- `GET /agents`
- `GET /agents/{agent_id}`
- `POST /workflows`
- `GET /workflows`
- `GET /workflows/{workflow_id}`
- `POST /workflows/{workflow_id}/stages/{stage}/run`
- `POST /workflows/{workflow_id}/stages/{stage}/approve`
- `POST /workflows/{workflow_id}/stages/{stage}/next`
- `GET /workflows/{workflow_id}/stages/{stage}`
- `GET /workflows/{workflow_id}/stages/{stage}/outputs`
- `GET /workflows/{workflow_id}/agents/{agent_code}/latest-output`

## Execução do workflow

- `run` executa um estágio e deixa em `awaiting_human_approval`.
- `approve` marca estágio como `approved`.
- `next` só avança quando o estágio atual está `approved`.

Regras especiais implementadas:
- Stage `8-prototype-visual` inclui compact e full do estágio `7-validacao` no prompt.
- Stage `9-definicao` usa como entrada principal o compact do estágio `7-validacao`.

## Testes

### Testes automatizados
```bash
pytest -q
```

### Teste de integração completo (executável)
```bash
./scripts/test_full_workflow_integration.py
```
