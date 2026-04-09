# SaaS Product Workflow

Workflow de 10 estagios para construir produtos SaaS AI-First usando Claude Code.
Cada estagio e um agente independente. Voce (humano) executa cada passo e decide quando avancar.

## Estrutura

```
agents/                         ← Configuracao dos 10 agentes
docs-workflow/                  ← Material de apoio (exemplos, templates, contextos)
outputs/workflow/{agent}/       ← Saidas geradas (full/ e compact/)
CLAUDE.md                       ← Orquestrador (carregado automaticamente)
```

## Como usar

### 1. Iniciar o workflow (estagio 0.1)

No Claude Code, cole:

```
Atue conforme o agente definido em agents/0.1-intake/agent.md

Produto: [descreva seu SaaS]
Demanda: [dor do cliente ou ideia de feature]
Dominio: [fintech, healthtech, edtech, etc.]
Segmento: [PME, enterprise, consumidor]
```

O agente vai gerar os artefatos em `outputs/workflow/0.1-intake/full/` e o resumo compacto em `outputs/workflow/0.1-intake/compact/`.

### 2. Avancar para o proximo estagio

```
Atue conforme o agente definido em agents/0.2-pesquisa/agent.md

Leia o resumo compacto em: outputs/workflow/0.1-intake/compact/

Dados disponiveis: [metricas, tickets, NPS, feedback, etc.]
```

Repita para cada estagio. O agente sempre le o `/compact/` do anterior como input.

### 3. Consultar exemplos (opcional)

Se quiser ver como um estagio ficaria preenchido:

```
Leia docs-workflow/examples/fintech/0.4-ideacao.md como referencia
```

Consulte `docs-workflow/examples/index.md` para ver todos os exemplos disponiveis.

## Fluxo visual

```
DISCOVERY          DESIGN              BUILD              SHIP         LEARN
0.1→0.2→0.3    0.4(diverge)→0.5     0.6(diverge)→0.7    0.8→0.9      0.10
 convergir      3-5 alternativas     PRD|Backlog|Arq     convergir    decidir
 no problema    →Go/No-Go            →Specs unificadas   no deploy    proximo
                                                                      ciclo
```

**Momentos de divergencia**: 0.4 (gerar alternativas) e 0.6 (4 artefatos paralelos)
**Momentos de convergencia**: 0.5 (decidir Go/No-Go) e 0.7 (specs unificadas)
**Decisao de ciclo**: 0.10 (iterar / pivotar / escalar / encerrar)

## Economia de tokens

- Cada sessao roda 1 agente so
- Entre estagios, apenas o resumo compacto (~80 palavras) e passado
- Templates e contextos sao carregados sob demanda (nao ficam no prompt)
- Exemplos sao carregados apenas quando voce pede

## Modelos

| Agente | Modelo | Motivo |
|--------|--------|--------|
| 0.1, 0.8, 0.9 | Haiku | Tarefas estruturadas com template fixo |
| 0.2-0.7, 0.10 | Sonnet | Raciocinio analitico/criativo |

Custo estimado: ~$0.61/ciclo completo (sem iteracoes).
