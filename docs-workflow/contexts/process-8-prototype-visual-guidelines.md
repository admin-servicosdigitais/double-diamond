# Guidelines para Geracao de Prototipo Visual (estagio 8)

Este documento e a especificacao tecnica que o agente 8 carrega ao gerar HTMLs single-file clicaveis. Define stack, design tokens obrigatorios, estrutura minima, o que fazer e o que nao fazer, e o checklist pre-save.

## Principio central

O HTML gerado e **descartavel por design**. Ele existe para apresentacao a stakeholders — nao para testes de usuario, nao para producao, nao para entrar na base de codigo do produto real. Isso muda todas as decisoes de trade-off a seu favor: simplicidade ganha de performance, CDN ganha de build step, clareza visual ganha de engenharia robusta.

## Stack fixo (nao negociavel)

Todo HTML gerado deve incluir exatamente estas duas dependencias externas e **nenhuma outra**:

```html
<script src="https://cdn.tailwindcss.com"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

- **Tailwind Play CDN**: compila Tailwind no browser em tempo real. Oficialmente marcado como "nao para producao" pela Tailwind — aceito aqui exatamente porque o artefato e descartavel
- **Alpine.js 3.x**: reatividade declarativa leve (~15KB), interatividade suficiente para navegar telas, abrir modais, alternar toggles e simular fluxos

**Proibido**: React, Vue, Svelte, jQuery, htmx, Bootstrap, Materialize, Bulma, imagens externas, fontes externas (usar `system-ui` ou stack nativa), Tailwind compilado, qualquer outro CDN ou pacote.

## Design tokens obrigatorios

Toda geracao deve definir as variaveis CSS abaixo no `:root`. Escolha valores coerentes com o dominio do produto, mas **nunca pule um token**.

### Cores
```css
:root {
  --color-primary:    #0ea5e9;  /* cor principal da marca/acao */
  --color-secondary:  #6366f1;  /* cor secundaria, suporte visual */
  --color-success:    #10b981;  /* feedback positivo, metricas verdes */
  --color-warning:    #f59e0b;  /* atencao, estados intermediarios */
  --color-danger:     #ef4444;  /* erro, alerta critico */

  --color-neutral-50:  #f9fafb;
  --color-neutral-100: #f3f4f6;
  --color-neutral-200: #e5e7eb;
  --color-neutral-300: #d1d5db;
  --color-neutral-400: #9ca3af;
  --color-neutral-500: #6b7280;
  --color-neutral-600: #4b5563;
  --color-neutral-700: #374151;
  --color-neutral-800: #1f2937;
  --color-neutral-900: #111827;
}
```

Ajuste a paleta de acordo com o dominio:
- **Saude/clinico**: primary azul (#0ea5e9), success verde (#10b981), danger vermelho clinico (#dc2626)
- **Fintech/enterprise**: primary azul marinho (#1e3a8a) ou preto (#0f172a)
- **Edtech**: primary roxo/violeta (#7c3aed), secondary laranja (#f97316)
- **Lifestyle/consumo**: primary coral/rosa, secondary amarelo

### Tipografia
```css
:root {
  --font-family-base: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-size-xs:   0.75rem;
  --font-size-sm:   0.875rem;
  --font-size-base: 1rem;
  --font-size-lg:   1.125rem;
  --font-size-xl:   1.25rem;
  --font-size-2xl:  1.5rem;
  --font-size-3xl:  1.875rem;
}
```

Nunca carregue Google Fonts ou qualquer font CDN — use stack nativa.

### Espacamento, raio e sombra
```css
:root {
  --spacing-unit: 0.25rem;
  --radius-sm: 0.375rem;
  --radius-md: 0.75rem;
  --radius-lg: 1.25rem;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
  --shadow-lg: 0 12px 32px rgba(0,0,0,0.12);
}
```

### Uso em Tailwind via arbitrary values
```html
<button class="bg-[var(--color-primary)] text-white rounded-[var(--radius-md)] shadow-[var(--shadow-md)]">
  Agendar doacao
</button>
```

Esse padrao permite que o HTML seja coeso visualmente sem precisar extender o `tailwind.config` (que nao existe com Play CDN).

## Estrutura obrigatoria do HTML

### 1. `<head>` com meta tags de artefato
As meta tags substituem o frontmatter YAML (que nao existe em HTML). Exemplo:

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="artefato" content="8-prototipo-visual">
  <meta name="estagio" content="8">
  <meta name="tipo-usuario" content="doador">
  <meta name="slug" content="saude-hematologia-sangue">
  <meta name="data" content="2026-04-10">
  <meta name="fonte" content="7-prototipo--20260410--saude-hematologia-sangue.md">
  <title>Protótipo Visual — Doador — Vein CRM</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <style>
    :root { /* tokens aqui */ }
    /* device frame CSS aqui */
  </style>
</head>
```

### 2. Banner fixo topo (prototype-only)
Sempre presente, sem excecao. Ocupa os ~36px superiores da tela. Texto exato:

> **Protótipo de apresentacao** — Tailwind Play CDN + Alpine.js — nao e codigo de producao

Estilo sugerido: fundo `--color-warning` amarelado com texto escuro, fonte pequena, `position: fixed; top: 0; left: 0; right: 0; z-index: 9999`.

### 3. Device frame
Duas variantes, escolhidas com base no tipo de usuario:

**Mobile (end-users como doador, aluno, paciente)**:
- Container com largura fixa 375px e altura 812px (padrao iPhone SE/12)
- Bordas arredondadas grandes (`--radius-lg` x 3)
- Sombra grande (`--shadow-lg`) para destacar
- Centralizado na viewport com fundo escuro ao redor (simula "deitando o celular na mesa")
- Notch superior opcional (div pequena no topo)

**Desktop (operadores, admins, coordenadores)**:
- Container `max-w-6xl` (1152px) centralizado
- Header da aplicacao com logo, nome do produto, avatar do usuario
- Sidebar esquerda opcional com navegacao
- Area de conteudo principal com cards/tabelas

### 4. Navegacao Alpine entre telas
Padrao obrigatorio:

```html
<div x-data="{
  screen: 0,
  screens: ['Convite', 'Triagem', 'Horario', 'Consent', 'Check-in', 'Hemograma', 'Proximo convite'],
  next() { if (this.screen < this.screens.length - 1) this.screen++ },
  prev() { if (this.screen > 0) this.screen-- }
}">

  <!-- Pager dots -->
  <div class="flex gap-2 justify-center">
    <template x-for="(name, i) in screens" :key="i">
      <button
        @click="screen = i"
        :class="screen === i ? 'bg-[var(--color-primary)]' : 'bg-[var(--color-neutral-300)]'"
        class="w-2 h-2 rounded-full"
        :aria-label="'Ir para tela ' + name"
      ></button>
    </template>
  </div>

  <!-- Telas -->
  <template x-if="screen === 0">
    <div><!-- conteudo da tela 1 --></div>
  </template>
  <template x-if="screen === 1">
    <div><!-- conteudo da tela 2 --></div>
  </template>

  <!-- Botoes de navegacao -->
  <div class="flex justify-between mt-4">
    <button @click="prev()" :disabled="screen === 0" class="...">Voltar</button>
    <button @click="next()" :disabled="screen === screens.length - 1" class="...">Avancar</button>
  </div>
</div>
```

### 5. Ajustes *must* implementados como interacao real
Nao basta desenhar — o ajuste precisa ser **interativo** no HTML. Exemplos:

- Ajuste "modal de segunda confirmacao" → `x-data="{ open: false }"` + botao que seta `open = true` + `<template x-if="open">` com modal overlay
- Ajuste "disclaimer clinico abaixo da metrica" → texto fixo pequeno em `--color-neutral-500` sob a metrica, sempre visivel
- Ajuste "tutorial de instalacao PWA" → overlay modal que aparece no primeiro load, com 2 passos (screenshots simulados via SVG inline) e botao "entendi, comecar"

### 6. Rodape com metadados
Pequeno texto no bottom do arquivo indicando:
- Slug do caso
- Data de geracao
- Estagio fonte (`7-prototipo--...md`)

Fica como "assinatura" do artefato, util quando stakeholders questionam de onde veio.

## O que fazer

- **Emojis Unicode** em texto quando representam icones simples (✓ ✗ → ← 📍 🩸) — nao precisa de CDN
- **SVG inline** para logos, icones customizados e visualizacoes (barras, donuts, sparklines)
- **Dados mockados realistas** coerentes com o protótipo descritivo (ex: nomes brasileiros, CPF formato valido mas fake, enderecos de cidades reais)
- **Animacoes CSS simples** (`transition`, `@keyframes`) para polish — fade-in de telas, pulsacoes de notificacao
- **Alpine transitions** (`x-transition`) em modais e trocas de tela
- **Acessibilidade basica**: `aria-label` em botoes-icone, `focus-visible` com outline, contraste AA
- **Mobile-first real**: se for tipo mobile, testar que funciona bem em viewport 375x812

## O que NAO fazer

- **Nao carregar imagens externas** (nada de `<img src="https://...">`) — dependencia extra, lenta, pode quebrar
- **Nao usar Google Fonts** ou qualquer CDN de fontes — stack nativa only
- **Nao implementar logica de negocio real** (calculos, validacoes complexas, fetch de APIs) — mocks estaticos
- **Nao inventar dados sensiveis reais** — use placeholders claramente ficticios (nunca CPFs de pessoas reais, nunca emails reais)
- **Nao copiar o texto do protótipo descritivo literalmente** — adapte para copia de UI curta e punchy
- **Nao usar jQuery, axios, lodash ou qualquer lib alem de Alpine** — Alpine e Tailwind cobrem 100% das necessidades do artefato
- **Nao gerar HTMLs > 2500 linhas** — se ultrapassar, revise se esta duplicando conteudo
- **Nao adicionar Service Worker, manifest.json ou recursos PWA reais** — e um HTML simulando um PWA, nao um PWA real
- **Nao usar `innerHTML` dinamico** em Alpine — use `x-text`, `x-html` so se absolutamente necessario

## Checklist do agente antes de salvar

Para cada HTML gerado, passe por este checklist:

- [ ] Tipo de usuario detectado bate com perfil descrito no protótipo (nao inclui revisores)
- [ ] Meta tags de artefato presentes no `<head>`
- [ ] Tailwind Play CDN + Alpine CDN incluidos, nada mais
- [ ] Design tokens completos no `:root` (todas as variaveis obrigatorias)
- [ ] Banner "prototype-only" fixo no topo, sempre visivel
- [ ] Device frame correto (mobile para end-users, desktop para operadores)
- [ ] Todas as telas descritas no protótipo estao presentes (1 tela markdown = 1 tela no HTML)
- [ ] Navegacao Alpine funcional (proxima, anterior, pager dots)
- [ ] Todos os ajustes *must* do relatorio incorporados **como interacao visivel**
- [ ] Acessibilidade basica: aria-labels, foco visivel, contraste AA
- [ ] Sem dependencias externas alem de Tailwind/Alpine
- [ ] Sem dados sensiveis ou PII real
- [ ] Arquivo abre sem erros de console quando carregado no browser
- [ ] Rodape com slug, data e estagio fonte
- [ ] Nome do arquivo segue padrao `8-prototipo-visual--{tipo}--{YYYYMMDD}--{slug}.html`

Se qualquer item falhar, **nao salve** — corrija antes.

## Referencias cruzadas

- Template do artefato: `docs-workflow/templates/process-artifact-schemas.md` (secao TMPL-011.5)
- Formato do resumo compacto: `docs-workflow/templates/process-summary-format.md` (secao Resumo 8)
- Agente orquestrador: `agents/8-prototype-visual/agent.md`
