import os

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


class AuthJWT(BaseModel):
    secret_key: str = "secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 20 * 60
    refresh_token_expire_minutes: int = 30 * 24 * 60 * 60  # 30 дней


class Settings(BaseSettings):

    # Настройки postgres
    db_name: str = Field("", env="DB_NAME")
    db_user: str = Field("", env="DB_USER")
    db_password: str = Field("", env="DB_PASSWORD")
    db_host: str = Field("", env="DB_HOST")
    db_port: int = Field(5321, env="DB_PORT")

    # Настройки Redis
    redis_host: str
    redis_port: int

    # Настройки jwt
    auth_jwt: AuthJWT = AuthJWT()
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")

    # Настройки Sentry
    sentry_sdk_dns: str
    sentry_traces_sample_rate: float
    sentry_profiles_sample_rate: float

    class Config:
        env_file = ".env.example"
        case_sensitive = False


settings = Settings()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PostgreSQLConfig(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: int


pg_config_data = PostgreSQLConfig(
    dbname=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
)
