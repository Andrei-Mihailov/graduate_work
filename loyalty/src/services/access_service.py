from http import HTTPStatus
from fastapi import Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.promocode import AvailableForUsers
from .base_service import BaseService
from db.database import get_db
from db.redis_db import RedisCache, get_redis


class AccessService(BaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        super().__init__(cache, storage)
        self.model = AvailableForUsers

    async def is_promocode_available_for_user(self, promocode_id: int, user_id: int, group_id: int) -> bool:
        user_access = await self.storage.execute(
            select(AvailableForUsers).filter(
                AvailableForUsers.promo_code_id == promocode_id,
                (AvailableForUsers.users.contains(user_id) |
                 AvailableForUsers.groups.contains(group_id))
            )
        )
        user_promo_access = user_access.scalars().first()
        return user_promo_access is not None


async def get_access_service(
    redis: RedisCache = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
) -> AccessService:
    return AccessService(redis, db)
