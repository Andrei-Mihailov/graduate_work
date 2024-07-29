import multiprocessing
import gunicorn.app.base
import click
import asyncio
import functools as ft
import sys

import sentry_sdk
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from contextlib import asynccontextmanager
from aio_pika import connect_robust
from aio_pika.exceptions import AMQPConnectionError
from backoff import on_exception, expo

from api.v1 import users, roles, permissions
from db import postgres_db
from db import redis_db
from core.config import settings
from api.v1.service import check_jwt
from services.broker_service import broker_service
from models.broker import EventType


@on_exception(expo, (AMQPConnectionError, ConnectionError), max_tries=10)
@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_db.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    broker_service.connection = await connect_robust(settings.rabbit_connection)
    broker_service.channel = await broker_service.connection.channel()
    broker_service.exchange = await broker_service.channel.declare_exchange(settings.rabbit_exchange, durable=True)
    for queue_name in EventType:
        queue = await broker_service.channel.declare_queue(name=queue_name.value, durable=True)
        await queue.bind(broker_service.exchange)
    yield
    await redis_db.redis.close()
    await broker_service.channel.close()
    await broker_service.connection.close()


app = FastAPI(
    lifespan=lifespan,
    title="Сервис авторизации",
    description="Реализует методы идентификации, аутентификации, авторизации",
    docs_url="/auth/api/openapi",
    openapi_url="/auth/api/openapi.json",
    default_response_class=ORJSONResponse,
)

sentry_sdk.init(
    dsn=settings.sentry_sdk_dns,
    traces_sample_rate=settings.sentry_traces_sample_rate,
    profiles_sample_rate=settings.sentry_profiles_sample_rate,
)


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


app.include_router(users.router, prefix="/auth/api/v1/users")
app.include_router(
    roles.router, prefix="/auth/api/v1/roles", dependencies=[Depends(check_jwt)]
)
app.include_router(
    permissions.router, prefix="/auth/api/v1/permissions", dependencies=[Depends(check_jwt)]
)


def async_cmd(func):
    @ft.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.command()
@click.option(
    "--email",
    default="test",
    prompt="Enter email",
    help="email for the superuser",
)
@click.option(
    "--password",
    default="test",
    prompt="Enter password",
    help="Password for the superuser",
)
@async_cmd
async def create_superuser(email, password):
    from models.entity import User
    from sqlalchemy.future import select

    async with postgres_db.async_session() as session:
        result = await session.execute(select(User).filter(User.email == email))
        existing_user = result.scalars().first()
        if existing_user:
            click.echo("User with this email already exists!")
            return

        # Создаем суперпользователя
        superuser_data = {
            "email": email,
            "password": password,
            "is_staff": True,
            "active": True,
            "is_superuser": True,
            "first_name": "superuser",
            "last_name": "superuser"
        }
        instance = User(**superuser_data)
        session.add(instance)
        try:
            await session.commit()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            click.echo("Error creating object")
            return None
        sentry_sdk.capture_message(f"Superuser {email} created successfully!")
        click.echo(f"Superuser {email} created successfully!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_superuser()
    else:
        options = {
            "bind": "%s:%s" % ("0.0.0.0", settings.service_port),
            "workers": number_of_workers(),
            "worker_class": "uvicorn.workers.UvicornWorker",
        }

        StandaloneApplication(app, options).run()
