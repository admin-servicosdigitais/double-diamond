# SaaS Product Workflow

Workflow de 13 estagios para construir produtos SaaS AI-First usando Claude Code.
Cada estagio e um agente independente. Voce (humano) executa cada passo e decide quando avancar.

## Estrutura

```
agents/                         ← Configuracao dos 13 agentes
docs-workflow/                  ← Material de apoio (exemplos, templates, contextos)
outputs/workflow/{agent}/       ← Saidas geradas (full/ e compact/)
CLAUDE.md                       ← Orquestrador (carregado automaticamente)
```

## Como usar

### 1. Iniciar o workflow (estagio 0.0 — Explorer)

O workflow comeca com o agente Explorer, que parte de temas abstratos e gera um radar de oportunidades. No Claude Code, cole:

```
Atue conforme o agente definido em agents/0.0-explorer/agent.md

Temas: [termos ou interesses abstratos, ex: futebol, corrida, saude]
```

O agente vai gerar os artefatos em `outputs/workflow/0.0-explorer/full/` e o resumo compacto em `outputs/workflow/0.0-explorer/compact/`.

### 2. Intake (estagio 0.1)

Use o resumo do Explorer para alimentar o Intake:

```
Atue conforme o agente definido em agents/0.1-intake/agent.md

Leia o resumo compacto em: outputs/workflow/0.0-explorer/compact/

Selecione a oportunidade [N] do radar
```

### 3. Avancar para os estagios seguintes (0.1.5+)

```
Atue conforme o agente definido em agents/0.1.5-sourcing/agent.md

Leia o resumo compacto em: outputs/workflow/0.1-intake/compact/

```

Repita para cada estagio. O agente sempre le o `/compact/` do anterior como input.

Exceção: O item 0.5.5 é um html que não é validado pelo processo 0.6, pois ele tem como output HTML de prototipação visual e navegável. Sendo assim o 0.6 usará o compactado do 0.5.

## Economia de tokens

- Cada sessao roda 1 agente apenas
- Entre estagios, apenas o resumo compacto é passado
- Templates e contextos são carregados sob demanda (não ficam no prompt)
