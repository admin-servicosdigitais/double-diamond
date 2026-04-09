# SaaS Concerns Checklist

Referencia compartilhada para multi-tenancy, seguranca e observabilidade.
Carregue este arquivo nos estagios 0.4+ quando o agente solicitar.

---

## Multi-Tenancy

### Estrategia de isolamento
Escolha uma e justifique:
- **Pool**: banco compartilhado, isolamento por `tenant_id` em todas as tabelas
- **Silo**: banco separado por tenant (maior custo, maior isolamento)
- **Bridge**: schema separado por tenant no mesmo banco

### Regras obrigatorias
- Toda tabela com dados de negocio deve ter coluna `tenant_id`
- Toda query deve filtrar por `tenant_id` — queries sem filtro devem ser rejeitadas
- Indices compostos devem incluir `tenant_id` como primeiro campo
- APIs devem extrair `tenant_id` do token/contexto, nunca do request body
- Testes devem validar: tenant A nao acessa dados de tenant B (esperar 403)

---

## Seguranca

### Autenticacao
- OAuth2 / SAML / MFA conforme o tier do cliente
- Tokens com expiracao curta + refresh token
- Rate limiting por tenant e por usuario

### Autorizacao
- RBAC (Role-Based) ou ABAC (Attribute-Based) conforme complexidade
- Roles minimos: admin, member, viewer (por tenant)
- Permissoes verificadas no backend, nunca apenas no frontend

### Dados sensiveis
- Encriptacao at rest (AES-256) e in transit (TLS 1.2+)
- PII mascarada em logs
- Auditoria de acesso a dados sensiveis

### Testes de seguranca obrigatorios
| Cenario | Resultado esperado |
|---------|-------------------|
| Tenant A acessa recurso de Tenant B | 403 Forbidden |
| Token expirado | 401 Unauthorized |
| SQL injection em campos de input | Input sanitizado, query segura |
| XSS em campos de texto | Output escapado |
| Brute force de autenticacao | Rate limited apos N tentativas |

---

## Observabilidade

### Logging
- Logs estruturados (JSON) com campos obrigatorios:
  - `timestamp`, `level`, `service`, `tenant_id`, `correlation_id`, `user_id`
- PII nunca em logs (mascarar antes de logar)
- Log levels: ERROR (incidentes), WARN (degradacao), INFO (operacoes), DEBUG (troubleshooting)

### Metricas
Metricas minimas a exportar:
- `request_duration_ms` (histograma, por endpoint e tenant)
- `request_count` (contador, por status code)
- `error_rate` (gauge, por servico)
- `active_users` (gauge, por tenant)
- Metricas de negocio especificas da feature

### Tracing
- Distributed tracing entre servicos (OpenTelemetry ou equivalente)
- `correlation_id` propagado em todos os requests
- Spans com `tenant_id` como atributo

### Alertas
| Condicao | Severidade | Acao |
|----------|-----------|------|
| Error rate > 1% por 5min | P1 | Paging on-call |
| Latencia p95 > 2x baseline por 10min | P2 | Notificacao Slack |
| Incidente de isolamento de tenant | P1 | Paging + rollback imediato |
| Disco/memoria > 85% | P3 | Notificacao |
