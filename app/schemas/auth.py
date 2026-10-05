from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SupabaseUser(BaseModel):
    id: str
    email: str | None = None
    role: str | None = None