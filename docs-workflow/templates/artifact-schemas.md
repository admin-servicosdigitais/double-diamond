# Biblioteca de Templates de Artefatos

Use o ID do template para referenciar a estrutura de output esperada em cada estagio.

---

## Convencao de nomenclatura de arquivos

Todo artefato salvo em `outputs/workflow/{agent-id}/full/` e `/compact/` **deve** seguir o padrao:

```
{slug}--{YYYYMMDD}--{agent-name}--{artifact-name}.ext
```

**Componentes**:
- `{slug}` — identificador humano-legivel do contexto da execucao
- `{YYYYMMDD}` — data de criacao do artefato (ex: `20260409`)
- `{agent-name}` — nome do agente em kebab-case: `explorer`, `intake`, `sourcing`, `pesquisa`, `framing`, `ideacao`, `validacao`, `prototype-visual`, `definicao`
- `{artifact-name}` — nome canonico do artefato em kebab-case (ex: `radar-oportunidades`, `prd`, `arquitetura`)

**Regras do slug**:
- Lowercase, ASCII puro (sem acentos), espacos e pontuacao substituidos por `-`
- Maximo de 40 caracteres — truncar preservando palavras inteiras
- **Origem**:
  - Em `0.0`: derivado dos temas recebidos do usuario (ex: `futebol-corrida`)
  - Em `0.1` em diante: derivado do **titulo da oportunidade escolhida** no 0.0 (ou do nome do produto quando ja definido). O slug **permanece estavel** do 0.1 ate o 0.6 — **nao recriar a cada estagio**
- **Herança**: cada estagio le o slug do resumo compacto do estagio anterior (campo `slug:` no frontmatter do resumo) e reutiliza. Se o slug mudar (ex: pivot no 0.5), registrar explicitamente no resumo e usar o novo a partir dali

**Colisao**: se ja existir arquivo com mesmo nome no mesmo dia, adicionar sufixo `-HHMM` apos a data (ex: `saude-hematologia-sangue--20260409-1430--explorer--radar-oportunidades.md`).

**Excecao — estagio 0.5.5 (prototipo visual HTML)**: o `{artifact-name}` e substituido pelo `{tipo}` de usuario:
```
{slug}--{YYYYMMDD}--prototype-visual--{tipo}.html
```
O `{tipo}` e detectado dinamicamente pelo agente 0.5.5 a partir dos fluxos descritos no protótipo 0.5 (ex: `doador`, `coordenador`, `professor`). Ver TMPL-011.5.

**Resumos compactos** em `/compact/` seguem o mesmo padrao com `{artifact-name}` fixo como `resumo`:
```
{slug}--{YYYYMMDD}--{agent-name}--resumo.md
```

**Exemplos**:
- `futebol-corrida--20260409--explorer--radar-oportunidades.md`
- `plataforma-corredores-amadores--20260410--intake--ficha-oportunidade.md`
- `saude-hematologia-sangue--20260410--prototype-visual--doador.html`
- `plataforma-corredores-amadores--20260420--definicao--prd.md`
- `saude-hematologia-sangue--20260410--explorer--resumo.md`

Os campos `**Arquivo**` nos templates abaixo usam os placeholders `{YYYYMMDD}` e `{slug}` — substitua ao gerar o artefato.

---

## TMPL-000: Radar de Oportunidades
**Estagio**: 0.0 | **Arquivo**: `{slug}--{YYYYMMDD}--explorer--radar-oportunidades.md`

```markdown
# Radar de Oportunidades — [Temas]

**Data**: [data]
**Temas recebidos**: [lista de termos do usuario]

## Tendencias identificadas
| # | Tendencia | Fonte | Relevancia para os temas |
|---|-----------|-------|--------------------------|
| 1 | [tendencia] | [publicacao, data] | [como conecta com os temas] |

## Oportunidades

### Oportunidade 1: [Titulo]
- **Angulo**: [tecnologia | comportamento | regulacao | monetizacao | comunidade]
- **Tipo de mercado**: [massa | nicho/alternativo] — oportunidades de nicho sao preferidas
- **Perfil de crescimento**: [gradual/bootstrap-friendly | moderado | hypergrowth]
- **Demanda**: [o que o mercado esta pedindo]
- **Dor**: [problema concreto do segmento]
- **Fontes**: [minimo 7 — noticias, dados, reports, foruns com citacao]
- **Segmento-alvo**: [PME | enterprise | consumidor | prosumer | micro-SMB — especificar nicho]
- **Dominio**: [fintech | healthtech | edtech | sportstech | etc.]
- **Potencial disruptivo**: [alto | medio | baixo]
- **Por que agora**: [timing — o que mudou recentemente]
- **Produto SaaS possivel**: [descricao em 1-2 frases]

#### Concorrentes (minimo 5-7)
| # | Nome | URL | Modelo | Estagio | Proposta de valor | Gap observado |
|---|------|-----|--------|---------|-------------------|---------------|
| 1 | [nome] | [url] | [SaaS/marketplace/API/etc] | [bootstrap/seed/A+/publico] | [diferencial] | [o que nao cobrem] |
| 2 | ... | ... | ... | ... | ... | ... |

**Sintese competitiva**: [onde estao os gaps agregados, qual flanco esta aberto para um entrante pequeno]

### Oportunidade 2: [Titulo]
[mesma estrutura]

### Oportunidade 3: [Titulo]
[mesma estrutura]

[adicionar mais se identificadas]

## Matriz comparativa
| Criterio | Opp 1 | Opp 2 | Opp 3 |
|----------|-------|-------|-------|
| Potencial disruptivo | [5/4/3/2/1] | [5/4/3/2/1] | [5/4/3/2/1] |
| Timing de mercado | [5/4/3/2/1] | [5/4/3/2/1] | [5/4/3/2/1] |
| Viabilidade tecnica | [5/4/3/2/1] | [5/4/3/2/1] | [5/4/3/2/1] |
| Tamanho do mercado | [5/4/3/2/1] | [5/4/3/2/1] | [5/4/3/2/1] |
| Competicao existente | [5/4/3/2/1] | [5/4/3/2/1] | [5/4/3/2/1] |
| Viabilidade de crescimento gradual (bootstrap) | [5/4/3/2/1] | [5/4/3/2/1] | [5/4/3/2/1] |
| Densidade de nicho (subatendido) | [5/4/3/2/1] | [5/4/3/2/1] | [5/4/3/2/1] |

## Recomendacao
**Oportunidade mais promissora**: [titulo]
**Justificativa**: [por que esta e a melhor aposta — baseada nos criterios acima]
```

---

## TMPL-001: Ficha da Oportunidade
**Estagio**: 0.1 | **Arquivo**: `{slug}--{YYYYMMDD}--intake--ficha-oportunidade.md`

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
**Estagio**: 0.1 | **Arquivo**: `{slug}--{YYYYMMDD}--intake--hipotese-inicial.md`

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

## TMPL-002A: Matriz de Fontes Quantitativas
**Estagio**: 0.1.5 | **Arquivo**: `{slug}--{YYYYMMDD}--sourcing--fontes-quantitativas.md`

```markdown
# Matriz de Fontes Quantitativas — [Titulo da Oportunidade]

**Referencia**: OPP-[ID]
**Persona**: [persona]
**Dominio**: [dominio]
**Segmento**: [segmento]
**Data**: [YYYY-MM-DD]

## Queries utilizadas
- [query 1 em PT]
- [query 2 em EN]
- [query 3 ...]

## Fontes validadas
| # | Fonte | Tipo | URL | Data | Autoridade | Metrica-chave extraida | Relevancia |
|---|-------|------|-----|------|------------|------------------------|------------|
| 1 | [nome publicacao] | report/dataset/benchmark/academico | [url] | [YYYY-MM] | A/M/B | [metrica = valor] | A/M/B |
| 2 | ... | ... | ... | ... | ... | ... | ... |

(minimo 8 fontes, pelo menos 3 tipos distintos)

## Sintese quantitativa
- [numero 1 mais relevante + fonte]
- [numero 2 mais relevante + fonte]
- [numero 3 mais relevante + fonte]
- [numero 4 ...]
- [numero 5 ...]

## Lacunas
- [o que nao foi possivel encontrar na web e precisa de pesquisa primaria]
- [dados confidenciais/pagos sem preview]
```

---

## TMPL-002B: Mapa de Acesso a Usuarios
**Estagio**: 0.1.5 | **Arquivo**: `{slug}--{YYYYMMDD}--sourcing--acesso-usuarios.md`

```markdown
# Mapa de Acesso a Usuarios — [Titulo da Oportunidade]

**Referencia**: OPP-[ID]
**Persona-alvo**: [persona]
**Data**: [YYYY-MM-DD]

## Canais identificados
| # | Canal | Tipo | URL | Tamanho aproximado | Metodo de engajamento | Custo estimado | Relevancia |
|---|-------|------|-----|--------------------|-----------------------|----------------|------------|
| 1 | [nome] | subreddit/linkedin/discord/forum/plataforma-paga/newsletter | [url] | [N membros/assinantes] | post/DM/survey/entrevista paga | [R$ ou gratuito] | A/M/B |
| 2 | ... | ... | ... | ... | ... | ... | ... |

(minimo 5 canais, pelo menos 2 categorias)

## Recomendacao de mix
1. **[canal prioritario 1]** — [metodo] — [justificativa de por que comecar por aqui]
2. **[canal prioritario 2]** — [metodo] — [justificativa]
3. **[canal prioritario 3]** — [metodo] — [justificativa]

## Restricoes observadas
- [barreiras de entrada: moderacao, comunidades fechadas, custo, regras de self-promotion]
- [consideracoes eticas: LGPD, consentimento, anonimato]
```

---

## TMPL-003: Plano de Pesquisa
**Estagio**: 0.2 | **Arquivo**: `{slug}--{YYYYMMDD}--pesquisa--plano-pesquisa.md`

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
**Estagio**: 0.2 | **Arquivo**: `{slug}--{YYYYMMDD}--pesquisa--evidencias.md`

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
**Estagio**: 0.2 | **Arquivo**: `{slug}--{YYYYMMDD}--pesquisa--mapa-dores.md`

```markdown
# Mapa de Dores — [Titulo]

**Referencia**: OPP-[ID]

## Jornada atual (ponto de dor)
[Descreva passo a passo como o usuario lida com o problema hoje]

## Dores priorizadas
| # | Dor | Frequencia | Severidade | Valor negocio | Score |
|---|-----|-----------|------------|---------------|-------|
| 1 | [dor] | [5/4/3/2/1] | [5/4/3/2/1] | [5/4/3/2/1] | [H/M/L] |

## Incertezas remanescentes
1. [o que ainda nao sabemos]
2. [o que precisaria de mais investigacao]
```

---

## TMPL-006: Problem Statement
**Estagio**: 0.3 | **Arquivo**: `{slug}--{YYYYMMDD}--framing--problem-statement.md`

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
**Estagio**: 0.3 | **Arquivo**: `{slug}--{YYYYMMDD}--framing--metricas-sucesso.md`

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
**Estagio**: 0.4 | **Arquivo**: `{slug}--{YYYYMMDD}--ideacao--alternativas.md`

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
**Estagio**: 0.4 | **Arquivo**: `{slug}--{YYYYMMDD}--ideacao--conceito-escolhido.md`

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
| [risco] | [5/4/3/2/1] | [5/4/3/2/1] | [como reduzir] |
```

---

## TMPL-010: Prototipo Descritivo
**Estagio**: 0.5 | **Arquivo**: `{slug}--{YYYYMMDD}--validacao--prototipo.md`

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
**Estagio**: 0.5 | **Arquivo**: `{slug}--{YYYYMMDD}--validacao--relatorio-teste.md`

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

## TMPL-011.5: Prototipo Visual Clicavel (HTML)
**Estagio**: 0.5.5 | **Arquivo**: `{slug}--{YYYYMMDD}--prototype-visual--{tipo}.html`

Diferentemente dos outros templates desta biblioteca, este artefato e um **arquivo HTML single-file** (nao markdown). A especificacao completa de stack, design tokens, estrutura obrigatoria, checklist e what-not-to-do vive em:

> **`docs-workflow/contexts/prototype-visual-guidelines.md`** — spec tecnica carregada pelo agente 0.5.5

Resumo das regras inegociaveis:
- **Stack**: Tailwind Play CDN + Alpine.js 3.x — nada mais
- **Tokens**: CSS variables em `:root` para cores, tipografia, espacamento, raio, sombra
- **Estrutura**: meta tags de artefato no `<head>`, banner fixo "prototype-only" no topo, device frame (mobile 375x812 para end-users, `max-w-6xl` desktop para operadores), navegacao Alpine entre telas, ajustes *must* do relatorio 0.5 implementados como interacao real
- **Quantidade de arquivos**: um HTML por tipo de usuario com fluxo descrito tela-a-tela no 0.5-prototipo (detectado dinamicamente pelo agente)

**Meta tags obrigatorias no `<head>`** (substituem o frontmatter YAML):
```html
<meta name="artefato" content="0.5.5-prototipo-visual">
<meta name="estagio" content="0.5.5">
<meta name="tipo-usuario" content="{tipo}">
<meta name="slug" content="{slug}">
<meta name="data" content="{YYYY-MM-DD}">
<meta name="fonte" content="{slug}--{YYYYMMDD}--validacao--prototipo.md">
```

**Esqueleto minimo do HTML**:
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- meta tags de artefato -->
  <title>Protótipo Visual — {tipo} — {produto}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <style>
    :root { /* design tokens */ }
    .device-frame { /* mobile 375x812 ou desktop max-w-6xl */ }
    .proto-banner { position: fixed; top: 0; ... }
  </style>
</head>
<body class="bg-[var(--color-neutral-100)]">
  <div class="proto-banner">Protótipo de apresentacao — nao e codigo de producao</div>
  <main class="device-frame" x-data="{ screen: 0, screens: [...] }">
    <!-- telas em <template x-if="screen === N"> -->
    <!-- navegacao proxima/anterior + pager dots -->
  </main>
  <footer>Slug: {slug} · Data: {YYYY-MM-DD} · Fonte: {slug}--...--validacao--prototipo.md</footer>
</body>
</html>
```

**Este artefato NAO gera resumo compacto que alimenta o 0.6.** Gera apenas um side-note em `outputs/workflow/0.5.5-prototype-visual/compact/{slug}--{YYYYMMDD}--prototype-visual--resumo.md` para trackeabilidade. O 0.6 continua consumindo o Resumo 0.5 intacto. Ver `artifact-summary-format.md` secao "Resumo 0.5.5".

---

## TMPL-012: PRD
**Estagio**: 0.6 | **Arquivo**: `{slug}--{YYYYMMDD}--definicao--prd.md`

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
| [item] | [5/4/3/2/1] | [acao] |

## Release strategy
- **Fase 1 (MVP)**: [o que entra]
- **Fase 2**: [o que vem depois]
- **Feature flags**: [quais]
```

---

## TMPL-013: Backlog Priorizado
**Estagio**: 0.6 | **Arquivo**: `{slug}--{YYYYMMDD}--definicao--backlog.md`

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
**Estagio**: 0.6 | **Arquivo**: `{slug}--{YYYYMMDD}--definicao--arquitetura.md`

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
**Estagio**: 0.6 | **Arquivo**: `{slug}--{YYYYMMDD}--definicao--release-plan.md`

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
