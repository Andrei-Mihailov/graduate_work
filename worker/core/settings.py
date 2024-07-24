from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rabbit_user: str = Field(..., env="RABBIT_USER")
    rabbit_password: str = Field(..., env="RABBIT_PASSWORD")
    rabbit_host: str = Field(..., env="RABBIT_HOST")
    rabbit_port: int = Field(..., env="RABBIT_PORT")

    db_name: str = Field("postgres", env="DB_NAME")
    db_user: str = Field("app", env="POSTGRES_USER")
    db_password: str = Field("123qwe", env="POSTGRES_PASSWORD")
    db_host: str = Field("notifications_db", env="POSTGRES_HOST")
    db_port: int = Field(5432, env="POSTGRES_PORT")
    echo_db: bool = Field(False, env="ECHO_DB")
    
    class Config:
        env_file = ".env"

    @property
    def db_connection(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()

NEW_USER_QUEUE: str = "users.registration"
DELETE_USER_QUEUE: str = "users.delete"
