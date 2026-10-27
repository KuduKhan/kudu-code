"""Explicit language verifiers: no model-selected arbitrary shell execution."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
from fastapi import HTTPException
from .workspace import safe_path

PROFILES = {
  'python-syntax': {
    'language':'Python','image':'python:3.13-slim', 'suffixes':('.py',),
    'command':['python','-c',"import ast,pathlib; files=[p for p in pathlib.Path('/code').rglob('*.py') if '.git' not in p.parts and 'node_modules' not in p.parts]; [ast.parse(p.read_text(encoding='utf8'),filename=str(p)) for p in files]; print(f'{len(files)} Python files parsed')"],
    'scope':'Python parsing only; no unit tests or security validation'},
  'javascript-syntax': {
    'language':'JavaScript','image':'node:22-alpine','suffixes':('.js','.mjs','.cjs'),
    'command':['node','-e',"const fs=require('fs'),cp=require('child_process'),p=require('path');let n=0;function visit(d){for(const x of fs.readdirSync(d,{withFileTypes:true})){if(['node_modules','.git','.next'].includes(x.name))continue;const q=p.join(d,x.name);if(x.isDirectory())visit(q);else if(x.isFile()&&/\\.(js|mjs|cjs)$/.test(x.name)){cp.execFileSync(process.execPath,['--check',q],{stdio:'pipe'});n++}}};visit('/code');console.log(n+' JavaScript files parsed')"],
    'scope':'JavaScript syntax only; no integration tests or security validation'},
}

def list_profiles():
    return [{'id':name,'language':v['language'],'scope':v['scope']} for name,v in PROFILES.items()]

def run_verification(root: Path,profile: str):
    if profile not in PROFILES: raise HTTPException(422,'Unknown verification profile')
    entry = PROFILES[profile]
    # Do not follow symlinks in the tree; never mount directories containing links out of workspace.
    for path in root.rglob('*'):
        if path.is_symlink(): raise HTTPException(409,'Workspace contains symlinks; inspect before sandbox verification')
    files=[p for p in root.rglob('*') if p.is_file() and p.suffix in entry['suffixes'] and '.git' not in p.parts and 'node_modules' not in p.parts]
    if not files: raise HTTPException(422,'No matching files for selected language verification profile')
    args = ['docker','run','--rm','--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges',
            '--pids-limit=64','--memory=512m','--cpus=1','--user=65534:65534',
            '--mount',f'type=bind,src={root},dst=/code,readonly','--tmpfs','/tmp:rw,noexec,nosuid,size=32m',
            entry['image'],*entry['command']]
    try:
        result=subprocess.run(args,capture_output=True,text=True,timeout=90)
    except (FileNotFoundError,subprocess.TimeoutExpired) as exc:
        raise HTTPException(503,'Docker unavailable or timed out; refusing unsafe host fallback') from exc
    return {'passed':result.returncode==0,'output':(result.stdout+'\n'+result.stderr)[-2500:],'scope':entry['scope']}
