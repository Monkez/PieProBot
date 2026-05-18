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
        channels = client.get("/api/channels")
        assert channels.status_code == 200
        assert any(item["name"] == "telegram" for item in channels.json())
        created = client.post("/api/memory", json={"content": "use qdrant for vector memory"}).json()
        assert created["id"].startswith("mem_")
        results = client.get("/api/memory/search?q=qdrant").json()
        assert len(results) >= 1
