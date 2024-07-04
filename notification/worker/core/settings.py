import os

from enum import Enum
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    login: str = Field(..., env="LOGIN")
    password: str = Field(..., env="PASSWORD")
    domain: str = Field(..., env="DOMAIN")
    smtp_host: str = Field(..., env="SMTP_HOST")
    smtp_port: str = Field(..., env="SMTP_PORT")
    ampq_url: str = Field(..., env="AMQP_URL")
    api_key_email: str = Field(..., env="API_KEY_EMAIL")
    clickhouse_host: str = Field(..., env="CLICKHOUSE_HOST")
    rm_user: str = Field(..., env="RABBIT_USER")
    rm_password: str = Field(..., env="RABBIT_PASSWORD")
    rabbit_host: str = Field(..., env="RABBIT_HOST")
    rabbit_port: int = Field(..., env="RABBIT_PORT")
    sender_name: str = Field(..., env="SENDER_NAME")
    sender_email: str = Field(..., env="SENDER_EMAIL")

    class Config:
        env_file = ".env"


TEMPLATES_DIR = "../templates/"
EVENT_TO_TEMPLATE = {
    "registration": os.path.join(TEMPLATES_DIR, "mail.html"),
    "new_films": os.path.join(TEMPLATES_DIR, "new_film.html"),
}

settings = Settings()


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"


SEND_WELCOME_QUEUE: str = "email.send_welcome"
NEW_FILMS_QUEUE: str = "email.new_films"
