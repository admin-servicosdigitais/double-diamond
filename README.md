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
uvicorn src.main:app --host 127.0.0.1 --port 3333 --reload
```

API disponível em:
- `http://127.0.0.1:3333`
- Swagger: `http://127.0.0.1:3333/docs`

> Para rodar sem chamadas externas ao Agno, use:
```bash
AGNO_MOCK=1 uvicorn src.main:app --host 127.0.0.1 --port 3333 --reload
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
uvicorn src.main:app --host 127.0.0.1 --port 3333 --reload
```

### Rodando em Docker (SQLite com volume)

```bash
docker run --rm -p 3333:3333 \
  -e WORKFLOW_BACKEND=sqlite \
  -e WORKFLOW_SQLITE_PATH=/app/data/workflows/workflows.db \
  -v $(pwd)/data:/app/data \
  -w /app python:3.12-slim bash -lc "pip install -r requirements.txt && uvicorn src.main:app --host 0.0.0.0 --port 3333"
```

> Observação: SQLite melhora controle transacional para um deployment single-instance. Para escala horizontal, prefira Postgres.

## Exemplos de curl

### Criar workflow
```bash
curl -X POST "http://127.0.0.1:3333/workflows" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "wf-demo",
    "name": "Workflow Demo"
  }'
```

### Executar stage
```bash
curl -X POST "http://127.0.0.1:3333/workflows/wf-demo/stages/1-explorer/run" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "temas": ["corrida", "saude"]
    }
  }'
```

### Aprovar stage
```bash
curl -X POST "http://127.0.0.1:3333/workflows/wf-demo/stages/1-explorer/approve"
```

### Consultar outputs do stage
```bash
curl "http://127.0.0.1:3333/workflows/wf-demo/stages/1-explorer/outputs"
```

## Endpoints principais

### Saúde e catálogo de agentes
| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/health` | Healthcheck simples (`{"status": "ok"}`) |
| `GET` | `/agents` | Lista todos os agentes carregados de `agents/*/agent.md` |
| `GET` | `/agents/{agent_id}` | Retorna o agente por id (ex.: `1-explorer`) |

### Workflows
| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/workflows` | Cria um workflow |
| `GET` | `/workflows` | Lista todos os workflows persistidos |
| `GET` | `/workflows/{workflow_id}` | Busca um workflow específico |
| `POST` | `/workflows/{workflow_id}/stages/{stage}/run` | Executa um estágio específico |
| `POST` | `/workflows/{workflow_id}/stages/{stage}/approve` | Aprova manualmente um estágio |
| `POST` | `/workflows/{workflow_id}/stages/{stage}/next` | Executa o próximo estágio (se o atual estiver aprovado) |
| `GET` | `/workflows/{workflow_id}/stages/{stage}` | Consulta estado do estágio |
| `GET` | `/workflows/{workflow_id}/stages/{stage}/outputs` | Retorna saída compacta, lista de artefatos full do estágio e metadados |
| `GET` | `/workflows/{workflow_id}/stages/{stage}/outputs/{artifact}` | Retorna conteúdo e metadados de um artefato específico |
| `PATCH` | `/workflows/{workflow_id}/stages/{stage}/outputs/{artifact}` | Atualiza conteúdo do artefato (`{"content": "..."}`) quando o stage está em `awaiting_human_approval` |
| `GET` | `/workflows/{workflow_id}/agents/{agent_code}/latest-output` | Retorna o último output disponível por código de agente |

> Observação: os endpoints de `run`, `approve`, `next` e `PATCH .../outputs/{artifact}` podem retornar `409 Conflict` quando as pré-condições de estado do workflow não forem atendidas.

## Exemplos adicionais de curl

### Listar workflows
```bash
curl "http://127.0.0.1:3333/workflows"
```

### Executar próximo estágio
```bash
curl -X POST "http://127.0.0.1:3333/workflows/wf-demo/stages/1-explorer/next" \
  -H "Content-Type: application/json" \
  -d '{"input": {"contexto_extra": "rodar próxima etapa"}}'
```

### Buscar último output por agente
```bash
curl "http://127.0.0.1:3333/workflows/wf-demo/agents/7-validacao/latest-output"
```

### Buscar artefato específico
```bash
curl "http://127.0.0.1:3333/workflows/wf-demo/stages/1-explorer/outputs/produto--2026-04-13--explorer--radar-de-oportunidades.md"
```

### Atualizar artefato específico
```bash
curl -X PATCH "http://127.0.0.1:3333/workflows/wf-demo/stages/1-explorer/outputs/produto--2026-04-13--explorer--radar-de-oportunidades.md" \
  -H "Content-Type: application/json" \
  -d '{"content": "# Radar revisado pelo humano"}'
```

## Execução do workflow

- `run` executa um estágio e deixa em `awaiting_human_approval`.
- `approve` marca estágio como `approved`.
- `next` só avança quando o estágio atual está `approved`.

Regras especiais implementadas:
- Stage `8-prototype-visual` inclui compact e full do estágio `7-validacao` no prompt.
- Stage `9-definicao` usa como entrada principal o compact do estágio `7-validacao`.
- `output_compact.md` é interno do sistema: não deve ser listado em índices/listagens de artefatos.
- O `output_compact.md` é formado pela concatenação de até 25 linhas por arquivo em `output_full/` (limite total: `25 x quantidade de arquivos`).


## Skill de Quality Gate

A skill de Quality Gate formaliza o papel de interrogador entre stages do Double Diamond antes da aprovação humana.

- Local: `skills/quality-gate/SKILL.md`
- Status: ainda **não integrada** a LLM/Agno nesta etapa.
- Uso futuro: será utilizada em etapa posterior pelo `QualityGateService` para orientar avaliação e perguntas.


## Quality Gate Intelligence Modes

O Quality Gate suporta dois modos de execução, sem alterar os endpoints existentes:

- `AGNO_MOCK=1` -> **deterministic mode** (rule-based atual, compatível com comportamento legado).
- `AGNO_MOCK=0` (ou diferente de `1`) -> **skill + LLM mode** usando `skills/quality-gate/SKILL.md` via runtime Agno, com fallback automático para o modo determinístico em caso de erro/timeout/JSON inválido.

## Testes

### Testes automatizados
```bash
pytest -q
```

### Teste de integração completo (executável)
```bash
./scripts/test_full_workflow_integration.py
```
