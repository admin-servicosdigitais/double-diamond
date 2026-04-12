# Code Review — Migração do workflow de agentes (Claude Code → Agno + API)

## Escopo analisado

- Camadas `api`, `application`, `domain`, `infrastructure`.
- Orquestração em `WorkflowService`.
- Execução via `AgnoAgentRunner` + `PromptAssembler`.
- Casos especiais de estágios/agents (1, 4, 8, 9).
- Persistência em filesystem.
- Contratos da API FastAPI.

## Problemas priorizados

### 🔴 Críticos

1. **Estados do workflow são strings livres, sem enum nem validação de transição.**
   - Hoje `status` é `str` e `update_stage_status` aceita qualquer valor.
   - Isso permite estados inválidos e transições incoerentes (ex.: `draft -> completed` sem execução).
   - Impacto: inconsistência de estado, difícil auditoria e maior risco de bugs em integrações futuras.

2. **Race conditions e escrita não-atômica no filesystem.**
   - `WorkflowRepository` lê/escreve `state.json` sem lock e sem rename atômico.
   - Chamadas concorrentes (API em múltiplos workers/threads) podem sobrescrever estado e perder metadata.
   - Impacto: corrupção lógica do workflow e resultados não determinísticos.

3. **`run_stage` marca estágio anterior como `completed` antes de garantir execução bem-sucedida do próximo.**
   - Se o runner falhar depois dessa atualização, o estágio anterior fica finalizado e o atual pode ficar em `running`, quebrando o fluxo.
   - Impacto: workflow pode travar em estado intermediário sem rollback.

### 🟠 Médios

4. **Acoplamento de regras de negócio especiais direto no `WorkflowService` por `if stage == ...`.**
   - Regras de 8 e 9 estão hardcoded (`include_full_previous_stage`, override de entrada para 9).
   - Impacto: baixa escalabilidade para novos casos especiais (10, 11, branches, loops).

5. **`PromptAssembler` mistura instruções do agente com contexto em um único blob sem delimitadores fortes por tipo.**
   - Contextos `dict` viram bullet list simples (`- key: value`), sem serialização robusta.
   - Impacto: perda de estrutura, ambiguidades de prompt e risco de colisão semântica.

6. **`ToolRegistry` usa fallback silencioso para falhas de tool externa.**
   - `websearch` retorna `None` se imports falham; caller não recebe erro explícito.
   - Impacto: agente roda “degradado” sem transparência operacional.

7. **Contratos HTTP parcialmente tipados (`dict[str, Any]`) e respostas de outputs sem response model.**
   - Endpoints como `/outputs` retornam dicionário dinâmico.
   - Impacto: menor discoverability no OpenAPI e mais fragilidade para clientes.

8. **`WorkflowService` concentra responsabilidades demais (state machine, carregamento de input, resolução de agente, leitura de artefatos).**
   - Coesão funcional alta, mas coesão de responsabilidades baixa.
   - Impacto: manutenção e testes unitários mais difíceis com crescimento do domínio.

### 🟡 Baixos

9. **Inconsistências de idioma/nomenclatura e mensagens de erro.**
   - Mistura PT/EN em campos, mensagens e nomes (`next_stage_available`, mensagens em português).
   - Impacto: menor padronização de DX para consumidores externos.

10. **`get_next_stage`/`_get_previous_stage` recalculam ordenação lendo markdown em toda chamada.**
    - Repetição de trabalho e dependência de I/O em runtime quente.
    - Impacto: custo desnecessário e potencial comportamento inconsistente se arquivos mudarem durante execução.

11. **`StageExecutionRequest` existe no domínio mas não participa do fluxo real dos endpoints.**
    - Impacto: modelo órfão e ruído arquitetural.

## Sugestões objetivas de melhoria

### 1) Fortalecer a máquina de estados

- Introduzir enum para `StageStatus` e uma tabela explícita de transições válidas.
- Validar transição no repositório (ou em um `WorkflowStateMachine` dedicado).
- Tornar transições idempotentes (aprovar estágio já aprovado retorna 200/sem efeito).

Exemplo:

```python
class StageStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    AWAITING_HUMAN_APPROVAL = "awaiting_human_approval"
    APPROVED = "approved"
    COMPLETED = "completed"

ALLOWED = {
    StageStatus.DRAFT: {StageStatus.RUNNING},
    StageStatus.RUNNING: {StageStatus.AWAITING_HUMAN_APPROVAL},
    StageStatus.AWAITING_HUMAN_APPROVAL: {StageStatus.APPROVED},
    StageStatus.APPROVED: {StageStatus.COMPLETED},
}
```

### 2) Tornar persistência segura para concorrência

- Aplicar lock por workflow (`filelock`/`fcntl`) durante read-modify-write.
- Gravar em arquivo temporário + `os.replace` para atomicidade.
- Versionar `state.json` (campo `version`) para detecção de write skew.

### 3) Evitar estados parciais em falhas

- Em `run_stage`, só atualizar `previous_stage -> completed` após a execução e persistência do estágio atual.
- Em erro, marcar estágio atual como `failed` com `error_code/error_message` em metadata.

### 4) Externalizar regras especiais por política de estágio

- Criar `StagePolicyResolver` (por `stage_id`) com contrato:
  - `input_source_stage`
  - `include_full_previous_stage`
  - validações adicionais (ex.: precondição No-Go no estágio 8)
- Remove ifs hardcoded do service e facilita evolução.

### 5) Melhorar montagem de prompt

- Serializar contexto estruturado como JSON/YAML delimitado em bloco:
  - `# Runtime Context (json)` + fenced block.
- Separar claramente: `agent_instructions`, `workflow_memory`, `user_context`, `artifacts`.

### 6) Observabilidade e operação

- Registrar logs estruturados com `workflow_id`, `stage`, `run_id`, `execution_mode`, tools ativas.
- Expor motivo de degradação de tools no metadata/output quando fallback acontecer.

### 7) API mais consistente e REST-friendly

- Definir `response_model` para `/outputs` e `/latest-output`.
- Considerar nomenclatura de ação via recursos de execução:
  - `POST /workflows/{id}/stages/{stage}/executions`
  - `POST /workflows/{id}/stages/{stage}/approvals`
- Padronizar envelope de erro (code, message, details).

### 8) Preparação para banco de dados

- Introduzir interface de repositório de domínio (protocolo) e implementação FS como adapter.
- Modelar entidades separadas:
  - workflow
  - stage_execution
  - artifacts
- Facilita migração para Postgres sem alterar camada de aplicação.

## Pontos positivos observados

- Boa separação inicial de camadas e uso de Pydantic.
- Reuso consistente dos `agent.md` como fonte de verdade da configuração dos agentes.
- Regras especiais críticas (8 e 9) já cobertas por teste de integração.
- Fluxo de aprovação humana está implementado e bloqueia avanço sem aprovação.

## Edge cases/pontos de falha a acompanhar

- Reexecução de estágio já `completed` (comportamento hoje não explicitado).
- Falha entre `save_stage_output` e `update_stage_status` gera estado quebrado.
- Prompt potencialmente muito grande com full artifacts do estágio 7 no estágio 8 (token explosion).
- Dependência de variáveis/SDK (`agno`) sem healthcheck dedicado de runtime.
