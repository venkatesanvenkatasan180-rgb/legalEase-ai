from fastapi.testclient import TestClient

from backend.main import app
from backend.dependencies import get_settings

client = TestClient(app)


def test_generate_in_demo_mode(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "demo_mode", True)

    payload = {
        "document_type": "Freelance Work Contract",
        "parties": "Jane Doe (Provider), TechNova Inc. (Client)",
        "terms": [
            "Payment within 30 days",
            "Confidentiality must be maintained",
        ],
        "effective_date": "September 24, 2026",
        "jurisdiction": "India",
        "additional_instructions": "",
    }

    response = client.post("/generate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["demo_mode"] is True
    assert "Freelance Work Contract" in data["text"]


def test_generate_validation():
    response = client.post(
        "/generate",
        json={
            "document_type": "",
            "parties": "",
            "effective_date": "",
        },
    )
    assert response.status_code == 422
