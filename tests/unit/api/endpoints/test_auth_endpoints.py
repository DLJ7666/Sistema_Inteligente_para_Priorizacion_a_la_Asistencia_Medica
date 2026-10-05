import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException, status

from app.main import app

client = TestClient(app)


@patch("app.services.auth.AuthService.authenticate_user")
def test_login_success(mock_authenticate):
    mock_authenticate.return_value = {"access_token": "valid_bearer_token", "token_type": "bearer"}

    payload = {
        "username": "medico@hospital.com",
        "password": "PasswordSegura123!"
    }
    response = client.post("api/v1/auth/token", data=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "valid_bearer_token"

@pytest.mark.parametrize("invalid_payload", [
    {},
    {"username": "test@example.com"},
    {"password": "secretpassword"},
    {"username": None, "password": "secretpassword"},
    {"username": "test@example.com", "password": None},
])
def test_login_invalid_input(invalid_payload):
    response = client.post("api/v1/auth/token", data=invalid_payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@patch("app.services.auth.AuthService.authenticate_user")
def test_login_unauthorized(mock_authenticate):
    mock_authenticate.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Correo electrónico o contraseña incorrectos"
    )

    payload = {
        "username": "medico@hospital.com",
        "password": "PasswordIncorrecta"
    }
    response = client.post("api/v1/auth/token", data=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Correo electrónico o contraseña incorrectos"