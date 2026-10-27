from fastapi.testclient import TestClient
from app.main import app

def test_api_is_closed_by_default(tmp_path,monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH',str(tmp_path/'locked.db'))
    monkeypatch.delenv('KUDU_CONTROL_TOKEN',raising=False)
    monkeypatch.delenv('KUDU_DEV_MODE',raising=False)
    with TestClient(app) as c:
        assert c.get('/api/overview').status_code==403

def test_dev_mode_rejects_forwarded_headers(tmp_path,monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH',str(tmp_path/'forwarded.db'))
    monkeypatch.delenv('KUDU_CONTROL_TOKEN',raising=False)
    with TestClient(app) as c:
        assert c.get('/api/overview').status_code==200
        assert c.get('/api/overview',headers={'X-Forwarded-For':'8.8.8.8'}).status_code==403
