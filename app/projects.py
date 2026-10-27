"""Project registry with explicit workspace scoping."""
from __future__ import annotations
import re
from urllib.parse import urlsplit
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from . import db
from .security import authorize

router = APIRouter(prefix='/api/projects', tags=['projects'], dependencies=[Depends(authorize)])
_SLUG = re.compile(r'^[a-z][a-z0-9-]{1,47}$')
_REPO = re.compile(r'^/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?$')

class ProjectIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    workspace: str = Field(min_length=2, max_length=48)
    repo_url: str = Field(default='', max_length=250)
    stack: str = Field(default='Unknown', max_length=80)

    @field_validator('workspace')
    @classmethod
    def valid_slug(cls, value: str):
        if not _SLUG.fullmatch(value):
            raise ValueError('Workspace must be a lowercase slug (2-48 characters)')
        return value

    @field_validator('repo_url')
    @classmethod
    def valid_repo(cls, value: str):
        if not value:
            return value
        parsed = urlsplit(value)
        if parsed.scheme != 'https' or parsed.netloc != 'github.com' or not _REPO.fullmatch(parsed.path) or parsed.query or parsed.fragment or parsed.username or parsed.password:
            raise ValueError('Only canonical https://github.com/owner/repo GitHub URLs are accepted')
        return value.rstrip('/')

@router.get('')
def list_projects():
    return db.rows('SELECT * FROM projects ORDER BY created_at DESC, name ASC')

@router.post('', status_code=201)
def create_project(item: ProjectIn):
    if db.one('SELECT id FROM projects WHERE workspace=?', (item.workspace,)):
        raise HTTPException(409, 'Workspace name already registered')
    identifier = db.uid()
    try:
        db.execute('INSERT INTO projects (id,name,workspace,repo_url,stack,created_at) VALUES (?,?,?,?,?,?)',
                   (identifier, item.name.strip(), item.workspace, item.repo_url, item.stack.strip(), db.stamp()))
    except Exception as exc:
        if 'UNIQUE' in str(exc):
            raise HTTPException(409, 'Workspace name already registered') from exc
        raise
    db.log('project_created', f'Project registered: {item.name}', project_id=identifier)
    return db.one('SELECT * FROM projects WHERE id=?', (identifier,))

@router.get('/{project_id}')
def get_project(project_id: str):
    result = db.one('SELECT * FROM projects WHERE id=?', (project_id,))
    if not result:
        raise HTTPException(404, 'Project not found')
    return result
