from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = Field("notification_service", env="PROJECT_NAME")
    service_host: str = Field("127.0.0.1", env="NS_HOST")
    service_port: int = Field(8080, env="NS_PORT")

    db_name: str = Field("postgres", env="DB_NAME")
    db_user: str = Field("app", env="POSTGRES_USER")
    db_password: str = Field("123qwe", env="POSTGRES_PASSWORD")
    db_host: str = Field("notifications_db", env="POSTGRES_HOST")
    db_port: int = Field(5432, env="POSTGRES_PORT")
    echo_db: bool = Field(False, env="ECHO_DB")

    rabbit_host: str = Field("rabbitmq", env="RABBITMQ_HOST")
    rabbit_port: int = Field(5672, env="RABBITMQ_PORT")
    rabbit_user: str = Field("rmuser", env="RABBITMQ_USER")
    rabbit_password: str = Field("rmpassword", env="RABBITMQ_PASSWORD")
    rabbit_delivery_mode: int = Field(2, env="RABBITMQ_DELIVERY_MODE")
    rabbit_exchange: str = Field("main", env="RABBITMQ_EXCHANGE")

    class Config:
        env_file = "./envs/.env"

    @property
    def db_connection(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def rabbit_connection(self):
        return f"amqp://{self.rabbit_user}:{self.rabbit_password}@{self.rabbit_host}/"


settings = Settings()
