from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_valid_request():
    response = client.post("/api/chat", json={"message": "how do i vote?"})
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "response" in data
    assert "confidence" in data

def test_chat_empty_request():
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422  # Pydantic validation error

def test_chat_missing_field():
    response = client.post("/api/chat", json={})
    assert response.status_code == 422
