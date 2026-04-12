# Formato de Resumo entre Estagios

Use este formato para comprimir artefatos ao passar de um estagio para o proximo.
**Nunca cole artefatos completos** — use resumos de ~80-120 palavras.

---

## Convencao de nomenclatura dos resumos

Todo resumo compacto salvo em `outputs/workflow/{agent-id}/compact/` segue o padrao:

```
{slug}--{YYYYMMDD}--{agent-name}--resumo.md
```

Regras do slug e do `{agent-name}` sao as mesmas descritas em `artifact-schemas.md` (secao "Convencao de nomenclatura de arquivos"). O slug **deve** ser o mesmo usado nos artefatos `/full/` do mesmo estagio, e deve ser herdado do estagio anterior a partir do 0.1.

**Frontmatter obrigatorio** em todo resumo, antes do corpo:

```yaml
---
estagio: "0.X"
data: YYYY-MM-DD
slug: "{slug}"
slug_origem: "{estagio que definiu o slug atual, ex: 0.0 ou 0.5 em caso de pivot}"
artefato_anterior: "{nome do arquivo /full/ que este resumo comprime}"
---
```

**Exemplos de nomes**:
- `futebol-corrida--20260409--explorer--resumo.md`
- `plataforma-corredores-amadores--20260410--intake--resumo.md`
- `plataforma-corredores-amadores--20260420--definicao--resumo.md`

Quando um estagio tem multiplos artefatos `/full/` (ex: 0.6 gera PRD + Backlog + Arquitetura + Release Plan), o resumo e **unico** por estagio e consolida todos eles — o campo `artefato_anterior` vira uma lista.

---

## Resumo 0.0 → entrada para 0.1

```
Temas explorados: [lista de termos do usuario]
Oportunidade 1: [titulo] — Demanda: [demanda] | Dor: [dor] | Fonte: [fonte] | Segmento: [segmento] | Dominio: [dominio] | Potencial: [A/M/B]
Oportunidade 2: [titulo] — Demanda: [demanda] | Dor: [dor] | Fonte: [fonte] | Segmento: [segmento] | Dominio: [dominio] | Potencial: [A/M/B]
Oportunidade 3: [titulo] — Demanda: [demanda] | Dor: [dor] | Fonte: [fonte] | Segmento: [segmento] | Dominio: [dominio] | Potencial: [A/M/B]
Recomendacao: [titulo da oportunidade mais promissora]
Justificativa: [1-2 frases sobre por que esta e a melhor aposta]
```

## Resumo 0.1 → entrada para 0.2

```
Oportunidade: [titulo] (OPP-[ID])
Tipo: [classificacao]
Persona: [quem sente a dor]
Dor principal: [1 frase]
Hipotese: Acreditamos que [solucao] para [persona] vai gerar [resultado] porque [evidencia]
Decisao: Aceita para discovery
Sponsor: [nome/area]
```

## Resumo 0.1.5 → entrada para 0.2

```
Oportunidade: OPP-[ID]
Top 3 fontes quantitativas: [fonte1 (url)] | [fonte2 (url)] | [fonte3 (url)]
Metricas-chave ja extraidas: [metrica1=valor] | [metrica2=valor] | [metrica3=valor]
Top 3 canais de acesso a usuarios: [canal1] | [canal2] | [canal3]
Mix recomendado: [canal prioritario 1 — metodo] | [canal prioritario 2 — metodo]
Lacunas: [o que so pode ser obtido via entrevista/survey no 0.2]
```

## Resumo 0.2 → entrada para 0.3

```
Oportunidade: OPP-[ID]
Pergunta central: [o que precisamos saber]
Top 3 evidencias: [dado 1] | [dado 2] | [dado 3]
Dor #1: [dor mais critica] (freq: A, sev: A, valor: A)
Dor #2: [segunda dor] (freq: M, sev: A, valor: M)
Jornada atual resumida: [usuario faz X → enfrenta Y → resultado Z]
Incertezas: [1-2 pontos abertos]
```

## Resumo 0.3 → entrada para 0.4

```
Oportunidade: OPP-[ID]
Problema: [persona] precisa de [X] porque [causa], mas hoje [barreira]. Impacto: [negocio]
Hipotese central: Se [X], entao [Y] porque [evidencia]
North Star: [metrica] — baseline [X] → meta [Y] em [prazo]
Metricas leading: [2-3 metricas]
Guardrail: [metrica que nao pode piorar]
Escopo: dentro [X], fora [Y]
```

## Resumo 0.4 → entrada para 0.5

```
Oportunidade: OPP-[ID]
Conceito escolhido: [nome da alternativa]
Abordagem: [1-2 frases de como resolve]
Happy path: [3-5 passos resumidos]
Risco principal: [qual e mitigacao]
Trade-off aceito: [ganho vs perda]
Arquitetura: [frontend/backend/dados em 1 linha cada]
```

## Resumo 0.5 → entrada para 0.6

```
Oportunidade: OPP-[ID]
Decisao: Go / No-Go / Pivotar
Hipotese testada: [qual]
Resultado: [confirmado/refutado/surpresa]
Ajustes ao conceito: [1-3 ajustes]
Restricoes descobertas: [se houver]
```

## Resumo 0.5.5 → registro lateral (NAO alimenta proximo estagio)

O estagio 0.5.5 (prototipo visual para stakeholders) gera HTMLs clicaveis como side-artifact. Seu resumo compacto existe apenas para trackeabilidade e referencia cruzada — **nao e consumido pelo 0.6**. O 0.6 continua lendo apenas o Resumo 0.5 intacto.

Use este formato no arquivo `outputs/workflow/0.5.5-prototype-visual/compact/{slug}--{YYYYMMDD}--prototype-visual--resumo.md`:

```
Oportunidade: OPP-[ID]
Tipos de usuario mapeados: [tipo1 (N telas), tipo2 (M telas), ...]
HTMLs gerados: [lista de caminhos relativos completos]
Design tokens principais: primary=[hex], secondary=[hex], acento=[hex]
Ajustes must incorporados: [lista 1-3 linhas descrevendo como cada ajuste aparece no HTML]
Como apresentar: [dica curta, ex: "abrir cada HTML no Chrome com DevTools > Toggle device toolbar no iPhone SE"]
Fonte: {slug}--{YYYYMMDD}--validacao--prototipo.md + {slug}--{YYYYMMDD}--validacao--relatorio-teste.md
```

**Frontmatter obrigatorio** (alem dos campos padrao do summary):
```yaml
---
estagio: "0.5.5"
data: YYYY-MM-DD
slug: "{slug}"
slug_origem: "{estagio que definiu o slug}"
artefato_anterior: ["{slug}--...--validacao--prototipo.md", "{slug}--...--validacao--relatorio-teste.md"]
entrada_para: "nenhum (side-note)"
---
```

