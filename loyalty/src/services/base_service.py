import backoff
import sentry_sdk

from typing import List
from abc import ABC
from sqlalchemy.exc import DBAPIError
from fastapi.encoders import jsonable_encoder
from sqlalchemy.future import select
from asyncpg.exceptions import PostgresConnectionError as conn_err_pg

from db.redis_db import RedisCache
from db.postgres_db import AsyncSession


class AbstractBaseService(ABC):
    pass


class BaseService(AbstractBaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        self.cache = cache
        self.storage = storage
        self.model = None

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def create_new_instance(self, model_params):
        if not isinstance(model_params, dict):
            models_dto = jsonable_encoder(model_params)
        else:
            models_dto = model_params
        instance = self.model(**models_dto)
        self.storage.add(instance)
        try:
            await self.storage.commit()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None
        await self.storage.refresh(instance)
        return instance

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def get_instance_by_id(self, id: str):
        stmt = select(self.model).filter(self.model.id == id)
        try:
            result = await self.storage.execute(stmt)
            instance = result.scalars().first()
            return instance
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def get_instance_by_code(self, code: str):
        stmt = select(self.model).filter(self.model.code == code)
        try:
            result = await self.storage.execute(stmt)
            instance = result.scalars().first()
            return instance
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def del_instance_by_id(self, id: str) -> bool:
        try:
            instance = await self.get_instance_by_id(id)
            if instance:
                await self.storage.delete(instance)
                await self.storage.commit()
                return True
            else:
                return False
        except DBAPIError as e:
            sentry_sdk.capture_exception(e)
            raise e
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False

    async def set_cache(self, cache_key: str, cache_value: dict) -> None:
        await self.cache.set(cache_key, jsonable_encoder(cache_value))

    async def get_cache(self, cache_key: str):
        return await self.cache.redis.get(cache_key)

    async def cache_active_instances(self, instances: List):
        for instance in instances:
            await self.set_cache(f"{self.model.__name__.lower()}:{instance.id}", instance)
