from fastapi import Depends
from functools import lru_cache
import sentry_sdk

from models.entity import Permissions
from .base_service import BaseService
from db.redis_db import RedisCache, get_redis
from db.postgres_db import AsyncSession, get_session


class PermissionService(BaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        super().__init__(cache, storage)
        self.model = Permissions

    async def create_permission(self, params: dict) -> Permissions:
        try:
            permission = await self.create_new_instance(params)
            return permission
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    async def assign_permission_to_role(self, data: dict) -> bool:
        try:
            role = await self.permission_to_role(
                str(data.get("permissions_id")), str(data.get("role_id"))
            )
            if role is not None:
                return True
            return False
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False

    async def remove_permission_from_role(self, data: dict) -> bool:
        try:
            return await self.permission_from_role(
                str(data.get("permissions_id")), str(data.get("role_id"))
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False


@lru_cache()
def get_permission_service(
    redis: RedisCache = Depends(get_redis),
    db: AsyncSession = Depends(get_session),
) -> PermissionService:
    return PermissionService(redis, db)
