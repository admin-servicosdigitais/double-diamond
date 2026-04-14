# SaaS Product Workflow — Orquestrador

## Visao geral
Workflow de 9 processos para construcao de produtos SaaS AI-First.
Cada processo e um agente independente. O humano executa cada passo, valida e decide quando avancar.

## Numeracao oficial (sequencial)

O numero do processo e sequencial e o nome do processo e exatamente o nome do agente:

1. explorer
2. intake
3. sourcing
4. pesquisa
5. framing
6. ideacao
7. validacao
8. prototype-visual
9. definicao

> Observacao: os diretorios tecnicos ja foram atualizados para IDs `1-9` em `agents/` e `outputs/workflow/`.

## Fluxo: Divergir e Convergir

```
  EXPLORE (divergir em oportunidades)
  ┌─────────────────────────────────────────┐
  │  1 explorer                             │
  │  (temas abstratos → oportunidades)      │
  └──────────────────────┬──────────────────┘
                         ▼
  DISCOVERY (convergir no problema)
  ┌────────────────────────────────────────────────────────────┐
  │ 2 intake ──→ 3 sourcing ──→ 4 pesquisa ──→ 5 framing      │
  └──────────────────────┬─────────────────────────────────────┘
                         ▼
  DESIGN (divergir em solucoes, convergir em uma)
  ┌─────────────────────────────────────────┐
  │ 6 ideacao ────────→ 7 validacao         │
  └──────────────────────┬──────────────────┘
                         ▼
  STAKEHOLDER PREVIEW
  ┌─────────────────────────────────────────┐
  │ 8 prototype-visual (obrigatorio)        │
  └──────────────────────┬──────────────────┘
                         ▼
  DEFINE
  ┌─────────────────────────────────────────┐
  │ 9 definicao                             │
  └─────────────────────────────────────────┘
```

## Regras de governanca do fluxo

1. **Validacao humana obrigatoria** ao fim de cada processo.
2. So avancar quando houver aprovacao explicita do humano no output `compact/`.
3. O processo **8 prototype-visual e obrigatorio** (nao opcional).
4. O processo **9 definicao consome o Resumo 7 (validacao)** como entrada tecnica oficial.
5. O processo 8 gera preview para stakeholders e registro lateral, sem alterar a base tecnica do 9.

## Mapa processo ↔ agente ↔ pasta tecnica

| Processo | Nome do processo (agente) | Pasta tecnica atual |
|---|---|---|
| 1 | explorer | `agents/1-explorer/agent.md` |
| 2 | intake | `agents/2-intake/agent.md` |
| 3 | sourcing | `agents/3-sourcing/agent.md` |
| 4 | pesquisa | `agents/4-pesquisa/agent.md` |
| 5 | framing | `agents/5-framing/agent.md` |
| 6 | ideacao | `agents/6-ideacao/agent.md` |
| 7 | validacao | `agents/7-validacao/agent.md` |
| 8 | prototype-visual | `agents/8-prototype-visual/agent.md` |
| 9 | definicao | `agents/9-definicao/agent.md` |

## Como executar

### Processo 1 — explorer
```
Atue conforme o agente definido em agents/1-explorer/agent.md

Temas: [termos ou interesses abstratos, ex: futebol, corrida, saude]
```

### Processo 2 — intake
```
Atue conforme o agente definido em agents/2-intake/agent.md

Produto: [descreva o SaaS]
Demanda: [dor ou ideia]
Dominio: [fintech, edtech, etc.]
Segmento: [PME, enterprise, consumidor]
```
Se executou o processo 1:
```
Leia o resumo em outputs/workflow/1-explorer/compact/
Selecione a oportunidade [N] do radar
```

### Processo 3 — sourcing
```
Atue conforme o agente definido em agents/3-sourcing/agent.md

Leia o resumo compacto em outputs/workflow/2-intake/compact/
```

### Processos 4 a 9
```
Atue conforme o agente definido em agents/N-nome/agent.md

Leia o resumo compacto do estagio anterior em:
outputs/workflow/[estagio-anterior]/compact/

Contexto adicional: [informacoes novas]
```

No processo 8 (`prototype-visual`), use tambem os artefatos completos de `outputs/workflow/7-validacao/full/`.

## Onde ficam os outputs

Cada agente salva seus artefatos em:
- `outputs/workflow/{agent-id}/full/` — artefatos completos
- `outputs/workflow/{agent-id}/compact/` — resumo comprimido para o proximo processo

O proximo processo le apenas o `/compact/` do anterior (exceto insumos full necessarios do 8).

### Regra do output compacto (obrigatoria)
1. O `output_compact.md` deve ser a **concatenacao** de um compacto de no maximo **25 linhas por arquivo** existente em `output_full/`.
2. Limite total: `25 x quantidade_de_arquivos_em_output_full`.
   - Ex.: 1 arquivo em `output_full/` → `output_compact.md` com no maximo 25 linhas.
   - Ex.: 3 arquivos em `output_full/` → `output_compact.md` com no maximo 75 linhas.
3. `output_compact.md` e **informacao interna de sistema** e **nunca deve ser listado** em respostas, indices ou listagens de artefatos.

## Regras de sessao (economia de tokens)

1. **1 sessao = 1 agente** — contexto limpo por processo
2. **Nunca cole artefatos completos** entre processos — use o resumo em `outputs/workflow/{agent-id}/compact/`
3. **Templates de output** estao em `docs-workflow/templates/process-artifact-schemas.md`
4. **Concerns SaaS** estao em `docs-workflow/contexts/process-saas-concerns-checklist.md` — carregados sob demanda
