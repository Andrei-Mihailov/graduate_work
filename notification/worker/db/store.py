from clickhouse_driver import Client
from core.settings import settings


class Store:
    """Класс для взаимодействия с хранилищем уведомлений."""

    def __init__(self) -> None:
        self.client = Client(host=settings.clickhouse_host)
        self.temp_storage = []

    def create_db_notification(self) -> None:
        self.client.execute(
            "CREATE DATABASE IF NOT EXISTS notification",
        )

    def create_table_notification(self) -> None:
        self.client.execute(
            "CREATE TABLE IF NOT EXISTS notification.regular_table "
            "(id String, status String, context String) Engine=MergeTree() ORDER BY id"
        )

    def init_db(self) -> None:
        self.create_db_notification()
        self.create_table_notification()

    def save_notification(self, data_message: dict[str, str]) -> None:
        if len(self.temp_storage) < 1000:
            self.temp_storage.append(
                data_message["id"], data_message["status"], data_message["context"]
            )
        else:
            """Сохранение уведомления в базу."""
            template_query: str = (
                "INSERT INTO notification.regular_table (id, status, context) VALUES"
            )
            self.client.execute(template_query, self.temp_storage)
            self.temp_storage = []
