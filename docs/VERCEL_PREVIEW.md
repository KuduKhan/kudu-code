# Vercel Preview Deployment — KUDU CODE

## Hosting mode
The Git repository exposes a separate **read-only showcase** in root `index.py`, selected by `pyproject.toml` (`[tool.vercel] entrypoint = "index:app"`).

The dashboard is rendered from `web/`. Mock API reads expose zero user projects/tasks, agent role descriptions, and disconnected provider statuses. Every POST/PUT/PATCH/DELETE is rejected with HTTP 405, and no filesystem/database/Git/secret execution capability is included in the hosted entrypoint.

**This is a UI and API preview, not the autonomous agent runtime.** The secured local control plane remains `app.main:app`. Never route the operator runtime to a public Vercel domain without replacing local SQLite, implementing durable job workers, and deploying identity-aware authorization.

## Deployment through the Vercel dashboard

1. Sign into the Vercel team **Mufasa Khan's projects**.
2. Open https://vercel.com/new and import GitHub repository `KuduKhan/kudu-code`.
3. Choose project name `kudu-code`, root directory `./`, framework **FastAPI**, and leave build/output overrides empty.
4. Keep Vercel's deployment protection enabled for previews if the design is private.
5. Deploy and inspect the preview build and function logs.
6. Verify `/`, `/api/health`, `/api/overview`, `/api/agents`, `/assets/preview.js`.
7. Verify POST `/api/projects` returns **405** (with no token or secrets).
8. Ensure `/api/health` returns `"preview":true` and `"read_only":true`.

No GitHub token, Vercel token, Supabase key, or AI model key is needed for this public read-only showcase. Do not configure production secrets.

## Release guardrails
Do not promote this app as production v1.0 autonomous engineering. Storage, real agent execution, provider writes, test execution, and task persistence are intentionally unavailable in this deployment.

## October 27, 2026 deployment attempt
Vercel project creation through the connected team API returned **403 Forbidden**. The repo source was committed, but a deployment URL cannot be confirmed until project creation is authorized from the Vercel team/dashboard.
