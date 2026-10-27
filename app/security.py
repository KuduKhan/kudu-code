"""Default local-only control API; production requires an explicit bearer token."""
from __future__ import annotations
import hmac
import os
from fastapi import HTTPException, Request

def authorize(request: Request):
    secret = os.getenv('KUDU_CONTROL_TOKEN', '')
    supplied = request.headers.get('authorization', '')
    if secret:
        if not hmac.compare_digest(supplied, f'Bearer {secret}'):
            raise HTTPException(401, 'Valid control token required')
        return
    host = request.client.host if request.client else ''
    if host not in {'127.0.0.1', '::1', 'testclient'}:
        raise HTTPException(403, 'Remote access disabled; set KUDU_CONTROL_TOKEN')
