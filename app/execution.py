"""Governed file application and isolated, read-only Docker verification."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from . import db
from .security import authorize
from .tasks import get_task_or_404
from .workspace import project_path, inspect_repo, safe_path, _git

router = APIRouter(prefix='/api/tasks', dependencies=[Depends(authorize)], tags=['execution'])

class Approval(BaseModel):
    confirm: bool

class VerifyRequest(BaseModel):
    command: str = Field(default='python-syntax', pattern=r'^python-syntax$')

class PushRequest(BaseModel):
    confirm: bool

def _context(task_id: str):
    task = get_task_or_404(task_id)
    project = db.one('SELECT * FROM projects WHERE id=?',(task['project_id'],))
    return task,project,project_path(project['workspace'])

@router.post('/{task_id}/apply')
def apply_proposal(task_id: str, approval: Approval):
    if not approval.confirm:
        raise HTTPException(400,'Explicit confirmation required')
    task,project,root = _context(task_id)
    if task['status']!='awaiting_approval' or not task['proposal']:
        raise HTTPException(409,'Task is not awaiting file approval')
    if inspect_repo(root)['dirty']:
        raise HTTPException(409,'Workspace has uncommitted changes; resolve them first')
    proposal = json.loads(task['proposal'])
    files = proposal['files']
    if not files: raise HTTPException(409,'Empty proposal')
    destinations=[]
    for file in files:
        path = safe_path(root,file['path'])
        old = path.read_bytes() if path.exists() else b''
        if hashlib.sha256(old).hexdigest() != file['baseline_sha256']:
            raise HTTPException(409,f"File changed since proposal: {file['path']}")
        destinations.append((path,file['path'],file['content']))
    branch = 'kudu/task-' + task_id.split('-')[0]
    _git(['switch','-c',branch],root)
    try:
        for path,relative,content in destinations:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding='utf-8')
        _git(['add','--',*[rel for _,rel,_ in destinations]],root)
        _git(['-c','user.name=KUDU CODE','-c','user.email=engineering@users.noreply.github.com',
              'commit','-m',f"feat: {task['title'][:70]}"],root)
    except Exception:
        # Preserve files and branch for operator inspection; never silently erase work.
        db.execute("UPDATE tasks SET status='failed',result=?,branch=?,updated_at=? WHERE id=?",
                   ('Changes require manual inspection; Git commit failed',branch,db.stamp(),task_id))
        raise
    db.execute("UPDATE tasks SET status='implemented',branch=?,result=?,updated_at=? WHERE id=?",
               (branch, f'Committed {len(destinations)} approved file(s); verification pending',db.stamp(),task_id))
    db.log('files_applied',f'Approved changes committed to {branch}',task_id,project['id'])
    return {'status':'implemented','branch':branch,'files':[rel for _,rel,_ in destinations]}

@router.post('/{task_id}/verify')
def verify_task(task_id: str, request: VerifyRequest):
    task,project,root = _context(task_id)
    if task['status'] not in ('implemented','verification_failed'):
        raise HTTPException(409,'Task must be committed before verification')
    inspect_repo(root)
    pyfiles = sorted(x for x in root.rglob('*.py') if '.git' not in x.parts and not x.is_symlink())
    if not pyfiles:
        raise HTTPException(422,'No Python files; configure a suitable language-specific runner')
    image = os.getenv('KUDU_DOCKER_IMAGE','python:3.13-slim')
    if not image.startswith('python:') or len(image)>60 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-_' for c in image):
        raise HTTPException(500,'Invalid Docker verification image setting')
    program = "import ast,pathlib; files=list(pathlib.Path('/code').rglob('*.py')); [ast.parse(p.read_text(encoding='utf-8'),filename=str(p)) for p in files]; print(f'{len(files)} Python files parsed')"
    cmd = ['docker','run','--rm','--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges',
           '--pids-limit=64','--memory=512m','--cpus=1','--user=65534:65534',
           '--mount',f'type=bind,src={root},dst=/code,readonly', '--tmpfs','/tmp:rw,noexec,nosuid,size=32m',
           image,'python','-c',program]
    try:
        completed = subprocess.run(cmd, capture_output=True,text=True,timeout=100)
    except (FileNotFoundError,subprocess.TimeoutExpired) as exc:
        raise HTTPException(503,'Docker unavailable or verification timed out; no host execution fallback') from exc
    passed=completed.returncode==0
    status='verified' if passed else 'verification_failed'
    output=(completed.stdout+'\n'+completed.stderr)[-2500:]
    db.execute('UPDATE tasks SET status=?,result=?,updated_at=? WHERE id=?',(status,output,db.stamp(),task_id))
    db.log('verification', f'Isolated syntax verification: {status}',task_id,project['id'])
    return {'status':status,'passed':passed,'output':output,'scope':'Python syntax only; not a full functional or security test'}

@router.post('/{task_id}/push')
def push_branch(task_id: str, request: PushRequest):
    if not request.confirm:
        raise HTTPException(400,'Explicit push confirmation required')
    task,project,root = _context(task_id)
    if task['status']!='verified':
        raise HTTPException(409,'Isolated verification required before branch push')
    if not project['repo_url']:
        raise HTTPException(409,'GitHub repository not configured')
    if inspect_repo(root)['dirty']:
        raise HTTPException(409,'Workspace dirty; refusing push')
    if _git(['remote','get-url','origin'],root).rstrip('/') != project['repo_url'].rstrip('/'):
        raise HTTPException(409,'Git remote differs from registered repository')
    if _git(['branch','--show-current'],root) != task['branch']:
        raise HTTPException(409,'Current branch differs from task branch')
    if not task['branch'].startswith('kudu/task-'):
        raise HTTPException(403,'Only task branches may be pushed')
    _git(['push','origin',f"{task['branch']}:{task['branch']}"],root,timeout=90)
    db.execute("UPDATE tasks SET status='completed',result=?,updated_at=? WHERE id=?",
               ('Branch pushed successfully; PR/release approval still required',db.stamp(),task_id))
    db.log('branch_pushed',f"Branch pushed: {task['branch']}",task_id,project['id'])
    return {'status':'completed','branch':task['branch'], 'note':'Branch only; no main-branch merge or production deploy'}
