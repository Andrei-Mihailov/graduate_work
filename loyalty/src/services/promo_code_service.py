import sentry_sdk

from typing import List
from datetime import datetime
from models.promocode import PromoCode, AvailableForUsers
from http import HTTPStatus
from fastapi.encoders import jsonable_encoder
from fastapi import Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.promocode import PromoCode
from models.user import User
from .base_service import BaseService
from db.database import get_db
from db.redis_db import RedisCache, get_redis


class PromoCodeService(BaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        super().__init__(cache, storage)
        self.model = PromoCode

    async def get_valid_promocode(self, promocode_id: int, user_id: int) -> PromoCode:
        """Проверяет валидность промокода."""
        promocode_cache_key = f"promocode:{promocode_id}"
        cached_promocode = await self.get_cache(promocode_cache_key)

        if not cached_promocode:
            promocode: PromoCode = await self.get_instance_by_id(promocode_id)
            if not promocode or not promocode.is_active:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail="Промокод не найден или истек"
                )

            user_access = await self.storage.execute(
                select(AvailableForUsers)
                .filter(
                    AvailableForUsers.promo_code_id == promocode_id,
                    (AvailableForUsers.users.contains(user_id) |
                     AvailableForUsers.groups.contains(user_id))
                )
            )
            user_promo_access = user_access.scalars().first()

            if not user_promo_access:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN, detail="У вас нет доступа к этому промокоду"
                )

            if promocode.expiration_date and promocode.expiration_date < datetime.utcnow().date():
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Промокод истек")

            # Кэшируем активный промокод
            await self.cache_active_instances([promocode])
            return promocode

        return cached_promocode

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

    async def get_active_promocodes_for_user(self, user_id: int) -> List[dict]:
        # Получаем информацию о пользователе, включая group_id
        user_record = await self.storage.execute(
            select(User).filter(User.id == user_id)
        )
        user = user_record.scalars().first()

        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Пользователь не найден")

        group_id = user.group_id  # Предполагается, что у вас есть поле group_id в модели User

        active_promocodes = (
            await self.storage.execute(
                select(PromoCode).filter(
                    PromoCode.is_active == True,
                    PromoCode.expiration_date >= datetime.utcnow().date(),
                )
            )
        ).scalars().all()

        user_promocodes = []
        for promo in active_promocodes:
            if await self.is_promocode_available_for_user(promo.id, user_id, group_id):
                user_promocodes.append({
                    "code": promo.code,
                    "discount_type": promo.discount_type,
                    "discount_value": promo.discount,
                    "expiration_date": promo.expiration_date,
                })

        return user_promocodes


async def get_promo_code_service(
    redis: RedisCache = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
) -> PromoCodeService:
    return PromoCodeService(redis, db)
