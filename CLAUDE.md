# SaaS Product Workflow — Orquestrador

## Visao geral
Workflow de 12 estagios para construcao de produtos SaaS AI-First.
Cada estagio e um agente independente. O humano executa cada passo e decide quando avancar.

## Fluxo: Divergir e Convergir

```
  EXPLORE (divergir em oportunidades)
  ┌─────────────────────────────────────────┐
  │ 0.0 Explorer                            │
  │  (temas abstratos → oportunidades)      │
  └──────────────────────┬──────────────────┘
                         ▼
  DISCOVERY (convergir no problema)
  ┌────────────────────────────────────────────────────────────┐
  │ 0.1 Intake ──→ 0.1.5 Sourcing ──→ 0.2 Pesquisa ──→ 0.3 Framing │
  │  (demanda)     (fontes web)       (evidencias)     (problema)  │
  └──────────────────────┬─────────────────────────────────────┘
                         ▼
  DESIGN (divergir em solucoes, convergir em uma)
  ┌─────────────────────────────────────────┐
  │ 0.4 Ideacao ────────→ 0.5 Validacao     │
  │  DIVERGE: 3-5          CONVERGE:         │
  │  alternativas          Go / No-Go /      │
  │  genuinamente          Pivotar            │
  │  distintas                                │
  └──────────────────────┬──────────────────┘
                         ▼ [somente se Go]
  BUILD (divergir em artefatos paralelos, convergir em specs)
  ┌─────────────────────────────────────────┐
  │ 0.6 Definicao ──────→ 0.7 Construcao   │
  │  DIVERGE: 4 artefatos   CONVERGE:       │
  │  PRD | Backlog |         specs tecnicas  │
  │  Arquitetura |           unificadas      │
  │  Release plan                            │
  └──────────────────────┬──────────────────┘
                         ▼
  SHIP (convergir no lancamento)
  ┌─────────────────────────────────────────┐
  │ 0.8 Homologacao ──→ 0.9 Go-live        │
  │  (UAT + rollout)     (deploy + comms)   │
  └──────────────────────┬──────────────────┘
                         ▼
  LEARN (decidir proximo ciclo)
  ┌─────────────────────────────────────────┐
  │ 0.10 Aprendizado                        │
  │  Iterar → volta para 0.4               │
  │  Pivotar → volta para 0.0 ou 0.1       │
  │  Escalar → volta para 0.6 (fase 2)     │
  │  Encerrar → fim                         │
  └─────────────────────────────────────────┘
```

## Estagios

| # | Agente | Modelo | Momento | Input | Output |
|---|--------|--------|---------|-------|--------|
| 0.0 | Explorer | **sonnet** | **Divergir** | Temas abstratos | Radar de oportunidades |
| 0.1 | Intake | **haiku** | Convergir | Resumo 0.0 ou demanda bruta | Ficha + Hipotese |
| 0.1.5 | Sourcing | **sonnet** | Convergir | Resumo 0.1 | Matriz de fontes + Mapa de acesso a usuarios |
| 0.2 | Pesquisa | **sonnet** | Convergir | Resumo 0.1 + Resumo 0.1.5 | Evidencias + Mapa dores |
| 0.3 | Framing | **sonnet** | Convergir | Resumo 0.2 | Problem statement + Metricas |
| 0.4 | Ideacao | **sonnet** | **Divergir** | Resumo 0.3 | 3-5 alternativas + Conceito |
| 0.5 | Validacao | **sonnet** | **Convergir** | Resumo 0.4 | Prototipo + Go/No-Go |
| 0.6 | Definicao | **sonnet** | **Divergir** | Resumo 0.5 | PRD + Backlog + Arq + Release |
| 0.7 | Construcao | **sonnet** | **Convergir** | Resumo 0.6 | Specs + Testes + Doc |
| 0.8 | Homologacao | **haiku** | Convergir | Resumo 0.7 | Release notes + Rollout + UAT |
| 0.9 | Go-live | **haiku** | Convergir | Resumo 0.8 | Checklist + Playbook + Comms |
| 0.10 | Aprendizado | **sonnet** | Decidir | Resumo 0.9 + KPIs | Relatorio + Decisao + Backlog |

## Como executar um estagio

### Passo 0 — Exploracao criativa (0.0, opcional)
```
Atue conforme o agente definido em agents/0.0-explorer/agent.md

Temas: [termos ou interesses abstratos, ex: futebol, corrida, saude]
```

### Passo 1 — Intake (0.1)
```
Atue conforme o agente definido em agents/0.1-intake/agent.md

Produto: [descreva o SaaS]
Demanda: [dor ou ideia]
Dominio: [fintech, edtech, etc.]
Segmento: [PME, enterprise, consumidor]
```
Se executou o 0.0, use o resumo compacto como input:
```
Leia o resumo em outputs/workflow/0.0-explorer/compact/
Selecione a oportunidade [N] do radar
```

### Passo 1.5 — Sourcing (0.1.5) — obrigatorio
```
Atue conforme o agente definido em agents/0.1.5-sourcing/agent.md

Leia o resumo compacto em outputs/workflow/0.1-intake/compact/
```
Este estagio faz pesquisa web profunda e entrega ao 0.2 a matriz de fontes quantitativas e o mapa de canais de acesso a usuarios — elimina a necessidade de fornecer dados internos manualmente.

### Passo 2 — Estagios seguintes (0.2+)
```
Atue conforme o agente definido em agents/0.X-nome/agent.md

Leia o resumo compacto do estagio anterior em:
outputs/workflow/[estagio-anterior]/compact/

Contexto adicional: [informacoes novas]
```

### Passo 3 — Consultar exemplo (opcional)
```
Leia docs-workflow/examples/fintech/0.4-ideacao.md como referencia
```

## Onde ficam os outputs

Cada agente salva seus artefatos em:
- `outputs/workflow/{agent-id}/full/` — artefatos completos
- `outputs/workflow/{agent-id}/compact/` — resumo comprimido para o proximo agente

O proximo agente le apenas o `/compact/` do anterior. O `/full/` e para consulta humana.

## Regras de sessao (economia de tokens)

1. **1 sessao = 1 agente** — contexto limpo por estagio
2. **Nunca cole artefatos completos** entre estagios — use o resumo em `outputs/workflow/{agent-id}/compact/`
3. **Templates de output** estao em `docs-workflow/templates/artifact-schemas.md` — agente referencia por ID
4. **Concerns SaaS** estao em `docs-workflow/contexts/saas-concerns-checklist.md` — carregados apenas em 0.4+
5. **Exemplos** sao carregados sob demanda via `docs-workflow/examples/index.md`

## Estrutura de pastas

```
agents/                              — Agentes (so configs)
  0.X-nome/agent.md

docs-workflow/                       — Material de apoio para os agentes
  templates/artifact-schemas.md      — Templates de artefatos (TMPL-000 a 027)
  templates/artifact-summary-format.md — Formato de resumo entre estagios
  contexts/saas-concerns-checklist.md  — Multi-tenancy, seguranca, observabilidade
  contexts/dod-framework.md          — Criterios de qualidade
  examples/index.md                  — Indice de exemplos (few-shot)
  examples/fintech/                  — Exemplos fintech
  examples/edtech/                   — Exemplos edtech

outputs/workflow/                    — Outputs gerados (gestao de estado)
  0.X-nome/full/                     — Artefatos completos
  0.X-nome/compact/                  — Resumos para proximo agente
```
