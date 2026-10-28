"""Read-only KUDU CODE showcase for Vercel Functions.

This deliberately does not import or start the local operator control plane.
No SQLite writes, Git operations, token authentication, or sandbox execution
are exposed by this deployment. Use `uvicorn app.main:app` locally for the
approved operator workflow until a durable, authenticated backend exists.
"""
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Keep the hosted preview independent of the local operator modules.
# Only static role descriptions are exposed, with no agent execution.
AGENTS = (
    ("architect", "Architect", "Design the requirements and architecture"),
    ("frontend", "Frontend", "Implement responsive accessible UI"),
    ("backend", "Backend", "Implement routes, services and business logic"),
    ("database", "Database", "Define schema and verify data policies"),
    ("devops", "DevOps", "Manage repositories, CI and environments"),
    ("qa", "Quality", "Implement and execute functional regression tests"),
    ("security", "Security", "Evaluate data access, inputs, and supply-chain risks"),
    ("review", "Reviewer", "Review diff and verify acceptance criteria"),
)
ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
VERSION = "1.0.0-preview"
app = FastAPI(title="KUDU CODE — Read-only Preview", version=VERSION, docs_url=None, redoc_url=None, openapi_url=None)
# Never crash at cold-start just because static files were omitted from a bundle.
# Missing static files are observable via /api/health rather than an import-time 500.
if WEB.is_dir():
    app.mount("/assets", StaticFiles(directory=str(WEB)), name="assets")

@app.middleware("http")
async def secure_preview(request: Request, call_next):
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        response = JSONResponse({"detail": "Read-only Vercel preview: changes are disabled."}, status_code=405)
    else:
        response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "style-src-attr 'unsafe-inline'; connect-src 'self'; "
        "img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    )
    return response

@app.get("/")
def homepage():
    page = WEB / "index.html"
    if not page.is_file():
        return HTMLResponse(
            "<!doctype html><title>KUDU CODE preview unavailable</title>"
            "<h1>Preview assets unavailable</h1>"
            "<p>The deployment does not contain web/index.html. "
            "Check the Vercel build output and redeploy the complete repository.</p>",
            status_code=503,
        )
    return FileResponse(page)

@app.get("/api/health")
def health():
    return {"status": "ok" if (WEB / "index.html").is_file() else "degraded",
            "service": "KUDU CODE", "version": VERSION, "preview": True,
            "read_only": True, "assets_available": (WEB / "index.html").is_file()}

@app.get("/api/overview")
def overview():
    return {"projects": 0, "tasks": 0, "active": 0, "completed": 0,
            "version": VERSION, "preview": True, "read_only": True}

@app.get("/api/projects")
def projects():
    return []

@app.get("/api/tasks")
def tasks():
    return []

@app.get("/api/agents")
def agents():
    return [{"id": slug, "name": label, "mission": purpose, "execution": "not active in hosted preview"}
            for slug, label, purpose in AGENTS]

@app.get("/api/events")
def events():
    return []

@app.get("/api/integrations")
def integrations():
    return [{"name": name, "configured": False,
             "mode": "Not connected in read-only Vercel preview"}
            for name in ("github", "vercel", "supabase", "openai")]

@app.get("/api/integrations/{provider}/check")
def check_provider(provider: str):
    if provider not in {"github", "vercel", "supabase"}:
        raise HTTPException(404, "Unknown provider")
    return {"provider": provider, "connected": False,
            "reason": "External services are disabled in the hosted preview"}

@app.get("/api/toolchains")
def toolchains():
    return []

@app.get("/api/{path:path}")
def disabled_endpoint(path: str):
    raise HTTPException(404, "Endpoint unavailable in the read-only Vercel preview")
