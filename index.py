"""Read-only KUDU CODE showcase for Vercel Functions.

This deliberately does not import or start the local operator control plane.
No SQLite writes, Git operations, token authentication, or sandbox execution
are exposed by this deployment. Use `uvicorn app.main:app` locally for the
approved operator workflow until a durable, authenticated backend exists.
"""
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.planner import AGENTS

ROOT = Path(__file__).resolve().parent
VERSION = "1.0.0-preview"
app = FastAPI(title="KUDU CODE — Read-only Preview", version=VERSION, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/assets", StaticFiles(directory=str(ROOT / "web")), name="assets")

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
    return FileResponse(ROOT / "web" / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "KUDU CODE", "version": VERSION, "preview": True, "read_only": True}

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
