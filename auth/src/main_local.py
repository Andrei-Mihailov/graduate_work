import uvicorn
import click
import sys
import asyncio

import functools as ft
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from core.config import settings
from db import postgres_db
from db import redis_db
from api.v1.service import check_jwt
from api.v1 import users, roles, permissions


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_db.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    yield
    await redis_db.redis.close()


app = FastAPI(
    lifespan=lifespan,
    title="Сервис авторизации",
    description="Реализует методы идентификации, аутентификации, авторизации",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


def async_cmd(func):
    @ft.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


@click.command()
@click.option(
    '--email',
    default='test',
    prompt='Enter email',
    help='email for the superuser')
@click.option(
    '--password',
    default='test',
    prompt='Enter password',
    help='Password for the superuser')
@async_cmd
async def create_superuser(email, password):
    from models.entity import User
    from sqlalchemy.future import select
    async with postgres_db.async_session() as session:
        result = await session.execute(select(User).filter(User.email == email))
        existing_user = result.scalars().first()
        if existing_user:
            click.echo('User with this email already exists!')
            return

        # Создаем суперпользователя
        superuser_data = {
            "email": email,
            "password": password,
            "is_superuser": True
        }
        instance = User(**superuser_data)
        session.add(instance)
        try:
            await session.commit()
        except Exception as e:
            print(f"Ошибка при создании объекта: {e}")
            return None

        click.echo(f'Superuser {email} created successfully!')


app.include_router(users.router, prefix="/api/v1/users")
app.include_router(
    roles.router, prefix="/api/v1/roles", dependencies=[Depends(check_jwt)]
)
app.include_router(
    permissions.router, prefix="/api/v1/permissions", dependencies=[Depends(check_jwt)]
)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        create_superuser()
    else:
        uvicorn.run(app, host='0.0.0.0', port=8080)
