from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_correlation_id_and_task_logs_are_queryable() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/chat/wait",
            json={"message": "write task logs"},
            headers={"x-correlation-id": "corr_test_observability"},
        )
        assert response.headers["x-correlation-id"] == "corr_test_observability"
        task_id = response.json()["task_id"]

        all_logs = client.get("/logs?correlation_id=corr_test_observability").json()["logs"]
        assert any(row["logger"] == "api.request" for row in all_logs)

        task_logs = client.get(f"/logs/tasks/{task_id}").json()["logs"]
        assert any(row.get("task_id") == task_id for row in task_logs)

