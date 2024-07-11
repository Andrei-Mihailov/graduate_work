import logging

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Kafka
    KAFKA_TOPIC: str = Field("events", env="KAFKA_TOPIC")
    KAFKA_HOST: str = Field("localhost", env="KAFKA_HOST")
    KAFKA_PORT: int = Field(9092, env="KAFKA_PORT")
    KAFKA_GROUP: str = Field("echo-messages", env="KAFKA_GROUP")
    CONSUMER_TIMEOUT_MS: int = Field(100, env="CONSUMER_TIMEOUT_MS")
    MAX_RECORDS_PER_CONSUMER: int = Field(100, env="MAX_RECORDS_PER_CONSUMER")
    NUM_PARTITIONS: int = Field(1, env="NUM_PARTITIONS")
    REPLICATION_FACTOR: int = Field(1, env="REPLICATION_FACTOR")
    JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY", default="secret-key")
    MAX_TRIES: int = Field(env="MAX_TRIES", default=5)
    DEBUG: bool = Field(env="DEBUG", default=True)

    AUTH_API_ME_URL: str = Field(
        "http://auth_service:8000/auth/api/v1/users/me", env="AUTH_API_ME_URL"
    )

    # Настройки postgres
    db_name: str = Field("", env="DB_NAME")
    db_user: str = Field("", env="DB_USER")
    db_password: str = Field("", env="DB_PASSWORD")
    db_host: str = Field("", env="DB_HOST")
    db_port: int = Field(5321, env="DB_PORT")

    class Config:
        env_file = ".env.example"
        case_sensitive = False


settings = Settings()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
