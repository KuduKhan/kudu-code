"""Control-plane authentication: fail closed unless local development is explicitly enabled."""
from __future__ import annotations
import hmac
import os
from fastapi import HTTPException, Request

def authorize(request: Request):
    secret=os.getenv('KUDU_CONTROL_TOKEN','')
    supplied=request.headers.get('authorization','')
    if secret:
        if not hmac.compare_digest(supplied,f'Bearer {secret}'):
            raise HTTPException(401,'Valid control token required')
        return
    # Development exception is OPT-IN and must not be used behind a reverse proxy.
    client=request.client.host if request.client else ''
    hostname=(request.url.hostname or '').lower()
    dev=os.getenv('KUDU_DEV_MODE')=='1'
    loopback=client in {'127.0.0.1','::1','testclient'} and hostname in {'localhost','127.0.0.1','::1','testserver'}
    forwarded=any(request.headers.get(h) for h in ('x-forwarded-for','x-forwarded-host','forwarded'))
    if not (dev and loopback and not forwarded):
        raise HTTPException(403,'API locked: configure KUDU_CONTROL_TOKEN; or explicitly opt in to loopback-only KUDU_DEV_MODE=1')
