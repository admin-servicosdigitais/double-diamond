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

### Build (0.6)
- Requisitos funcionais tem criterios de aceitacao (quando/dado/entao)
- Arquitetura endereca multi-tenancy, seguranca e observabilidade (ver `contexts/saas-concerns-checklist.md`)
- Backlog tem stories no formato correto com prioridade explícita
- Release plan tem rollout progressivo com feature flags
