"""Git and workspace operations: no user-supplied executable shell snippets."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path, PurePosixPath
import subprocess
from fastapi import HTTPException
from .settings import workspace_root

BLOCKED_NAMES = {'.env', '.git', '.npmrc', '.pypirc', '.ssh', 'id_rsa', 'id_ed25519', '.aws', '.kube', 'credentials.json', 'secrets.json', 'secret.json'}
ALLOWED_SUFFIXES = {'.py','.ts','.tsx','.js','.jsx','.json','.md','.html','.css','.scss','.sql','.toml','.yaml','.yml','.txt','.sh','.go','.rs','.java','.kt','.swift','.dart','.vue','.svelte','.xml'}

def project_path(slug: str) -> Path:
    root = workspace_root()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not slug or not slug.isascii() or not all(ch in 'abcdefghijklmnopqrstuvwxyz0123456789-' for ch in slug):
        raise HTTPException(400,'Invalid workspace')
    path = root / slug
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise HTTPException(403,'Workspace escapes configured root')
    return path

def safe_path(root: Path, raw: str) -> Path:
    if not isinstance(raw,str) or len(raw)>240 or '\\' in raw or '\x00' in raw:
        raise HTTPException(400,'Invalid file path')
    p = PurePosixPath(raw)
    if p.is_absolute() or '..' in p.parts or not p.parts or any(part.startswith('.') or part.lower() in BLOCKED_NAMES for part in p.parts) or p.suffix.lower() not in ALLOWED_SUFFIXES:
        raise HTTPException(400,'File path forbidden by policy')
    dest = root.joinpath(*p.parts)
    if not dest.resolve().is_relative_to(root.resolve()) or any(x.is_symlink() for x in (dest, *dest.parents) if x != root.parent):
        raise HTTPException(403,'Symlink path forbidden')
    return dest

def _git(args: list[str], cwd: Path, timeout: int=30):
    try:
        p = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c','protocol.file.allow=never', *args],
                           cwd=str(cwd), text=True, capture_output=True, timeout=timeout,
                           env={**os.environ, 'GIT_TERMINAL_PROMPT':'0', 'GIT_OPTIONAL_LOCKS':'0'})
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise HTTPException(502, 'Git command unavailable or timed out') from exc
    if p.returncode:
        raise HTTPException(409, f'Git operation failed: {p.stderr[-550:]}')
    return p.stdout.strip()

def clone_repository(repo_url: str, slug: str):
    if not repo_url:
        raise HTTPException(400,'Project has no GitHub URL')
    root = project_path(slug)
    if root.exists():
        raise HTTPException(409,'Workspace exists; import is not allowed to overwrite it')
    root.mkdir(mode=0o700)
    try:
        _git(['clone','--depth','1','--no-checkout','--',repo_url,str(root)],root.parent,timeout=90)
        _git(['checkout','--force','HEAD'],root)
    except Exception:
        # Never remove a workspace after partial clone; inspection is required.
        raise
    return root

def inspect_repo(root: Path) -> dict:
    if not root.is_dir() or not (root/'.git').exists():
        raise HTTPException(409, 'Clone repository into this workspace before proposing code')
    status = _git(['status','--porcelain'],root)
    return {'branch':_git(['branch','--show-current'],root), 'dirty':bool(status), 'files':len(_git(['ls-files'],root).splitlines())}

def source_context(root: Path, limit: int=37000):
    inspect_repo(root)
    names = _git(['ls-files'],root).splitlines()
    chunks, used = [], 0
    for name in names:
        try:
            path = safe_path(root,name)
            if not path.is_file() or path.stat().st_size>14000: continue
            data = path.read_text('utf-8')
            if len(data)>14000: continue
            if used + len(data) > limit: break
            chunks.append(f'### {name}\n{data}')
            used += len(data)
        except (UnicodeError,OSError,HTTPException):
            continue
    return '\n\n'.join(chunks)

def validate_proposal(root: Path, proposal: dict) -> list[dict]:
    files = proposal.get('files',[])
    if not isinstance(files,list) or len(files)>12:
        raise HTTPException(422,'Too many proposed files')
    checked, seen = [], set()
    for f in files:
        if not isinstance(f,dict) or not isinstance(f.get('content'),str) or len(f['content'])>80000:
            raise HTTPException(422,'Invalid proposed file')
        name = f.get('path')
        path = safe_path(root,name)
        if name in seen: raise HTTPException(422,'Duplicate path in proposal')
        seen.add(name)
        old = path.read_bytes() if path.exists() else b''
        checked.append({'path':name,'content':f['content'],'baseline_sha256':hashlib.sha256(old).hexdigest(), 'new':not path.exists()})
    return checked
