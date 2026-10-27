from fastapi.testclient import TestClient
from app.main import app

def test_integrations_are_secrets_free(tmp_path,monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH',str(tmp_path/'i.db'))
    monkeypatch.setenv('GITHUB_TOKEN','super-secret-test-value')
    with TestClient(app) as c:
        providers = c.get('/api/integrations').json()
        assert next(x for x in providers if x['name']=='github')['configured']
        assert 'super-secret-test-value' not in str(providers)
        assert len(c.get('/api/agents').json()) >= 5
        assert isinstance(c.get('/api/events').json(),list)
        assert c.get('/api/integrations/random/check').status_code==404

def test_auth_token(tmp_path,monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH',str(tmp_path/'auth.db'))
    monkeypatch.setenv('KUDU_CONTROL_TOKEN','test-secret')
    with TestClient(app) as c:
        assert c.get('/api/overview').status_code == 401
        assert c.get('/api/overview', headers={'Authorization':'Bearer test-secret'}).status_code == 200
