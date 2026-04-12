# SaaS Product Workflow

Workflow de 9 processos para construir produtos SaaS AI-First.
Cada processo e um agente independente. Voce (humano) executa cada passo e valida antes de avancar.

## Estrutura

```
agents/                         ← Configuracao dos agentes
docs-workflow/                  ← Material de apoio (exemplos, templates, contextos)
outputs/workflow/{agent}/       ← Saidas geradas (full/ e compact/)
CLAUDE.md                       ← Orquestrador (carregado automaticamente)
```

## Numeracao oficial dos processos

A numeracao do workflow passa a ser sequencial e o nome do processo e exatamente o nome do agente:

1. explorer
2. intake
3. sourcing
4. pesquisa
5. framing
6. ideacao
7. validacao
8. prototype-visual
9. definicao

## Regras de passagem obrigatorias

- **Validacao humana obrigatoria em todos os processos** antes de avancar.
- O proximo processo so inicia apos aprovacao explicita do humano no output `compact/` do processo atual.
- `prototype-visual` (processo 8) deixa de ser opcional e entra como etapa obrigatoria de preview para stakeholders.

## Como usar

### 1. Iniciar o workflow (processo 1 — explorer)

No Claude Code, cole:

```
Atue conforme o agente definido em agents/1-explorer/agent.md

Temas: [termos ou interesses abstratos, ex: futebol, corrida, saude]
```

O agente vai gerar os artefatos em `outputs/workflow/1-explorer/full/` e o resumo compacto em `outputs/workflow/1-explorer/compact/`.

### 2. Intake (processo 2)

Use o resumo do explorer para alimentar o intake:

```
Atue conforme o agente definido em agents/2-intake/agent.md

Leia o resumo compacto em: outputs/workflow/1-explorer/compact/

Selecione a oportunidade [N] do radar
```

### 3. Sourcing (processo 3)

```
Atue conforme o agente definido em agents/3-sourcing/agent.md

Leia o resumo compacto em: outputs/workflow/2-intake/compact/
```

### 4. Processos seguintes (4 ao 9)

Repita para cada agente, sempre lendo `compact/` do anterior e validando humanamente antes de seguir.

**Importante:** o processo 9 (`definicao`) continua consumindo o `compact/` do processo 7 (`validacao`). O processo 8 (`prototype-visual`) e obrigatorio para preview e aprovacao de stakeholders, mas nao substitui a entrada tecnica do processo 9.

## Economia de tokens

- Cada sessao roda 1 agente apenas
- Entre processos, apenas o resumo compacto e passado
- Templates e contextos sao carregados sob demanda (nao ficam no prompt)
