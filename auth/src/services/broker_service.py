from typing import Union
import orjson

from requests.exceptions import Timeout, ConnectionError
from aio_pika import RobustConnection, RobustChannel, RobustExchange, Message
from aio_pika.exceptions import AMQPConnectionError
from backoff import on_exception, expo

from core.config import settings
from models.broker import UserResponce


class BrokerService:
    def __init__(self):
        self.connection: Union[RobustConnection, None] = None
        self.channel: Union[RobustChannel, None] = None
        self.exchange: Union[RobustExchange, None] = None

    @on_exception(expo, (ConnectionError, Timeout, AMQPConnectionError), max_tries=10)
    async def send_message(self, queue_name: str, data: UserResponce):
        message = Message(
            body=orjson.dumps(data.model_dump()),
            delivery_mode=settings.rabbit_delivery_mode,
        )
        await self.exchange.publish(routing_key=queue_name, message=message)

    async def put_one_message_to_queue(self, event: str, user: UserResponce):
        await self.send_message(queue_name=event, data=user)


broker_service: BrokerService = BrokerService()


def get_broker_service() -> BrokerService:
    return broker_service
