from fastapi.testclient import TestClient
from app.main import app

def test_workspace_not_cloned(tmp_path,monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH',str(tmp_path/'x.sqlite'))
    monkeypatch.setenv('KUDU_WORKSPACE_ROOT',str(tmp_path/'sandbox'))
    with TestClient(app) as c:
        p = c.post('/api/projects',json={'name':'Minimal Project','workspace':'minimal'}).json()
        assert c.get(f"/api/projects/{p['id']}/repository").json()['cloned'] is False
        assert c.post(f"/api/projects/{p['id']}/clone").status_code == 400
