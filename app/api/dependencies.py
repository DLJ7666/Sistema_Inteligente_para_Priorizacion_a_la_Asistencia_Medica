from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import Client, create_client

from app.core.config import settings
from app.schemas.auth import SupabaseUser

client: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.POSTGRES_ANON_KEY
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token"
)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> SupabaseUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de autenticación",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token.startswith(("Bearer ", "bearer ")):
        token = token.split(" ")[1].strip()
    try:
        user_response = client.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise credentials_exception

        user = user_response.user
    except Exception as e:
        print(f"❌ Error al validar token con Supabase: {e}", flush=True)
        raise credentials_exception

    return SupabaseUser(
            id=user.id,
            email=user.email,
            role=user.role
        )