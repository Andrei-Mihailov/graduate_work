import logging
from typing import Union, Any

from pydantic import Field
from pydantic_settings import BaseSettings
from clickhouse_driver import Client
from kafka3 import KafkaConsumer
from requests.exceptions import ConnectionError
from backoff import on_exception, expo


class Settings(BaseSettings):
    # ClickHouse
    CH_HOST: str = Field("localhost", env="CH_HOST")
    CH_PORT: int = Field(8123, env="CH_PORT")
    CH_USER: str = Field("localhost", env="CH_USER")
    CH_PASSWORD: str = Field(8123, env="CH_PASSWORD")
    CH_DATABASE: str = Field("movies_analysis", env="CH_DATABASE")
    # Kafka
    KAFKA_TOPIC: str = Field("events", env="KAFKA_TOPIC")
    KAFKA_HOST: str = Field("localhost", env="KAFKA_HOST")
    KAFKA_PORT: int = Field(9092, env="KAFKA_PORT")
    KAFKA_GROUP: str = Field("echo-messages", env="KAFKA_GROUP")
    CONSUMER_TIMEOUT_MS: int = Field(100, env="CONSUMER_TIMEOUT_MS")
    MAX_RECORDS_PER_BATCH: int = Field(100, env="MAX_RECORDS_PER_BATCH")
    MAX_TRIES: int = Field(10, env="MAX_TRIES")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

logger = logging.getLogger(__name__)


class Clickhouse:
    def __init__(self) -> None:
        self.clickhouse_connect: Union[Client, None]

    @on_exception(expo, (ConnectionError), max_tries=5)
    def execute_query(self, query: str, data: Union[Any, None]):
        if self.clickhouse_connect is not None:
            self.clickhouse_connect.execute(query, data)
        else:
            raise ConnectionError("Clickhouse client is not connected")


class Kafka:
    def __init__(self) -> None:
        self.kafka_connect: Union[KafkaConsumer, None]


ch = Clickhouse()
kafka = Kafka()
