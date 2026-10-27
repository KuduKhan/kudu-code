import hashlib
import json
import subprocess
from fastapi.testclient import TestClient
from app import db
from app.main import app


def git(*args,cwd):
    return subprocess.run(['git',*args],cwd=cwd,check=True,capture_output=True,text=True).stdout.strip()


def test_approved_change_creates_feature_commit(tmp_path,monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH',str(tmp_path/'workflow.db'))
    monkeypatch.setenv('KUDU_WORKSPACE_ROOT',str(tmp_path/'workspace'))
    with TestClient(app) as c:
        project=c.post('/api/projects',json={'name':'Test Project','workspace':'test-project'}).json()
        root=tmp_path/'workspace'/'test-project'
        root.mkdir(parents=True)
        git('init','-b','main',cwd=root)
        git('config','user.name','Test Operator',cwd=root)
        git('config','user.email','test@example.org',cwd=root)
        (root/'README.md').write_text('# Project')
        git('add','README.md',cwd=root)
        git('commit','-m','initial',cwd=root)
        task=c.post('/api/tasks',json={'title':'Implement simple feature','project_id':project['id'],'instruction':'Build a Python function and test its expected behavior'}).json()
        proposal={'summary':'Create a hello module','verification':['Run syntax check'],
                  'files':[{'path':'hello.py','content':'def hello():\n    return "world"\n',
                            'new':True,'baseline_sha256':hashlib.sha256(b'').hexdigest()}]}
        db.execute('UPDATE tasks SET status=?, proposal=? WHERE id=?',('awaiting_approval',json.dumps(proposal),task['id']))
        result=c.post(f"/api/tasks/{task['id']}/apply",json={'confirm':True})
        assert result.status_code==200,result.text
        assert result.json()['status']=='implemented'
        assert git('branch','--show-current',cwd=root).startswith('kudu/task-')
        assert 'world' in (root/'hello.py').read_text()
        assert git('status','--porcelain',cwd=root)==''
        assert c.get(f"/api/tasks/{task['id']}").json()['status']=='implemented'
