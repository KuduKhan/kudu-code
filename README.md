# KUDU CODE

**Autonomous engineering control plane** — an inspectable, self-hostable project and agent task manager.

KUDU CODE is being built with a secure-by-default local dashboard, persistent project/task history, a provider-backed planning and change proposal workflow, code review and opt-in sandbox testing. It does **not** have unrestricted production access or claim generated features are automatically validated.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000. For remote use, set a strong `KUDU_CONTROL_TOKEN` and put the service behind TLS, an identity-aware reverse proxy, and rate limits. The bearer token must not be distributed to other users.

## Security model

- `KUDU_CONTROL_TOKEN` required for non-loopback API access.
- No hard-coded credentials or secrets in repository.
- No automatic GitHub pushes, main merges, production releases or database migration writes.
- AI-generated files always require explicit approval.
- Docker-only untrusted tests; fail closed when Docker is unavailable.
- Restrict access to trusted users; this is a single-operator preview, not a multi-tenant SaaS.

See [Architecture](docs/ARCHITECTURE.md) and [Roadmap](docs/ROADMAP.md).
