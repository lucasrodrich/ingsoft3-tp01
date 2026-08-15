import os
os.environ["JWT_SECRET"] = "test-secret-with-enough-entropy"
os.environ["DATABASE_URL"] = "sqlite:///./restaurant_test.db"
os.environ["APP_TIMEZONE"] = "America/Argentina/Cordoba"

import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def register(client):
    def create(email="a@example.com", nombre="Usuario A", password="password123"):
        response = client.post("/api/auth/register", json={"nombre": nombre, "email": email, "password": password})
        assert response.status_code == 201, response.text
        data = response.json()
        return data, {"Authorization": f"Bearer {data['token']}"}
    return create

