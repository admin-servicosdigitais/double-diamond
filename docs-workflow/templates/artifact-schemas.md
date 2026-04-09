# Biblioteca de Templates de Artefatos

Use o ID do template para referenciar a estrutura de output esperada em cada estagio.

---

## TMPL-001: Ficha da Oportunidade
**Estagio**: 0.1 | **Arquivo**: `0.1-ficha-oportunidade.md`

```markdown
# Ficha da Oportunidade — [Titulo]

**ID**: OPP-[YYYYMMDD]-[SEQ]
**Data**: [data]
**Fonte**: [origem]
**Tipo**: [dor do cliente | oportunidade de mercado | debito tecnico | incidente | pedido de negocio | inovacao]
**Sponsor provisorio**: [nome/area]
**Status**: Aceita para discovery | Rejeitada

## Descricao da demanda
[texto]

## Segmento / Persona afetada
[quem]

## Impacto estimado
- Alcance: [quantos clientes/usuarios]
- Frequencia: [com que frequencia ocorre]
- Severidade: [baixa/media/alta/critica]
- Valor de negocio: [qualitativo]

## Demandas similares conhecidas
[listar ou "nenhuma identificada"]

## Decisao
[aceita/rejeitada + justificativa]
```

---

## TMPL-002: Hipotese Inicial
**Estagio**: 0.1 | **Arquivo**: `0.1-hipotese-inicial.md`

```markdown
# Hipotese Inicial — [Titulo da Oportunidade]

**Referencia**: OPP-[ID]

## Hipotese
Acreditamos que [solucao proposta] para [persona] vai gerar [resultado esperado] porque [evidencia ou premissa].

## O que precisa ser verdade
1. [premissa 1]
2. [premissa 2]
3. [premissa 3]

## Como saberemos que funciona
- Metrica primaria: [qual]
- Meta: [valor ou direcao]
- Prazo de validacao: [sugestao]

## Riscos conhecidos
- [risco 1]
- [risco 2]
```

---

## TMPL-003: Plano de Pesquisa
**Estagio**: 0.2 | **Arquivo**: `0.2-plano-pesquisa.md`

```markdown
# Plano de Pesquisa — [Titulo]

**Referencia**: OPP-[ID]
**Pergunta central**: [o que precisamos saber]

## Metodos selecionados
| Metodo | Fonte | Amostra | Timeline | Responsavel |
|--------|-------|---------|----------|-------------|
| [metodo] | [fonte] | [n] | [dias] | [quem] |

## Criterios de suficiencia
Consideraremos a pesquisa suficiente quando:
1. [criterio 1]
2. [criterio 2]

## Riscos da pesquisa
- [risco]
```

---

## TMPL-004: Evidencias Consolidadas
**Estagio**: 0.2 | **Arquivo**: `0.2-evidencias.md`

```markdown
# Evidencias — [Titulo]

**Referencia**: OPP-[ID]

## Dados quantitativos
| Fonte | Dado | Valor | Insight |
|-------|------|-------|---------|
| [fonte] | [dado] | [valor] | [insight] |

## Dados qualitativos
| Fonte | Citacao/Observacao | Frequencia | Tema |
|-------|-------------------|------------|------|
| [fonte] | [citacao] | [n de total] | [tema] |

## Benchmarks
| Concorrente/Referencia | O que faz | Diferenca |
|----------------------|-----------|-----------|
| [nome] | [como resolve] | [gap] |
```

---

## TMPL-005: Mapa de Dores
**Estagio**: 0.2 | **Arquivo**: `0.2-mapa-dores.md`

```markdown
# Mapa de Dores — [Titulo]

**Referencia**: OPP-[ID]

## Jornada atual (ponto de dor)
[Descreva passo a passo como o usuario lida com o problema hoje]

## Dores priorizadas
| # | Dor | Frequencia | Severidade | Valor negocio | Score |
|---|-----|-----------|------------|---------------|-------|
| 1 | [dor] | [A/M/B] | [A/M/B] | [A/M/B] | [H/M/L] |

## Incertezas remanescentes
1. [o que ainda nao sabemos]
2. [o que precisaria de mais investigacao]
```

---

## TMPL-006: Problem Statement
**Estagio**: 0.3 | **Arquivo**: `0.3-problem-statement.md`

```markdown
# Problem Statement — [Titulo]

**Referencia**: OPP-[ID]
**Status**: Aprovado | Em revisao

## Declaracao do problema
[Persona] precisa de [necessidade] porque [causa raiz], mas hoje [barreira]. Isso causa [impacto no negocio].

## Hipotese central
Se resolvermos [X], esperamos que [Y] mude em [Z] porque [evidencia].

## Por que agora
- [razao de timing 1]
- [razao de timing 2]

## Escopo
**Dentro**: [lista do que esta incluido]
**Fora**: [lista do que esta excluido e por que]

## Stakeholders alinhados
| Nome/Area | Papel | Status |
|-----------|-------|--------|
| [quem] | [sponsor/consultado/informado] | [alinhado/pendente] |
```

---

## TMPL-007: Metricas de Sucesso
**Estagio**: 0.3 | **Arquivo**: `0.3-metricas-sucesso.md`

```markdown
# Metricas de Sucesso — [Titulo]

**Referencia**: OPP-[ID]

## Metrica norte (North Star)
- **Metrica**: [nome]
- **Baseline atual**: [valor]
- **Meta**: [valor alvo]
- **Prazo**: [quando medir]

## Metricas leading (sinais precoces)
| Metrica | Baseline | Meta | Quando medir |
|---------|----------|------|-------------|
| [metrica] | [atual] | [alvo] | [prazo] |

## Metricas lagging (resultado final)
| Metrica | Baseline | Meta | Quando medir |
|---------|----------|------|-------------|
| [metrica] | [atual] | [alvo] | [prazo] |

## Metricas guardrail (nao piorar)
| Metrica | Limite |
|---------|--------|
| [metrica] | [nao ultrapassar X] |

## Criterios de sucesso
A solucao sera considerada bem-sucedida se:
1. [criterio 1]
2. [criterio 2]
```

---

## TMPL-008: Alternativas de Solucao
**Estagio**: 0.4 | **Arquivo**: `0.4-alternativas.md`

```markdown
# Alternativas de Solucao — [Titulo]

**Referencia**: OPP-[ID]

## Alternativa A: [Nome]
- **Abordagem**: [como resolve o problema]
- **Esforco**: [P/M/G]
- **Risco principal**: [qual]
- **Impacto esperado**: [qual metrica move e quanto]
- **Dependencias**: [o que precisa existir]

## Alternativa B: [Nome]
[mesma estrutura]

## Alternativa C: [Nome]
[mesma estrutura]

## Matriz de decisao
| Criterio (peso) | Alt. A | Alt. B | Alt. C |
|-----------------|--------|--------|--------|
| Impacto na metrica norte (3) | [1-5] | [1-5] | [1-5] |
| Esforco de implementacao (2) | [1-5] | [1-5] | [1-5] |
| Risco tecnico (2) | [1-5] | [1-5] | [1-5] |
| Time-to-value (2) | [1-5] | [1-5] | [1-5] |
| Alinhamento estrategico (1) | [1-5] | [1-5] | [1-5] |
| **Score ponderado** | **[X]** | **[X]** | **[X]** |
```

---

## TMPL-009: Conceito Escolhido
**Estagio**: 0.4 | **Arquivo**: `0.4-conceito-escolhido.md`

```markdown
# Conceito Escolhido — [Titulo]

**Referencia**: OPP-[ID]
**Alternativa selecionada**: [nome]

## Descricao do conceito
[como funciona do ponto de vista do usuario]

## Jornada proposta (happy path)
1. [passo 1]
2. [passo 2]
3. [passo N]

## Arquitetura em alto nivel
- **Frontend**: [abordagem]
- **Backend**: [abordagem]
- **Dados**: [abordagem]
- **Integracoes**: [quais]
- **Multi-tenancy**: [abordagem — ver contexts/saas-concerns-checklist.md]

## Trade-offs aceitos
| O que ganhamos | O que abrimos mao | Por que e aceitavel |
|---------------|-------------------|-------------------|
| [ganho] | [perda] | [justificativa] |

## Riscos do conceito escolhido
| Risco | Probabilidade | Impacto | Mitigacao |
|-------|--------------|---------|-----------|
| [risco] | [A/M/B] | [A/M/B] | [como reduzir] |
```

---

## TMPL-010: Prototipo Descritivo
**Estagio**: 0.5 | **Arquivo**: `0.5-prototipo.md`

```markdown
# Prototipo — [Titulo]

**Referencia**: OPP-[ID]
**Hipotese testavel**: Se [acao], entao [resultado] em [contexto].

## Fluxo principal (tela a tela)

### Tela 1: [Nome]
- **O que o usuario ve**: [descricao]
- **O que o usuario faz**: [acao principal]
- **Feedback do sistema**: [o que acontece]

### Tela N: [Nome]
[mesma estrutura]

## Roteiro de teste
| # | Tarefa | Sucesso se | Metrica |
|---|--------|------------|---------|
| 1 | [tarefa] | [criterio] | [taxa de sucesso / tempo / erros] |

## Perguntas pos-teste
1. [pergunta sobre valor percebido]
2. [pergunta sobre clareza]
3. [pergunta sobre disposicao de uso]
```

---

## TMPL-011: Relatorio de Validacao
**Estagio**: 0.5 | **Arquivo**: `0.5-relatorio-teste.md`

```markdown
# Relatorio de Validacao — [Titulo]

**Referencia**: OPP-[ID]

## Resultados por tarefa
| Tarefa | Sucesso | Tempo medio | Observacoes |
|--------|---------|-------------|-------------|
| [tarefa] | [X de Y] | [tempo] | [padroes observados] |

## Aprendizados
1. **Confirmado**: [o que a hipotese previu e se confirmou]
2. **Surpreendente**: [o que nao esperavamos]
3. **Refutado**: [o que a hipotese previu mas nao se confirmou]

## Decisao
**Go / No-Go / Pivotar**

**Justificativa**: [baseada nos criterios pre-definidos]

## Proximos passos
- Se Go: [o que muda na solucao antes do PRD]
- Se No-Go: [o que investigar ou descartar]
- Se Pivotar: [nova direcao e por que]

## Ajustes recomendados ao conceito
1. [ajuste baseado em aprendizado]
```

---

## TMPL-012: PRD
**Estagio**: 0.6 | **Arquivo**: `0.6-prd.md`

```markdown
# PRD — [Nome da Feature]

**Referencia**: OPP-[ID] | **Versao**: 1.0 | **Data**: [data]
**PM**: [nome] | **Tech Lead**: [nome]

## Contexto e motivacao
[Por que estamos fazendo isso — link com problem statement]

## Objetivos e metricas
| Objetivo | Metrica | Baseline | Meta |
|----------|---------|----------|------|
| [obj] | [metrica] | [atual] | [alvo] |

## Personas e cenarios
**Persona primaria**: [descricao]
**Cenario principal**: [narrativa de uso]

## Requisitos funcionais
| ID | Requisito | Prioridade | Criterio de aceitacao |
|----|-----------|------------|----------------------|
| RF-01 | [requisito] | Must | [quando/dado/entao] |
| RF-02 | [requisito] | Should | [quando/dado/entao] |

## Requisitos nao-funcionais
| ID | Requisito | Especificacao |
|----|-----------|--------------|
| RNF-01 | Performance | [p95 < Xms] |
| RNF-02 | Disponibilidade | [99.X%] |
| RNF-03 | Multi-tenancy | [ver contexts/saas-concerns-checklist.md] |
| RNF-04 | Seguranca | [ver contexts/saas-concerns-checklist.md] |

## Fora de escopo
- [item 1]

## Riscos e dependencias
| Risco/Dependencia | Impacto | Mitigacao |
|-------------------|---------|-----------|
| [item] | [A/M/B] | [acao] |

## Release strategy
- **Fase 1 (MVP)**: [o que entra]
- **Fase 2**: [o que vem depois]
- **Feature flags**: [quais]
```

---

## TMPL-013: Backlog Priorizado
**Estagio**: 0.6 | **Arquivo**: `0.6-backlog.md`

```markdown
# Backlog — [Nome da Feature]

## Epicos
| Epico | Descricao | Prioridade |
|-------|-----------|------------|
| E-01 | [nome] | P0 |
| E-02 | [nome] | P1 |

## User Stories (ordenadas por prioridade)
| ID | Epico | User Story | Pontos | AC resumido |
|----|-------|------------|--------|-------------|
| US-01 | E-01 | Como [persona], quero [acao] para [beneficio] | [XS/S/M/L/XL] | [criterio chave] |

## Spikes tecnicos
| ID | Pergunta a responder | Timebox |
|----|---------------------|---------|
| SP-01 | [o que investigar] | [horas/dias] |
```

---

## TMPL-014: Arquitetura-alvo
**Estagio**: 0.6 | **Arquivo**: `0.6-arquitetura.md`

```markdown
# Arquitetura — [Nome da Feature]

## Visao geral
[Descricao textual: componentes, fluxo de dados, integracoes]

## Componentes
| Componente | Responsabilidade | Tecnologia |
|-----------|-----------------|-----------|
| [nome] | [o que faz] | [stack] |

## Modelo de dados (entidades principais)
| Entidade | Atributos chave | Relacoes |
|----------|----------------|----------|
| [entidade] | [campos] | [FK para] |

## SaaS Concerns
Aplique as diretrizes de `contexts/saas-concerns-checklist.md`:
- Multi-tenancy: [estrategia escolhida e justificativa]
- Observabilidade: [stack escolhida]
- Seguranca: [abordagem]
```

---

## TMPL-015: Release Plan
**Estagio**: 0.6 | **Arquivo**: `0.6-release-plan.md`

```markdown
# Release Plan — [Nome da Feature]

## Fases
| Fase | Escopo | Duracao estimada | Criterio de saida |
|------|--------|-----------------|-------------------|
| 1 - MVP | [user stories] | [semanas] | [criterio] |
| 2 - Maturacao | [user stories] | [semanas] | [criterio] |

## Feature flags
| Flag | Controla | Rollout |
|------|---------|---------|
| [flag_name] | [o que liga/desliga] | [% ou segmento] |

## Rollout progressivo
1. Time interno → 5% canary → 25% → 100%

## Dependencias de release
| Dependencia | Responsavel | Status |
|-------------|-------------|--------|
| [o que precisa estar pronto] | [quem] | [status] |
```

---

## TMPL-016: Specs Tecnicas
**Estagio**: 0.7 | **Arquivo**: `0.7-specs-tecnicas.md`

```markdown
# Specs Tecnicas — [Nome da Feature]

## US-[ID]: [titulo]

**Fluxo tecnico**:
1. [passo com componente, endpoint, payload]

**API Contract**:
- `[METHOD] /api/v1/[resource]`
- Request: `{ campo: tipo }`
- Response: `{ campo: tipo }`
- Erros: `400 [motivo], 404 [motivo], 403 [motivo]`

**Modelo de dados (DDL resumido)**:
- Tabela: [nome] — campos: [lista com tipos]
- Indices: [quais]
- Tenant isolation: [como tenant_id e aplicado]

**Regras de negocio**:
1. [regra com condicao e resultado]

**Observabilidade**:
- Logs: [eventos a logar]
- Metricas: [contadores, histogramas]
- Alertas: [condicoes]
```

---

## TMPL-017: Plano de Testes
**Estagio**: 0.7 | **Arquivo**: `0.7-plano-testes.md`

```markdown
# Plano de Testes — [Nome da Feature]

## Estrategia
- **Unitarios**: cobertura minima [X%] em regras de negocio
- **Integracao**: endpoints, filas, banco
- **E2E**: happy path + edge cases criticos
- **Performance**: carga esperada + 3x

## Casos de teste prioritarios
| ID | Tipo | Cenario | Input | Expected | Automacao |
|----|------|---------|-------|----------|-----------|
| TC-01 | Unit | [cenario] | [dado] | [esperado] | Sim |

## Testes de seguranca e multi-tenancy
Aplique os cenarios de `contexts/saas-concerns-checklist.md`:
| Cenario | O que valida |
|---------|-------------|
| Tenant A acessa dado de B | Retorna 403 |
| Token expirado | Retorna 401 |
| SQL injection em campo X | Input sanitizado |
| CRUD com tenant_id | Dados isolados |
| Query sem tenant_id | Rejeitada ou filtrada |
```

---

## TMPL-018: Documentacao Tecnica
**Estagio**: 0.7 | **Arquivo**: `0.7-doc-tecnica.md`

```markdown
# Doc Tecnica — [Nome da Feature]

## Visao geral
[O que o servico faz em 2-3 frases]

## Arquitetura implementada
[Componentes, fluxo, tecnologias usadas]

## Como rodar localmente
1. [passo a passo]

## Variaveis de ambiente
| Variavel | Descricao | Exemplo |
|----------|-----------|---------|
| [VAR] | [o que faz] | [valor exemplo] |

## Endpoints
| Metodo | Path | Descricao | Auth |
|--------|------|-----------|------|
| [POST] | [/api/v1/x] | [o que faz] | [Bearer token] |

## Decisoes tecnicas (ADRs resumidos)
| Decisao | Alternativas | Escolha | Motivo |
|---------|-------------|---------|--------|
| [o que] | [opcoes] | [escolhida] | [por que] |
```

---

## TMPL-019: Release Notes
**Estagio**: 0.8 | **Arquivo**: `0.8-release-notes.md`

```markdown
# Release Notes — [Feature] v[X.Y.Z]

**Data prevista**: [data] | **Tipo**: Feature | Bugfix | Melhoria

## O que muda para o usuario
- [mudanca visivel 1]

## O que muda internamente
- [mudanca tecnica 1]

## Breaking changes
- [nenhum | lista]

## Feature flags
| Flag | Estado no deploy | Rollout |
|------|-----------------|---------|
| [flag] | [off] | [ativacao manual apos validacao] |

## Problemas conhecidos
- [item ou "nenhum identificado"]
```

---

## TMPL-020: Plano de Rollout e Rollback
**Estagio**: 0.8 | **Arquivo**: `0.8-rollout-rollback.md`

```markdown
# Plano de Rollout — [Feature]

## Sequencia de deploy
| Etapa | Ambiente | Acao | Criterio de avanco | Responsavel |
|-------|---------|------|-------------------|-------------|
| 1 | Staging | Deploy + smoke test | Testes passam | DevOps |
| 2 | Producao (canary 5%) | Deploy + monitorar 30min | Error rate < 0.1% | SRE |
| 3 | Producao (25%) | Expandir rollout | Sem degradacao | SRE |
| 4 | Producao (100%) | Full rollout | Metricas estaveis 2h | PM + SRE |

## Criterios de rollback
Reverter imediatamente se:
1. Error rate > [X%]
2. Latencia p95 > [Xms]
3. Incidente de seguranca ou vazamento de dados entre tenants

## Procedimento de rollback
1. [desligar feature flag / reverter deploy]
2. [notificar stakeholders]
3. [investigar causa raiz]
```

---

## TMPL-021: Checklist UAT
**Estagio**: 0.8 | **Arquivo**: `0.8-checklist-uat.md`

```markdown
# Checklist de Homologacao — [Feature]

## Funcional
- [ ] Happy path completo validado
- [ ] Edge cases criticos testados
- [ ] Permissoes e roles verificados
- [ ] Dados entre tenants isolados

## Nao-funcional
- [ ] Performance dentro do SLA
- [ ] Teste de carga executado
- [ ] Scan de seguranca sem criticals/highs
- [ ] Logs e metricas fluindo

## Release readiness
- [ ] Release notes revisadas
- [ ] Rollback plan documentado e testado
- [ ] Monitoramento e alertas configurados
- [ ] Stakeholders notificados
- [ ] Aprovacao formal registrada

**Aprovador**: [nome] | **Data**: [data] | **Status**: Aprovado | Reprovado
```

---

## TMPL-022: Checklist de Producao
**Estagio**: 0.9 | **Arquivo**: `0.9-checklist-producao.md`

```markdown
# Checklist Go-Live — [Feature]

**Data do deploy**: [data] | **Janela**: [horario]

## Pre-deploy
- [ ] Backup do banco executado
- [ ] Feature flags configuradas (off)
- [ ] Monitoramento e dashboards prontos
- [ ] Equipe de plantao escalada
- [ ] Canal de war room criado

## Durante o deploy
- [ ] Deploy executado no ambiente de producao
- [ ] Smoke tests automatizados passaram
- [ ] Health checks de todos os servicos OK
- [ ] Feature flag ativada para grupo canary

## Pos-deploy (primeiras 2h)
- [ ] Error rate monitorado e dentro do esperado
- [ ] Latencia dentro do SLA
- [ ] Sem alertas de seguranca ou isolamento de tenant
- [ ] Primeiros usuarios operando com sucesso

## Pos-deploy (primeiras 24h)
- [ ] Metricas de adocao acompanhadas
- [ ] Tickets de suporte triados
- [ ] Comunicacao de lancamento enviada
```

---

## TMPL-023: Playbook de Suporte
**Estagio**: 0.9 | **Arquivo**: `0.9-playbook-suporte.md`

```markdown
# Playbook de Suporte — [Feature]

## Visao geral da feature
[2-3 frases para contextualizar o suporte]

## Problemas esperados e respostas
| Sintoma do usuario | Causa provavel | Acao do suporte | Escalacao |
|-------------------|---------------|-----------------|-----------|
| [sintoma] | [causa] | [acao] | [se persistir → quem] |

## Perguntas frequentes (FAQ)
1. **[pergunta]**: [resposta]

## Criterios de escalacao
| Severidade | Criterio | Para quem | SLA resposta |
|-----------|---------|-----------|-------------|
| P1 | Perda de dados ou acesso | Eng on-call | 15min |
| P2 | Feature nao funciona | Eng team | 2h |
| P3 | Duvida ou melhoria | Backlog | Proximo sprint |
```

---

## TMPL-024: Comunicacao aos Usuarios
**Estagio**: 0.9 | **Arquivo**: `0.9-comunicacao.md`

```markdown
# Comunicacao de Lancamento — [Feature]

## In-app notification (curta)
**Titulo**: [titulo]
**Corpo**: [2-3 frases sobre o que mudou e o beneficio]
**CTA**: [ex: "Experimentar agora"]

## Email de lancamento
**Assunto**: [assunto]
**Preview text**: [primeira linha]
**Corpo**:
Ola [nome],
[Paragrafo 1: o que lancamos e por que]
[Paragrafo 2: como funciona em 2-3 passos]
[Paragrafo 3: CTA + onde buscar ajuda]

## Notas para CS/Vendas (enablement interno)
- **O que e**: [1 frase]
- **Para quem**: [segmento/persona]
- **Pitch de valor**: [1-2 frases]
- **Objecoes comuns**: [objecao → resposta]
- **Demo**: [link ou roteiro simplificado]
```

---

## TMPL-025: Relatorio Pos-Release
**Estagio**: 0.10 | **Arquivo**: `0.10-relatorio-pos-release.md`

```markdown
# Relatorio Pos-Release — [Feature]

**Periodo de observacao**: [data inicio] a [data fim]

## Hipotese vs Realidade
| Metrica | Meta | Resultado | Delta | Veredicto |
|---------|------|-----------|-------|-----------|
| [metrica] | [meta] | [real] | [+/-X%] | Atingida / Nao atingida |

## Metricas DORA da entrega
| Metrica | Valor |
|---------|-------|
| Lead time for changes | [tempo] |
| Deployment frequency | [frequencia] |
| Change failure rate | [%] |
| Failed deployment recovery time | [tempo] |

## Feedback qualitativo
| Fonte | Tema | Sentimento | Volume |
|-------|------|-----------|--------|
| [fonte] | [tema] | [positivo/negativo] | [N tickets] |

## Incidentes
| Data | Severidade | Descricao | Tempo de resolucao | Causa raiz |
|------|-----------|-----------|-------------------|-----------|
| [data] | [P1/P2/P3] | [o que houve] | [tempo] | [causa] |

## Custo por tenant (se aplicavel)
| Componente | Custo mensal estimado |
|-----------|---------------------|
| [infra] | [valor] |
```

---

## TMPL-026: Decisao de Continuidade
**Estagio**: 0.10 | **Arquivo**: `0.10-decisao-continuidade.md`

```markdown
# Decisao de Continuidade — [Feature]

## Recomendacao
**Iterar / Pivotar / Escalar / Encerrar**

## Justificativa
[Baseada nos dados do relatorio — por que esta decisao]

## Se iterar
- Ajustes priorizados:
  1. [ajuste 1 — baseado em dado X]
  2. [ajuste 2 — baseado em feedback Y]

## Se escalar
- Fase 2 prevista: [escopo]
- Investimento adicional: [estimativa]

## Licoes aprendidas
1. **O que funcionou**: [licao]
2. **O que nao funcionou**: [licao]
3. **O que faremos diferente**: [mudanca no processo]
```

---

## TMPL-027: Backlog Atualizado
**Estagio**: 0.10 | **Arquivo**: `0.10-backlog-atualizado.md`

```markdown
# Backlog Atualizado — [Feature]

## Novos itens (originados do aprendizado)
| ID | User Story | Origem | Prioridade |
|----|-----------|--------|------------|
| US-N+1 | [story] | [feedback/dado/incidente] | [P0/P1/P2] |

## Itens repriorizados
| ID | Story | Prioridade anterior | Nova prioridade | Motivo |
|----|-------|---------------------|-----------------|--------|
| [id] | [story] | [antes] | [depois] | [por que] |

## Debitos tecnicos identificados
| ID | Debito | Impacto se ignorar | Prioridade |
|----|--------|-------------------|------------|
| TD-01 | [descricao] | [consequencia] | [P0/P1/P2] |
```
