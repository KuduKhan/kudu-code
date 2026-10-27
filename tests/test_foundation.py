from fastapi.testclient import TestClient
from app.main import app

def test_health(tmp_path, monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH', str(tmp_path/'test.sqlite3'))
    with TestClient(app) as client:
        assert client.get('/api/health').json()['status'] == 'ok'
        assert client.get('/api/overview').json()['projects'] == 0
