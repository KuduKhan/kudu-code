from fastapi.testclient import TestClient
from app.main import app

def test_task_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH',str(tmp_path/'tasks.db'))
    with TestClient(app) as c:
        p = c.post('/api/projects',json={'name':'Test Project','workspace':'test-project'}).json()
        t = c.post('/api/tasks',json={'title':'Build dashboard','project_id':p['id'],'instruction':'Build a responsive dashboard with tests and a backend API'}).json()
        assert t['status'] == 'planned'
        assert any(x['agent']=='qa' for x in t['plan'])
        assert c.get(f"/api/tasks/{t['id']}").json()['id'] == t['id']
        assert c.post(f"/api/tasks/{t['id']}/cancel").json()['status'] == 'cancelled'
        assert c.post(f"/api/tasks/{t['id']}/cancel").status_code == 409
