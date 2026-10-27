# KUDU CODE v1.0 Preview — release gate

The repository currently identifies itself as `1.0.0-preview`. This is **not** a production-ready autonomous engineering agent.

## Verified architecture (source inspection)

- FastAPI API and responsive static web control center.
- SQLite-based project/task persistence.
- Optional model-assisted planning and proposed changes.
- Workspace/repository integrations, approval-gated execution, and read-only provider integrations.
- CI runs pytest, JavaScript syntax validation and Python compilation.

## Required before production v1.0

- [ ] Validate CI results for the exact release commit.
- [ ] Run authenticated API, authorization-boundary and secret-handling tests.
- [ ] Prove isolated execution against malicious repositories; test sandbox escape and egress controls.
- [ ] Replace single-operator bearer-token assumptions with per-user identities, RBAC and auditability.
- [ ] Introduce durable job execution with retry, cancellation, idempotency and crash recovery.
- [ ] Add least-privilege GitHub App credentials and verify branch/PR/merge policies.
- [ ] Implement Vercel preview integration with staging and explicit production release approval.
- [ ] Implement scoped Supabase integration with migration review, RLS checks and backup/rollback planning.
- [ ] Test task-to-PR workflow end-to-end with real authorized test repositories.
- [ ] Validate responsive behavior, accessibility, error recovery and operator documentation.

## Release rule

Do not mark production v1.0 complete until every mandatory gate has test evidence. Never treat a version string, generated source file, or successful API response as proof of feature completion. Production writes, database migrations, merges and deployments must remain approval-controlled.

## Next implementation slice

Start with durable jobs and comprehensive execution-policy tests, then implement GitHub App PR automation in an isolated test repository. Integrate Vercel previews and development-scoped Supabase only after those gates pass.
