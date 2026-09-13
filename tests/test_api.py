from fastapi.testclient import TestClient

from eval_platform.api import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_evaluate_and_feedback_flow() -> None:
    response = client.post(
        "/evaluate",
        json={
            "cases": [
                {
                    "id": "api-1",
                    "prompt": "Explain a reset link.",
                    "reference": "A reset link verifies a password change request.",
                }
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["case_count"] == 1
    run_id = payload["id"]

    feedback = client.post(
        "/feedback",
        json={
            "run_id": run_id,
            "case_id": "api-1",
            "label": "accept",
            "rating": 4,
            "notes": "Useful baseline response.",
        },
    )

    assert feedback.status_code == 200
    assert client.get(f"/feedback?run_id={run_id}").json()[0]["label"] == "accept"