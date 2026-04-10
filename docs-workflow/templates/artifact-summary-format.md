# Formato de Resumo entre Estagios

Use este formato para comprimir artefatos ao passar de um estagio para o proximo.
**Nunca cole artefatos completos** — use resumos de ~80-120 palavras.

---

## Convencao de nomenclatura dos resumos

Todo resumo compacto salvo em `outputs/workflow/{agent-id}/compact/` segue o padrao:

```
resumo-{estagio}--{YYYYMMDD}--{slug}.md
```

Regras do slug sao as mesmas descritas em `artifact-schemas.md` (secao "Convencao de nomenclatura de arquivos"). O slug **deve** ser o mesmo usado nos artefatos `/full/` do mesmo estagio, e deve ser herdado do estagio anterior a partir do 0.1.

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
- `resumo-0.0--20260409--futebol-corrida.md`
- `resumo-0.1--20260410--plataforma-corredores-amadores.md`
- `resumo-0.6--20260420--plataforma-corredores-amadores.md`

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

## Resumo 0.6 → entrada para 0.7

```
Oportunidade: OPP-[ID]
Feature: [nome]
Requisitos Must: [RF-01, RF-02, ...] — [1 frase cada]
Arquitetura: [componentes principais + stack]
Multi-tenancy: [estrategia]
Stories prioritarias: [US-01 a US-05 em 1 linha cada]
Spikes: [se houver]
```

## Resumo 0.7 → entrada para 0.8

```
Oportunidade: OPP-[ID]
Feature: [nome]
Endpoints criados: [lista METHOD /path]
Cobertura de testes: [unitarios X%, integracao Y cenarios, E2E Z cenarios]
Riscos tecnicos: [1-2]
Decisoes tecnicas chave: [1-2 ADRs resumidos]
```

## Resumo 0.8 → entrada para 0.9

```
Oportunidade: OPP-[ID]
Feature: [nome] v[X.Y.Z]
Status UAT: Aprovado/Reprovado
Feature flags: [lista com estado]
Rollout plan: [staging → canary X% → expand Y% → full]
Criterios de rollback: [1-2 principais]
Problemas conhecidos: [se houver]
```

## Resumo 0.9 → entrada para 0.10

```
Oportunidade: OPP-[ID]
Feature: [nome]
Data go-live: [data]
Status deploy: [sucesso/incidente]
Metricas primeiras 24h: [error rate, latencia, adocao]
Tickets suporte: [N, temas principais]
```
