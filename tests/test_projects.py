from fastapi.testclient import TestClient
from app.main import app

def test_project_creation_and_validation(tmp_path, monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH', str(tmp_path/'p.db'))
    with TestClient(app) as c:
        payload = {'name':'KUDU CODE', 'workspace':'kudu-code', 'repo_url':'https://github.com/KuduKhan/kudu-code', 'stack':'Python'}
        assert c.post('/api/projects',json=payload).status_code == 201
        assert c.post('/api/projects',json=payload).status_code == 409
        assert len(c.get('/api/projects').json()) == 1
        payload['workspace'] = '../bad'
        assert c.post('/api/projects',json=payload).status_code == 422
        payload['workspace'] = 'good-name'
        payload['repo_url'] = 'https://github.com.evil.test/KuduKhan/kudu-code'
        assert c.post('/api/projects',json=payload).status_code == 422
