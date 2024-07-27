import sentry_sdk

from typing import List
from datetime import datetime
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.promocode import PromoCode
from .base_service import BaseService
from db.postgres_db import get_session
from db.redis_db import RedisCache, get_redis
from .access_service import AccessService


class PromoCodeService(BaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession, access_service: AccessService):
        super().__init__(cache, storage)
        self.model = PromoCode
        self.access_service = access_service

    async def get_valid_promocode(self, promocode_str: str, user_id: int) -> PromoCode:
        """Проверяет валидность промокода."""
        promocode_cache_key = f"promocode:{promocode_str}"
        cached_promocode = await self.get_cache(promocode_cache_key)

        if not cached_promocode:
            try:
                promocode: PromoCode = await self.get_instance_by_code(promocode_str)
                if not promocode or not promocode.is_active:
                    return 'not found'

                user = await self.get_user_by_id(user_id)

                if not user:
                    return 'User not found'

                # Проверяем доступность промокода для пользователя через AccessService
                user_has_access = await self.access_service.is_promocode_available_for_user(promocode.id, user_id, user.group_id)

                if not user_has_access:
                    return 'not access'

                if promocode.expiration_date and promocode.expiration_date < datetime.utcnow().date():
                    return 'expired'

                # Кэшируем активный промокод
                await self.cache_active_instances([promocode])
                return promocode

            except Exception as e:
                sentry_sdk.capture_exception(e)
                raise e
        return cached_promocode

    async def get_active_promocodes_for_user(self, user_id: int) -> List[dict]:
        """Получает активные промокоды для пользователя."""
        user = await self.get_user_by_id(user_id)

        if not user:
            return None

        active_promocodes = self.get_active_promocodes()

        user_promocodes = []
        for promo in active_promocodes:
            if await self.access_service.is_promocode_available_for_user(promo.id, user_id, user.group_id):
                user_promocodes.append({
                    "code": promo.code,
                    "discount_type": promo.discount_type,
                    "discount_value": promo.discount,
                    "expiration_date": promo.expiration_date,
                })

        return user_promocodes


async def get_promo_code_service(
    redis: RedisCache = Depends(get_redis),
    db: AsyncSession = Depends(get_session),
) -> PromoCodeService:
    return PromoCodeService(redis, db)
