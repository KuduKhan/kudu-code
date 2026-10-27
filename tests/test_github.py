from fastapi.testclient import TestClient
from app.github import coordinates
from app.main import app

def test_repo_coordinates():
    assert coordinates('https://github.com/KuduKhan/kudu-code.git')==['KuduKhan','kudu-code']

def test_pr_requires_pushed_branch(tmp_path,monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH',str(tmp_path/'pr.db'))
    with TestClient(app) as c:
        p=c.post('/api/projects',json={'name':'Working Project','workspace':'workproject','repo_url':'https://github.com/KuduKhan/kudu-code'}).json()
        t=c.post('/api/tasks',json={'project_id':p['id'],'title':'New feature','instruction':'Implement a feature with full testing'}).json()
        assert c.post(f"/api/tasks/{t['id']}/pull-request",json={'confirm':False}).status_code==400
        assert c.post(f"/api/tasks/{t['id']}/pull-request",json={'confirm':True}).status_code==409
