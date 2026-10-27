from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

def test_dashboard_assets(tmp_path, monkeypatch):
    monkeypatch.setenv('KUDU_DATABASE_PATH',str(tmp_path/'site.db'))
    with TestClient(app) as c:
        assert 'KUDU CODE' in c.get('/').text
        assert 'font-family' in c.get('/assets/styles.css').text
        assert 'function render()' in c.get('/assets/app.js').text
        assert "default-src 'self'" in c.get('/').headers['content-security-policy']

def test_js_syntax():
    import subprocess
    root=Path(__file__).resolve().parents[1]
    p=subprocess.run(['node','--check',str(root/'web/app.js')],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
