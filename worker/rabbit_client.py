import pika
import pika.channel

from settings import settings, NEW_USER_QUEUE, DELETE_USER_QUEUE


class RabbitMq:
    """Класс для взаимодействия с очередью сообщений."""

    def __init__(self) -> None:
        self.credentials = pika.PlainCredentials(settings.rabbit_user, settings.rabbit_password)
        self.connect = pika.SelectConnection(
            parameters=pika.ConnectionParameters(
                host=settings.rabbit_host,
                port=settings.rabbit_port,
                credentials=self.credentials,
            ),
            on_open_callback=self._on_open,
        )

    def run(self) -> None:
        try:
            self.connect.ioloop.start()
        except KeyboardInterrupt:
            self.connect.close()

    def _on_channel_open(self, channel: pika.channel.Channel) -> None:
        for queue in (NEW_USER_QUEUE, DELETE_USER_QUEUE):
            channel.exchange_declare(
                exchange="main", exchange_type="direct", durable=True, auto_delete=False
            )
            channel.basic_consume(queue=queue, on_message_callback=self._callback)

    def _on_open(self, connection: pika.SelectConnection) -> None:
        connection.channel(on_open_callback=self._on_channel_open)

    @staticmethod
    def _callback(channel: pika.channel.Channel, method, properties, body) -> None:
        print(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        