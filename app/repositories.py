"""Explicit repository checkout, inspect and branch management."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from . import db
from .security import authorize
from .workspace import project_path, clone_repository, inspect_repo

router = APIRouter(prefix='/api/projects', tags=['repositories'], dependencies=[Depends(authorize)])

@router.post('/{project_id}/clone')
def clone_project(project_id: str):
    project = db.one('SELECT * FROM projects WHERE id=?',(project_id,))
    if not project: raise HTTPException(404,'Project not found')
    root = clone_repository(project['repo_url'], project['workspace'])
    info = inspect_repo(root)
    db.log('repository_cloned', 'Repository cloned into scoped workspace', project_id=project_id)
    return {'workspace': project['workspace'], **info}

@router.get('/{project_id}/repository')
def repository_status(project_id: str):
    project = db.one('SELECT * FROM projects WHERE id=?',(project_id,))
    if not project: raise HTTPException(404,'Project not found')
    root = project_path(project['workspace'])
    if not (root/'.git').exists():
        return {'cloned':False,'workspace':project['workspace']}
    return {'cloned':True,'workspace':project['workspace'], **inspect_repo(root)}
