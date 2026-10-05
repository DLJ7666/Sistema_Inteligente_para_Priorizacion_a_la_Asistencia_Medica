from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

class Settings(BaseSettings):
    PROJECT_NAME: str = "SIPAM API"
    VERSION: str = "1.0.0"
    ENTORNO: str
    API_V1_STR: str = "/api/v1"
    
    SUPABASE_JWT_SECRET: str
    ALGORITHM: str
    
    POSTGRES_SERVER: str
    SUPABASE_URL: str
    POSTGRES_ANON_KEY: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return URL.create(
            drivername="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=int(self.POSTGRES_PORT),
            database=self.POSTGRES_DB,
        )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()