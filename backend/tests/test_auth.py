from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.domain.auth import UserRole
from app.main import app
from app.repositories.users import InMemoryUserRepository, UserCredentialRecord
from app.security import AuthService, get_auth_service, password_hash

PASSWORD = "correct-horse-battery-staple"


@pytest.fixture
def auth_service() -> AuthService:
    users = [
        UserCredentialRecord(
            id="admin-id",
            email="admin@example.com",
            display_name="Admin",
            role=UserRole.ADMIN,
            password_hash=password_hash.hash(PASSWORD),
        ),
        UserCredentialRecord(
            id="director-id",
            email="director@example.com",
            display_name="Director",
            role=UserRole.COMMERCIAL_DIRECTOR,
            password_hash=password_hash.hash(PASSWORD),
        ),
        UserCredentialRecord(
            id="reviewer-id",
            email="reviewer@example.com",
            display_name="Trade Reviewer",
            role=UserRole.TRADE_MARKETING_REVIEWER,
            password_hash=password_hash.hash(PASSWORD),
        ),
    ]
    return AuthService(
        InMemoryUserRepository(users),
        Settings(secret_key="test-secret-key-that-is-long-enough"),
    )


@pytest.fixture
def client(auth_service: AuthService) -> Iterator[TestClient]:
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_auth_service, None)


def login(client: TestClient, email: str) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_unauthorized_access_is_rejected(client: TestClient) -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_invalid_credentials_are_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "incorrect-password"},
    )
    assert response.status_code == 401


def test_admin_route_enforces_role(client: TestClient) -> None:
    admin_response = client.get(
        "/api/auth/admin-access-check", headers=login(client, "admin@example.com")
    )
    director_response = client.get(
        "/api/auth/admin-access-check", headers=login(client, "director@example.com")
    )
    assert admin_response.status_code == 200
    assert director_response.status_code == 403


@pytest.mark.parametrize("email", ["director@example.com", "reviewer@example.com"])
def test_director_and_reviewer_flows_are_authorized(client: TestClient, email: str) -> None:
    response = client.get("/api/auth/reviewer-access-check", headers=login(client, email))
    assert response.status_code == 200
