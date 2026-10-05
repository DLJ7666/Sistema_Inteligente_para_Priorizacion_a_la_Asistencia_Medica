from fastapi import HTTPException, status
from supabase import create_client, Client

from app.core.config import settings
from app.schemas.auth import Token


supabase_client: Client = create_client(settings.SUPABASE_URL, settings.POSTGRES_ANON_KEY)

class AuthService:
    def __init__(self, db):
        self.client = supabase_client

    def authenticate_user(self, email: str, password: str):
        credenciales_invalidas = "Credenciales inválidas"
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=credenciales_invalidas,
                )

            return Token(
                access_token=response.session.access_token
            )

        except Exception as e:
            if hasattr(e, 'detail') and e.detail == credenciales_invalidas:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=credenciales_invalidas,
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Correo electrónico o contraseña incorrectos",
                    headers={"WWW-Authenticate": "Bearer"},
                )