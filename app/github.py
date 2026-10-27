"""GitHub PR operations; scoped to explicitly registered repository and task branch."""
from __future__ import annotations
import os
from urllib.parse import urlsplit
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from . import db
from .security import authorize
from .tasks import get_task_or_404

router=APIRouter(prefix='/api/tasks',dependencies=[Depends(authorize)],tags=['github'])

class CreatePR(BaseModel):
    confirm: bool

def coordinates(url: str):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.netloc!='github.com':
        raise HTTPException(400,'GitHub URL required')
    parts=parsed.path.rstrip('/').removesuffix('.git').strip('/').split('/')
    if len(parts)!=2 or any(not p or '..' in p for p in parts):
        raise HTTPException(400,'Invalid GitHub repository')
    return parts

@router.post('/{task_id}/pull-request')
def create_pull_request(task_id: str,approval: CreatePR):
    if not approval.confirm: raise HTTPException(400,'Explicit PR authorization required')
    task=get_task_or_404(task_id)
    if task['status']!='completed': raise HTTPException(409,'Push a verified task branch before opening a PR')
    if task['pr_url']: return {'pull_request_url':task['pr_url'],'already_created':True}
    project=db.one('SELECT * FROM projects WHERE id=?',(task['project_id'],))
    if not project or not project['repo_url']: raise HTTPException(409,'Project has no repository')
    token=os.getenv('GITHUB_TOKEN')
    if not token: raise HTTPException(503,'GITHUB_TOKEN not configured')
    owner,repo=coordinates(project['repo_url'])
    headers={'Authorization':f'Bearer {token}', 'Accept':'application/vnd.github+json', 'X-GitHub-Api-Version':'2022-11-28'}
    try:
        response=httpx.get(f'https://api.github.com/repos/{owner}/{repo}',headers=headers,timeout=12)
        response.raise_for_status()
        default_branch=response.json()['default_branch']
        if default_branch==task['branch']: raise HTTPException(409,'Task branch cannot be the base')
        detail={'title':task['title'], 'head':task['branch'],'base':default_branch,
                'body':f"## KUDU CODE engineering proposal\n\n{task['title']}\n\nThis branch contains approved, committed code changes. A scoped syntax check ran successfully. **Human code review, comprehensive testing, and release approval are still required.**\n"}
        made=httpx.post(f'https://api.github.com/repos/{owner}/{repo}/pulls',headers=headers,json=detail,timeout=15)
        made.raise_for_status()
        pr_url=made.json().get('html_url','')
        if urlsplit(pr_url).netloc!='github.com':raise HTTPException(502,'GitHub returned an invalid PR URL')
    except (httpx.HTTPError,KeyError,ValueError) as exc:
        raise HTTPException(502,'GitHub pull request operation failed; inspect provider access and branch status') from exc
    db.execute('UPDATE tasks SET pr_url=?,updated_at=? WHERE id=?',(pr_url,db.stamp(),task_id))
    db.log('pull_request_created',f'Pull request created for task branch {task["branch"]}',task_id,project['id'])
    return {'pull_request_url':pr_url,'already_created':False}
