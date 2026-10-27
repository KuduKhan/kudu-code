"""Inspectable task decomposition; deterministic fallback works offline."""
from __future__ import annotations
import json
from typing import Any

AGENTS = (
    ('architect','Architect', 'Design the requirements and architecture'),
    ('frontend','Frontend', 'Implement responsive accessible UI'),
    ('backend','Backend', 'Implement routes, services and business logic'),
    ('database','Database', 'Define schema and verify data policies'),
    ('devops','DevOps', 'Manage repositories, CI and environments'),
    ('qa','Quality', 'Implement and execute functional regression tests'),
    ('security','Security', 'Evaluate data access, inputs, and supply-chain risks'),
    ('review','Reviewer', 'Review diff and verify acceptance criteria'),
)

def make_plan(instruction: str, stack: str = '') -> list[dict[str, Any]]:
    text = instruction.lower()
    chosen = ['architect']
    if any(word in text for word in ('ui','ux','design','frontend','responsive','page','dashboard','site','css','layout')):
        chosen.append('frontend')
    if any(word in text for word in ('api','backend','server','auth','login','service','endpoint')):
        chosen.append('backend')
    if any(word in text for word in ('database','schema','sql','supabase','migration','query')):
        chosen.append('database')
    if any(word in text for word in ('github','deploy','vercel','pipeline','release','ci/cd')):
        chosen.append('devops')
    if len(chosen) == 1:
        chosen += ['frontend', 'backend']
    chosen += ['qa','security','review']
    return [
        {'id':i+1,'agent':ident,'title':label,'objective':objective,'state':'pending'}
        for i, (ident, label, objective) in enumerate(AGENTS) if ident in set(chosen)
    ]

def decoded(task: dict[str, Any]) -> dict[str, Any]:
    task['plan'] = json.loads(task.get('plan') or '[]')
    if task.get('proposal'):
        task['proposal'] = json.loads(task['proposal'])
    else:
        task['proposal'] = None
    return task
