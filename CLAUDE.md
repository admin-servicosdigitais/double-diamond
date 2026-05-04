# Double Diamond — Backend

## Visão geral do projeto
API REST construída com **FastAPI** que orquestra um pipeline multi-agente de 9 estágios usando o framework **Agno**. Cada estágio do Double Diamond (exploração → definição) é um agente independente em `/agents/`. Os outputs de cada estágio são persistidos em `/outputs/workflow/`.

---

## Stack
- **Runtime:** Python 3.11+
- **Framework web:** FastAPI 0.115 + Uvicorn
- **Agentes:** Agno ≥ 1.0 + OpenAI SDK ≥ 2.31
- **Validação:** Pydantic v2
- **Configuração:** python-dotenv + PyYAML
- **Testes:** pytest + pytest-cov + pytest-mock
- **Infra:** Docker + docker-compose

---

## Domínio — O Workflow Double Diamond

### O que é
Workflow de 9 processos para construção de produtos SaaS AI-First. Cada processo é um agente independente. O humano executa cada passo, valida e decide quando avançar.

### Numeração oficial (sequencial)

| Processo | Nome do agente     | Pasta técnica                        |
|----------|--------------------|--------------------------------------|
| 1        | explorer           | `agents/1-explorer/agent.md`         |
| 2        | intake             | `agents/2-intake/agent.md`           |
| 3        | sourcing           | `agents/3-sourcing/agent.md`         |
| 4        | pesquisa           | `agents/4-pesquisa/agent.md`         |
| 5        | framing            | `agents/5-framing/agent.md`          |
| 6        | ideacao            | `agents/6-ideacao/agent.md`          |
| 7        | validacao          | `agents/7-validacao/agent.md`        |
| 8        | prototype-visual   | `agents/8-prototype-visual/agent.md` |
| 9        | definicao          | `agents/9-definicao/agent.md`        |

### Fluxo: Divergir e Convergir

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
  DESIGN (divergir em soluções, convergir em uma)
  ┌─────────────────────────────────────────┐
  │ 6 ideacao ────────→ 7 validacao         │
  └──────────────────────┬──────────────────┘
                         ▼
  STAKEHOLDER PREVIEW
  ┌─────────────────────────────────────────┐
  │ 8 prototype-visual (obrigatório)        │
  └──────────────────────┬──────────────────┘
                         ▼
  DEFINE
  ┌─────────────────────────────────────────┐
  │ 9 definicao                             │
  └─────────────────────────────────────────┘
```

### Regras de governança do fluxo
1. **Validação humana obrigatória** ao fim de cada processo.
2. Só avançar quando houver aprovação explícita do humano no output `compact/`.
3. O processo **8 prototype-visual é obrigatório** (não opcional).
4. O processo **9 definicao consome o Resumo 7 (validacao)** como entrada técnica oficial.
5. O processo 8 gera preview para stakeholders e registro lateral, sem alterar a base técnica do 9.

### Onde ficam os outputs

Cada agente salva seus artefatos em:
- `outputs/workflow/{agent-id}/full/` — artefatos completos
- `outputs/workflow/{agent-id}/compact/` — resumo comprimido para o próximo processo

O próximo processo lê apenas o `/compact/` do anterior (exceto insumos full necessários do 8).

### Regra do output compacto (obrigatória)
1. O `output_compact.md` deve ser a **concatenação** de um compacto de no máximo **25 linhas por arquivo** existente em `output_full/`.
2. Limite total: `25 × quantidade_de_arquivos_em_output_full`.
   - Ex.: 1 arquivo em `output_full/` → `output_compact.md` com no máximo 25 linhas.
   - Ex.: 3 arquivos em `output_full/` → `output_compact.md` com no máximo 75 linhas.
3. `output_compact.md` é **informação interna de sistema** e **nunca deve ser listado** em respostas, índices ou listagens de artefatos.

### Regras de sessão (economia de tokens)
1. **1 sessão = 1 agente** — contexto limpo por processo.
2. **Nunca cole artefatos completos** entre processos — use o resumo em `outputs/workflow/{agent-id}/compact/`.
3. **Templates de output** estão em `docs-workflow/templates/process-artifact-schemas.md`.
4. **Concerns SaaS** estão em `docs-workflow/contexts/process-saas-concerns-checklist.md` — carregados sob demanda.

---

## Arquitetura técnica — Clean Architecture com DDD

```
src/
├── api/routes/           → Endpoints FastAPI (controllers)
├── application/services/ → Casos de uso / orquestração
├── domain/models/        → Entidades e value objects (Pydantic v2)
├── infrastructure/
│   ├── agents/           → Implementações dos agentes Agno
│   └── persistence/      → Repositórios e persistência
└── loaders/              → Carregamento de configurações e dados

agents/                   → Definições dos 9 agentes por estágio
data/workflows/           → YAMLs de configuração dos workflows
outputs/workflow/         → Outputs gerados por cada estágio
docs-workflow/            → Contextos e templates de prompts
tests/unit/               → Testes unitários espelhando src/
```

---

## Regras de desenvolvimento

### O que NUNCA fazer
- Não alterar `.env`, `.env-example` ou qualquer arquivo de segredos
- Não modificar a estrutura ou sequência dos agentes sem task específica aprovada
- Não commitar com testes falhando
- Não introduzir dependências novas sem atualizar `requirements.txt`
- Não colocar lógica de negócio em `api/routes/` — apenas chamadas para `application/services/`

### Padrões obrigatórios
- Modelos de domínio usam **Pydantic v2** (`model_config`, `model_validator`, etc.)
- Todos os services são **injetados via dependência** no FastAPI (`Depends`)
- Agentes Agno seguem o padrão já estabelecido em `src/infrastructure/agents/`
- Outputs de agentes sempre gravados em `outputs/workflow/<estágio>/full/` e `compact/`
- Configurações de agentes em `data/workflows/` (YAML), nunca hardcoded

### Convenção de commits (Conventional Commits obrigatório)
```
feat(agents): adiciona suporte a retry no agente de validacao
fix(api): corrige serialização de resposta no endpoint de intake
chore(deps): atualiza agno para 1.1.0
docs(workflow): atualiza template do estágio de framing
test(services): adiciona cobertura para caso de erro no sourcing
```

---

## Comandos essenciais

```bash
# Ambiente
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Desenvolvimento
uvicorn src.api.main:app --reload --port 3333

# Docker
docker-compose up --build
docker-compose down

# Testes (rodar sempre antes do commit)
pytest tests/ -v
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Definição de Pronto (DoD) — toda task deve cumprir isso
1. Código implementado seguindo a arquitetura Clean/DDD
2. Testes unitários criados ou atualizados em `tests/unit/`
3. `pytest tests/` passando com 0 falhas
4. Sem imports não utilizados ou código comentado
5. Commit feito com mensagem Conventional Commits
6. PR aberto via `gh pr create --fill`

## Ao concluir uma task
```bash
# 1. Rodar testes
pytest tests/ -v

# 2. Verificar arquivos não rastreados relevantes
git status

# 3. Commitar por chunks
git add -p
git commit -m "feat(escopo): descrição clara do que foi feito"

# 4. Abrir PR
gh pr create --fill --base main
```

---

## Contexto de integração
- O frontend (`double-diamond-front`) consome esta API via HTTP
- Endpoints disponíveis via Postman em `postman/collections/`
- CORS configurado para aceitar o frontend em desenvolvimento (porta 3000)
- Variáveis de ambiente necessárias: ver `.env-example`