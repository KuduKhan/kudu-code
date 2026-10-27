# Architecture

KUDU CODE operates as a single-operator modular control plane.

- **Web:** responsive HTML/CSS/JS served from FastAPI, bearer API auth for remote deployments.
- **API:** Pydantic-validated endpoints; project/task lifecycle; strict state transitions.
- **Persistence:** SQLite (development). Migrate to managed PostgreSQL before horizontal scale.
- **Intelligence:** optional external Responses API; plans and JSON file proposals; no uncontrolled tool calls.
- **Workspace:** one directory per registered repository; validated names and GitHub HTTPS origins.
- **Execution:** opt-in Docker subprocess with network disabled and resource limits.
- **Governance:** explicit write approvals; sensitive actions disabled until independently authorized.

For a production-scale architecture, replace synchronous operations with a durable workflow engine and per-task ephemeral VM worker; put UI and API behind OIDC and least-privilege authorization; use structured secret management, outgoing-network egress controls, central audit storage, and per-user quotas.
