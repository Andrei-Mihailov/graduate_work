from typing import Union, Optional, List

import backoff
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as conn_err_redis

from .cache import Cache


class RedisCache(Cache):
    def __init__(self):
        self.redis: Union[Redis, None]

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def get(self, key: str) -> Optional[bytes]:
        data = await self.redis.get(key)
        if not data:
            return None
        return data

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def set(self, key: str, value: Union[str, int, bytes], expire: Optional[int] = None):
        await self.redis.set(key, value)
        if expire:
            await self.redis.expire(key, expire)

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def delete(self, key: str):
        await self.redis.delete(key)

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def set_promocode(self, code: str, promocode_id: int, expire: Optional[int] = None):
        await self.set(code, promocode_id, expire=expire)

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def get_promocode(self, code: str) -> Optional[int]:
        result = await self.get(code)
        if result is None:
            return None
        return int(result)

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def delete_promocode(self, code: str):
        await self.delete(code)

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def cache_active_promocodes(self, promocodes: List[int], expire: Optional[int] = None):
        """
        Кэширует список активных промокодов.
        Each promocode is stored in the format: 'promocode_id' -> promocode details.
        """
        for promocode in promocodes:
            await self.set(f"promocode:{promocode.id}", promocode, expire)

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def get_all_active_promocodes(self) -> List[Optional[int]]:
        """
        Получает все активные промокоды из кэша.
        Возвращает список идентификаторов промокодов.
        """
        keys = await self.redis.keys("promocode:*")
        values = await self.redis.mget(keys)
        return [int(value) for value in values if value is not None]

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def update_promocode_usage(self, promocode_id: int):
        """
        Обновляет количество использований промокода.
        Например, может уменьшать счетчик использований или выполнять другие действия.
        """
        key = f"promocode_usage:{promocode_id}"
        usage_count = await self.redis.incr(key)  # Увеличиваем счетчик использований
        return usage_count  # Возврат текущего значения счетчика

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def cancel_promocode_usage(self, promocode_id: int):
        """
        Отменяет использование промокода, сбрасывая его счетчик использований.
        """
        key = f"promocode_usage:{promocode_id}"
        await self.redis.delete(key)  # Удаляем счетчик использований


redis: Union[RedisCache, None] = None


async def get_redis() -> RedisCache:
    return redis
