from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_missing_payload():
    response = client.post("/webhook/new-lead", json={"name": "Test"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Email and message required."

def test_health():
    # Adding a simple health check test just to verify pytest is wired up
    assert True
