# Threat model and release gates

## Trust boundaries

1. User instructions, GitHub sources, and model output are untrusted inputs.
2. Provider credentials belong in server-side environment / secrets manager, never repository or browser source.
3. Source content given to a model is bounded and heuristically scrubbed; **redaction is not comprehensive**. Audit repositories before enabling external models.
4. Generated file content must be reviewed before approval. No instructions from repository files grant new permissions.
5. Git push affects only a `kudu/task-*` branch; PR creation is a separate approval gate.
6. Docker verification explicitly disables network, adds runtime limits and runs as non-root. Docker hosts and base image must be separately secured.
7. A successful language parser check is not equivalent to functional tests, security audit, or release approval.

## Before production

- Implement multi-user SSO/OIDC and per-repository RBAC.
- Replace single-process synchronous tasks with durable queue and isolated VM workers.
- Add idempotency keys, conflict-free concurrent task control, job cancel/retry and timeouts.
- Add comprehensive tests per project technology, checked before GitHub merge.
- Integrate branch protection/rulesets and approvals at GitHub provider level.
- Apply secret scanning and DLP to AI context and stored proposals.
- Encrypt proposal data, centralize immutable audit logs and managed backups.
- Pin and scan dependency/container versions; use least-privilege repository installation tokens.
- Configure TLS, network segmentation, Docker socket isolation and resource budgets.
- Add privacy retention policy, telemetry scrubbing, policy-enforced cost limits, operational SLOs.
- Enable safe staged production releases and rollback only under distinct authorization.

**Security posture:** Single-operator developer preview. NOT production-hardened, not multitenant, not fully autonomous, and not ready to connect to privileged production accounts by default.
