# KUDU CODE v1.0.0-preview — 27 October 2026

**Release channel:** Developer preview. Milestone 1.0 is the completion of the local preview control-plane build, NOT realization of the complete autonomous engineering vision.

## Delivered

- Responsive dark engineering dashboard, project/task views and operator dialogs.
- API for projects, tasks, events, agent catalog and integration diagnostics.
- SQLite persistence, task planning and read-only code context.
- Optional OpenAI Responses API file proposal workflow.
- Explicit human gate before file modification, Git commits and GitHub branch pushes.
- Scope-limited GitHub repository cloning and pull request creation.
- Isolated Docker syntax verification for Python and JavaScript; fail-closed when Docker is unavailable.
- End-to-end test of task approval through Git feature branch commit.
- CI with pytest, Node syntax validation, Python compilation.
- Local commit history from v0.1 through v1.0 preview.

## Not delivered / still planned

- True concurrent multi-agent execution with independent role-specific LLM sessions.
- A durable distributed orchestration engine, ephemeral VM compute workers, RBAC and multi-tenant tenancy.
- Native Supabase database schema write operations and Vercel deployment controls.
- Broad language/toolchain support, full automated unit/E2E/security test orchestration and browser agent.
- Full end-to-end real provider validation, safe production deployment/rollback, autonomous maintenance.

## Acceptance gates

Automated local test suite: run `python -m pytest -q`.
JavaScript validity: run `node --check web/app.js`.
Interface: inspected at 1390px desktop and 390px mobile in a sandboxed Chromium layout test. Functional cloud integrations require provider credentials and remote environment access.

Any future GA (general availability) designation requires separate security and operational validation.
