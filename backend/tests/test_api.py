from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_and_chat_api() -> None:
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        response = client.post("/api/chat/wait", json={"message": "hello from api"})
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "completed"
        assert "LocalProvider processed" in body["response"]


def test_api_tools_and_memory() -> None:
    with TestClient(app) as client:
        assert client.get("/api/tools").status_code == 200
        assert client.get("/api/tools").json()[0]["config_path"].startswith("tools/")
        channels = client.get("/api/channels")
        assert channels.status_code == 200
        assert any(item["name"] == "telegram" and item["config_path"] == "channels/telegram.yaml" for item in channels.json())
        created = client.post("/api/memory", json={"content": "use qdrant for vector memory"}).json()
        assert created["id"].startswith("mem_")
        results = client.get("/api/memory/search?q=qdrant").json()
        assert len(results) >= 1


def test_admin_api_key_protects_control_plane(monkeypatch) -> None:
    monkeypatch.setenv("ADMIN_API_KEY", "test-secret")
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/api/tasks").status_code == 401
        assert client.get("/api/tasks", headers={"x-api-key": "test-secret"}).status_code == 200
