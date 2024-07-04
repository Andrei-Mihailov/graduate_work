from typing import Union
import orjson

from requests.exceptions import Timeout, ConnectionError
from aio_pika import RobustConnection, RobustChannel, RobustExchange, Message
from aio_pika.exceptions import AMQPConnectionError
from backoff import on_exception, expo

from core.config import settings
from models.models import ResponseModel, RequestEventModel, UserModel


class BrokerService:
    def __init__(self):
        self.connection: Union[RobustConnection, None] = None
        self.channel: Union[RobustChannel, None] = None
        self.exchange: Union[RobustExchange, None] = None

    @on_exception(expo, (ConnectionError, Timeout, AMQPConnectionError), max_tries=10)
    async def send_message(self, queue_name: str, data: ResponseModel):
        message = Message(
            body=orjson.dumps(data.model_dump()),
            delivery_mode=settings.rabbit_delivery_mode,
        )
        queue = await self.channel.declare_queue(name=queue_name, durable=True)
        await queue.bind(self.exchange)
        await self.exchange.publish(routing_key=queue_name, message=message)

    def create_message(event: RequestEventModel, user: UserModel):
        event.context["username"] = user.username
        return ResponseModel(event=event.event, email=user.email, context=event.context)

    async def put_one_message_to_queue(self, event: RequestEventModel, user: UserModel):
        data = self.create_message(event, user)
        await self.send_message(queue_name=f"email.{event.type_event}", data=data)

    async def put_many_message_to_queue(self, event: RequestEventModel, user_list: list[UserModel]):
        for user in user_list:
            data = self.create_message(event, user)
            await self.send_message(queue_name=f"email.{event.type_event}", data=data)


broker_service: BrokerService = BrokerService()


def get_broker_service() -> BrokerService:
    return broker_service
