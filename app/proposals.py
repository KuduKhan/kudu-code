"""Model-generated changes remain reviewable until an operator approves them."""
from __future__ import annotations
import json
from fastapi import APIRouter, Depends, HTTPException
from . import db
from .intelligence import propose
from .security import authorize
from .tasks import get_task_or_404
from .workspace import project_path, source_context, validate_proposal

router = APIRouter(prefix='/api/tasks', dependencies=[Depends(authorize)], tags=['proposals'])

@router.post('/{task_id}/propose')
def create_proposal(task_id: str):
    task = get_task_or_404(task_id)
    if task['status'] not in ('planned', 'failed'):
        raise HTTPException(409,'Task must be planned before generating changes')
    project = db.one('SELECT * FROM projects WHERE id=?', (task['project_id'],))
    root = project_path(project['workspace'])
    # The model reads a bounded subset of non-secret, tracked source files.
    plan = json.loads(task['plan'])
    proposal = propose(task['instruction'], source_context(root), plan)
    verified = validate_proposal(root,proposal)
    if not verified:
        raise HTTPException(422,'Model returned no proposed files; refine the instruction')
    proposal = {'summary':str(proposal.get('summary',''))[:4000],
                'files':verified, 'verification':proposal.get('verification',[])[:12] if isinstance(proposal.get('verification'),list) else []}
    db.execute("UPDATE tasks SET proposal=?,status='awaiting_approval',updated_at=? WHERE id=?",(json.dumps(proposal),db.stamp(),task_id))
    db.log('proposal_ready',f'{len(verified)} proposed files awaiting approval',task_id,task['project_id'])
    return {'task_id':task_id,'status':'awaiting_approval','proposal':proposal}
