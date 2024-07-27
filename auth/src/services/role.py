from uuid import UUID
from functools import lru_cache
from typing import Union

from fastapi import Depends
import sentry_sdk

from .base_service import BaseService
from core.constains import DEFAULT_ROLE_DATA
from models.entity import Roles
from models.user import User
from db.postgres_db import AsyncSession, get_session
from db.redis_db import RedisCache, get_redis


class RoleService(BaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        super().__init__(cache, storage)
        self.model = Roles

    async def get(self, role_id: UUID) -> Union[Roles, None]:
        """Получить роль."""
        try:
            return await self.get_instance_by_id(role_id)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    async def get_by_name(self, role_name: str) -> Union[Roles, None]:
        """Получить роль по названию."""
        try:
            return await self.get_instance_by_name(role_name)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    async def create(self, role_data: dict) -> Roles:
        """Создание роли."""
        try:
            return await self.create_new_instance(role_data)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    async def update(self, role_id: str, update_data: dict) -> Roles:
        try:
            return await self.change_instance_data(role_id, update_data)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    async def delete(self, role_id: str) -> Roles:
        """Удаление роли."""
        try:
            return await self.del_instance_by_id(role_id)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    async def elements(self):
        try:
            return await self.get_all_instance()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return []

    async def assign_role(self, user_id: str, role_id: str) -> User:
        try:
            return await self.set_user_role(user_id, role_id)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    async def deassign_role(self, user_id: str) -> User:
        try:
            return await self.del_user_role(user_id)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    async def get_default_role(self) -> Roles:
        try:
            if not (default_role := await self.get_by_name(DEFAULT_ROLE_DATA["name"])):
                default_role = await self.create(DEFAULT_ROLE_DATA)
            return default_role
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None

    async def revoke_role(self, role: Roles, user: User) -> User:
        """Отзыв роли у пользователя."""
        try:
            return await self.del_user_role(user)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None


@lru_cache()
def get_role_service(
    redis: RedisCache = Depends(get_redis),
    db: AsyncSession = Depends(get_session),
) -> RoleService:
    return RoleService(redis, db)
