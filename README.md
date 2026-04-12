# Agent Workflow Orchestrator (FastAPI)

Base de projeto Python com FastAPI para orquestrar workflows de agentes, com arquitetura modular, tipagem via Pydantic e persistência inicial em filesystem (JSON).

## Estrutura

```text
src/
  api/routes/
  application/services/
  domain/models/
  infrastructure/agents/
  infrastructure/persistence/
  loaders/
data/workflows/
agents/*/agent.md
```

## Pré-requisitos

- Python 3.11+

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executar a API

```bash
uvicorn src.main:app --reload
```

API disponível em:
- `http://127.0.0.1:8000`
- Docs Swagger: `http://127.0.0.1:8000/docs`

## Endpoints

- `GET /health` → retorna `{ "status": "ok" }`
- `GET /agents` → retorna todos os agentes carregados de `agents/*/agent.md`
- `GET /agents/{agent_id}` → retorna um agente específico (ex.: `1-explorer`)
- `POST /workflows` → cria workflow
- `GET /workflows/{workflow_id}` → consulta workflow
- `POST /workflows/{workflow_id}/stages/{stage}/run` → executa agente do stage
- `POST /workflows/{workflow_id}/stages/{stage}/approve` → aprova stage atual
- `POST /workflows/{workflow_id}/stages/{stage}/next` → executa próximo stage (somente se aprovado)
- `GET /workflows/{workflow_id}/stages/{stage}` → status do stage
- `GET /workflows/{workflow_id}/stages/{stage}/outputs` → outputs do stage
- `GET /workflows/{workflow_id}/agents/{agent_code}/latest-output` → último output por agent_code (mapeia automaticamente para stage)

## Persistência JSON

A classe `WorkflowRepository` salva e carrega workflows em arquivos JSON no diretório `data/workflows/`.

## Loader de agentes

`AgentMarkdownLoader` percorre `agents/`, lê frontmatter YAML dos `agent.md` e devolve objetos `AgentDefinition` com:
- `id`
- `stage`
- `name`
- `description`
- `role`
- `model`
- `summary_format`
- `instructions_md` (markdown completo após frontmatter)

## Contratos de execução de agentes

Modelos adicionados em `src/domain/models/execution.py`:
- `StageExecutionRequest`
- `StageExecutionResult`

`StageState` também foi atualizado para incluir `status`, `created_at` e `updated_at`.

## Persistência de workflow em filesystem

A persistência foi organizada para sobreviver a restart de processo, gravando estado e artefatos em disco no formato:

```text
data/workflows/{workflow_id}/
  state.json
  stages/{stage}/
    input.json
    output_compact.md
    output_full/
    metadata.json
```

Métodos principais de `WorkflowRepository`:
- `create_workflow()`
- `get_workflow()`
- `save_stage_input()`
- `save_stage_output()`
- `update_stage_status()`

## Montagem de prompt de execução

A classe `PromptAssembler` (`src/application/services/prompt_assembler.py`) monta o contexto final do agente combinando:
- `instructions_md` do agente
- compact output do estágio anterior (quando existir)
- contexto adicional do usuário

Regras aplicadas:
- estágio `N` lê o compact de `N-1`
- texto final organizado em blocos limpos (`Agent Instructions`, `Previous Stage (N-1) Compact Output`, `Additional User Context`)

Assinatura:
- `PromptAssembler.build(agent, previous_compact, context)`

## Execução de agentes com Agno

Foi adicionado o adapter `AgnoAgentRunner` em `src/infrastructure/agents/agno_agent_runner.py` com assinatura:
- `AgnoAgentRunner.run(agent_definition, prompt) -> str`

Comportamento:
- recebe o prompt final já montado
- usa o `model` definido em `agent_definition`
- retorna a resposta completa (`response.content`)

Observação: o adapter é desacoplado de FastAPI e de persistência.

## WorkflowService (execução de etapas)

`WorkflowService` agora é responsável por executar e aprovar etapas:
- `run_stage(workflow_id, stage, input)`
- `approve_stage(workflow_id, stage)`
- `get_next_stage(stage)`

Regras aplicadas:
- não executa estágio `N` sem aprovação do `N-1`
- salva input e outputs de cada estágio no filesystem
- ciclo de status: `draft` → `running` → `awaiting_human_approval` → `approved` → `completed`



## Regras de avanço

- `run` executa o agente e deixa o estágio em `awaiting_human_approval`.
- `approve` libera o avanço para o próximo estágio.
- `next` só funciona se o estágio atual estiver `approved` (ou `completed`).

## Escopo atual de execução

No fluxo atual, a execução via API está habilitada apenas para o estágio `2-intake` usando:
- `AgentMarkdownLoader`
- `PromptAssembler`
- `AgnoAgentRunner`

Ao executar `POST /workflows/{workflow_id}/stages/2-intake/run`, o sistema salva:
- compact output em `output_compact.md`
- full outputs em `output_full/prompt.md` e `output_full/response_full.md`

Para validação local sem dependência externa do Agno, use `AGNO_MOCK=1`.

