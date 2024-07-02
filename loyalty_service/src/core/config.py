from pydantic import BaseModel
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str

    service_port: int
    service_host: str

    # Настройки postgres
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int

    # Настройки Redis
    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"

settings = Settings()

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