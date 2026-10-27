from __future__ import annotations
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from . import db
from .security import authorize
from .settings import VERSION

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.initialize()
    yield

app = FastAPI(title='KUDU CODE', version=VERSION, lifespan=lifespan, docs_url=None, redoc_url=None)
app.mount('/assets', StaticFiles(directory=str(Path(__file__).resolve().parent.parent/'web')), name='assets')

@app.middleware('http')
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; style-src-attr 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    return response

@app.get('/')
def homepage():
    return FileResponse(Path(__file__).resolve().parent.parent/'web/index.html')

@app.get('/api/health')
def health():
    return {'status':'ok', 'service':'KUDU CODE', 'version':VERSION}

@app.get('/api/overview', dependencies=[Depends(authorize)])
def overview():
    project_count = db.one('SELECT COUNT(*) AS n FROM projects')['n']
    task_count = db.one('SELECT COUNT(*) AS n FROM tasks')['n']
    active = db.one("SELECT COUNT(*) AS n FROM tasks WHERE status IN ('queued','planned','awaiting_approval','running')")['n']
    complete = db.one("SELECT COUNT(*) AS n FROM tasks WHERE status='completed'")['n']
    return {'projects': project_count, 'tasks': task_count, 'active': active, 'completed': complete, 'version': VERSION}

from .projects import router as projects_router
app.include_router(projects_router)
from .tasks import router as tasks_router
app.include_router(tasks_router)
from .proposals import router as proposals_router
app.include_router(proposals_router)
from .repositories import router as repo_router
app.include_router(repo_router)
from .execution import router as execution_router
app.include_router(execution_router)
from .integrations import router as integrations_router
app.include_router(integrations_router)
from .github import router as github_router
app.include_router(github_router)
