# Framework de Criterios de Qualidade (DoD)

Criterios base aplicaveis a todos os estagios. Cada agente adiciona criterios especificos.

---

## Criterios universais

- Nenhum campo vazio ou generico como "a definir"
- Artefatos referenciam o ID da oportunidade (OPP-[ID])
- Decisoes tem justificativa explicita baseada em dados ou evidencias
- Formato segue o template correspondente em `templates/artifact-schemas.md`

## Criterios por fase

### Discovery (0.1–0.3)
- Evidencias vem de pelo menos 2 fontes distintas
- Hipoteses sao falsificaveis e tem metricas de validacao
- Incertezas registradas honestamente (nao escondidas)
- Metricas tem baseline, meta e prazo

### Design (0.4–0.5)
- Pelo menos 3 alternativas genuinamente distintas (nao variacoes)
- Trade-offs documentados sem vies de confirmacao
- Conceito descreve experiencia do usuario, nao so tecnologia
- Criterios de go/no-go definidos ANTES dos resultados

### Build (0.6–0.7)
- Requisitos funcionais tem criterios de aceitacao (quando/dado/entao)
- API contracts com request, response e codigos de erro
- Tenant isolation explicito em cada spec
- Plano de testes cobre seguranca e multi-tenancy (ver `contexts/saas-concerns-checklist.md`)
- Documentacao suficiente para outro dev onboardar

### Ship (0.8–0.9)
- Release notes separam mudanca visivel de mudanca tecnica
- Rollout e progressivo com criterios de avanco explicitos
- Rollback tem procedimento passo a passo
- Comunicacao existe para usuario final E time interno

### Learn (0.10)
- Todas as metricas de 0.3 tem resultado medido
- DORA metrics reportadas
- Decisao de continuidade e explicita e justificada com dados
- Backlog atualizado com origem rastreavel
