"""Persistent, auditable software engineering tasks."""
from __future__ import annotations
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from . import db
from .planner import make_plan, decoded
from .security import authorize

router = APIRouter(prefix='/api/tasks', tags=['tasks'], dependencies=[Depends(authorize)])

class TaskIn(BaseModel):
    project_id: str
    title: str = Field(min_length=3,max_length=120)
    instruction: str = Field(min_length=12,max_length=12000)

def get_task_or_404(task_id: str):
    task = db.one('SELECT * FROM tasks WHERE id=?', (task_id,))
    if not task:
        raise HTTPException(404, 'Task not found')
    return task

@router.get('')
def list_tasks(project_id: str | None = None):
    if project_id:
        return [decoded(x) for x in db.rows('SELECT * FROM tasks WHERE project_id=? ORDER BY created_at DESC', (project_id,))]
    return [decoded(x) for x in db.rows('SELECT * FROM tasks ORDER BY created_at DESC LIMIT 200')]

@router.post('', status_code=201)
def create_task(payload: TaskIn):
    project = db.one('SELECT * FROM projects WHERE id=?', (payload.project_id,))
    if not project:
        raise HTTPException(404, 'Project not found')
    identifier = db.uid()
    now = db.stamp()
    plan = json.dumps(make_plan(payload.instruction, project['stack']))
    db.execute('INSERT INTO tasks (id,project_id,title,instruction,status,plan,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)',
               (identifier,payload.project_id,payload.title.strip(),payload.instruction,'planned',plan,now,now))
    db.log('task_planned', f'Task planned: {payload.title}', identifier,payload.project_id)
    return decoded(get_task_or_404(identifier))

@router.get('/{task_id}')
def get_task(task_id: str):
    return decoded(get_task_or_404(task_id))

@router.post('/{task_id}/cancel')
def cancel_task(task_id: str):
    task = get_task_or_404(task_id)
    if task['status'] not in ('planned', 'awaiting_approval', 'failed'):
        raise HTTPException(409,'Task not cancellable from this state')
    db.execute("UPDATE tasks SET status='cancelled',updated_at=? WHERE id=?", (db.stamp(),task_id))
    db.log('task_cancelled','Task cancelled',task_id,task['project_id'])
    return decoded(get_task_or_404(task_id))
