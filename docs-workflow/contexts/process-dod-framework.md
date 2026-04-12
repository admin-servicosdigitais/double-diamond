# Framework de Criterios de Qualidade (DoD)

Criterios base aplicaveis a todos os estagios. Cada agente adiciona criterios especificos.

---

## Criterios universais

- Nenhum campo vazio ou generico como "a definir"
- Artefatos referenciam o ID da oportunidade (OPP-[ID])
- Decisoes tem justificativa explicita baseada em dados ou evidencias
- Formato segue o template correspondente em `templates/process-artifact-schemas.md`

## Criterios por fase

### Discovery (2–5)
- Evidencias vem de pelo menos 2 fontes distintas
- Hipoteses sao falsificaveis e tem metricas de validacao
- Incertezas registradas honestamente (nao escondidas)
- Metricas tem baseline, meta e prazo

### Design (6–7)
- Pelo menos 3 alternativas genuinamente distintas (nao variacoes)
- Trade-offs documentados sem vies de confirmacao
- Conceito descreve experiencia do usuario, nao so tecnologia
- Criterios de go/no-go definidos ANTES dos resultados

### Build (9)
- Requisitos funcionais tem criterios de aceitacao (quando/dado/entao)
- Arquitetura endereca multi-tenancy, seguranca e observabilidade (ver `contexts/process-saas-concerns-checklist.md`)
- Backlog tem stories no formato correto com prioridade explícita
- Release plan tem rollout progressivo com feature flags
