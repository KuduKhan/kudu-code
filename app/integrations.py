"""Read-only connection diagnostics. Never return credentials to the browser."""
from __future__ import annotations
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from . import db
from .intelligence import model_ready
from .planner import AGENTS
from .toolchains import list_profiles
from .security import authorize

router = APIRouter(prefix='/api', dependencies=[Depends(authorize)],tags=['operations'])
CONNECTIONS = {
    'github': ('GITHUB_TOKEN','https://api.github.com/user', 'application/vnd.github+json'),
    'vercel': ('VERCEL_TOKEN','https://api.vercel.com/v2/user', None),
    'supabase': ('SUPABASE_ACCESS_TOKEN','https://api.supabase.com/v1/projects', None),
}

@router.get('/integrations')
def integrations():
    result = [{'name':name,'configured':bool(os.getenv(config[0])), 'mode':'read-only health check; scoped writes configured separately'} for name,config in CONNECTIONS.items()]
    result.append({'name':'openai','configured':model_ready(),'mode':'proposal generation; no tools or automatic execution'})
    return result

@router.get('/integrations/{provider}/check')
def check_integration(provider: str):
    if provider not in CONNECTIONS:
        raise HTTPException(404,'Unknown provider')
    env,url,accept=CONNECTIONS[provider]
    token=os.getenv(env,'')
    if not token:
        return {'provider':provider,'connected':False,'reason':'Credential not configured'}
    headers={'Authorization':f'Bearer {token}','Accept':accept or 'application/json'}
    try:
        result=httpx.get(url,headers=headers,timeout=8.0)
        return {'provider':provider, 'connected':result.is_success,
                'reason':'Authenticated' if result.is_success else f'Provider returned HTTP {result.status_code}'}
    except httpx.HTTPError:
        return {'provider':provider,'connected':False,'reason':'Provider check unavailable'}

@router.get('/events')
def recent_events(limit: int=40):
    limit=max(1,min(100,limit))
    return db.rows('SELECT * FROM events ORDER BY created_at DESC LIMIT ?', (limit,))

@router.get('/agents')
def list_agents():
    return [{'id':identifier,'name':label,'mission':purpose, 'execution':'policy-controlled'} for identifier,label,purpose in AGENTS]

@router.get('/toolchains')
def toolchains():
    return list_profiles()
