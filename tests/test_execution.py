from fastapi.testclient import TestClient
from app.main import app

def test_execution_requires_explicit_approval_and_proposal(tmp_path,monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH',str(tmp_path/'x.sqlite'))
    with TestClient(app) as c:
        p = c.post('/api/projects',json={'name':'Test Project','workspace':'execution-test'}).json()
        t = c.post('/api/tasks',json={'project_id':p['id'],'title':'Example change','instruction':'Please build an example service with unit tests'}).json()
        assert c.post(f"/api/tasks/{t['id']}/apply",json={'confirm':False}).status_code == 400
        assert c.post(f"/api/tasks/{t['id']}/apply",json={'confirm':True}).status_code == 409
        assert c.post(f"/api/tasks/{t['id']}/push",json={'confirm':True}).status_code == 409
