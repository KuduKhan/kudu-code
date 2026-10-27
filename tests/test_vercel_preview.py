"""Contract tests for the isolated Vercel read-only showcase."""
from fastapi.testclient import TestClient
from index import app

client = TestClient(app)


def test_preview_dashboard_and_health():
    page = client.get("/")
    assert page.status_code == 200
    assert "KUDU CODE" in page.text
    assert 'src="/assets/preview.js"' in page.text

    status = client.get("/api/health")
    assert status.status_code == 200
    assert status.json()["read_only"] is True
    assert status.json()["preview"] is True


def test_preview_api_has_no_persistent_or_live_data():
    overview = client.get("/api/overview")
    assert overview.status_code == 200
    assert overview.json()["projects"] == 0
    assert overview.json()["tasks"] == 0
    assert client.get("/api/projects").json() == []
    assert client.get("/api/tasks").json() == []
    assert client.get("/api/events").json() == []
    assert len(client.get("/api/agents").json()) >= 1
    assert all(not item["configured"] for item in client.get("/api/integrations").json())


def test_every_mutation_is_blocked():
    for path in ("/api/projects", "/api/tasks", "/api/tasks/example/apply", "/api/tasks/example/push"):
        response = client.post(path, json={"confirm": True})
        assert response.status_code == 405
        assert "Read-only" in response.json()["detail"]
    assert client.delete("/api/projects/example").status_code == 405


def test_hosted_preview_rejects_control_plane_endpoints():
    assert client.get("/api/projects/private").status_code == 404
    assert client.get("/api/tasks/private").status_code == 404
    assert client.get("/docs").status_code == 404


def test_security_headers_and_static_files():
    response = client.get("/")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert client.get("/assets/preview.js").status_code == 200
    assert client.get("/assets/preview.css").status_code == 200
