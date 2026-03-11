import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_page():
    # Проверяем, что страница логина доступна (код 200)
    response = client.get("/login")
    assert response.status_code == 300
    assert "Вход" in response.text