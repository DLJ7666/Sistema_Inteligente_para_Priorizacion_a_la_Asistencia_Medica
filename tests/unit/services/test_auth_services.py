import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.auth import AuthService


@patch("app.services.auth.supabase_client.auth.sign_in_with_password")
def test_authenticate_user_success(mock_sign_in):
    mock_response = MagicMock()
    mock_response.session.access_token = "fake_access_token_123"
    mock_sign_in.return_value = mock_response
    
    auth_service = AuthService(db=None)
    token = auth_service.authenticate_user("test@example.com", "password123")

    assert token.access_token == "fake_access_token_123"

@patch("app.services.auth.supabase_client.auth.sign_in_with_password")
def test_authenticate_user_invalid_credentials(mock_sign_in):
    mock_sign_in.side_effect = Exception("Auth error")

    auth_service = AuthService(db=None)
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate_user("wrong@example.com", "badpassword")
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Correo electrónico o contraseña incorrectos"

@patch("app.services.auth.supabase_client.auth.sign_in_with_password")
def test_authenticate_user_no_session(mock_sign_in):
    mock_response = MagicMock()
    mock_response.session = None
    mock_sign_in.return_value = mock_response

    auth_service = AuthService(db=None)
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate_user("test@example.com", "password123")
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Credenciales inválidas"
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"
