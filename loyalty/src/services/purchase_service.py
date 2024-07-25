import sentry_sdk

from datetime import datetime
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from models.purchase import Tariff, Purchase

from .base_service import BaseService
from .promo_code_service import PromoCodeService
from db.database import get_db
from db.redis_db import RedisCache, get_redis


class PurchaseService(BaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        super().__init__(cache, storage)

    async def calculate_final_amount(self, original_amount: float, discount_type: str, discount_value: float) -> float:
        """Вычисляет итоговую сумму с учетом промокода."""
        if discount_type == "percentage":
            final_amount = original_amount * (100 - discount_value) / 100
        elif discount_type == "fixed":
            final_amount = original_amount - discount_value
        elif discount_type == "trial":
            final_amount = 0
        else:
            raise ValueError(f"Unsupported discount type: {discount_type}")

        return max(final_amount, 0)

    async def get_purchase(self, purchase_id: int, user_id: int) -> Purchase:
        """Получает запись о покупке по ID для конкретного пользователя."""
        purchase: Purchase = await self.get_instance_by_id(purchase_id)
        if not purchase or purchase.user_id != user_id:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Запись о покупке не найдена.")
        return purchase

    async def cancel_purchase(self, purchase_id: int, user_id: int) -> None:
        """Отменяет покупку по ID."""
        purchase: Purchase = await self.get_instance_by_id(purchase_id)

        if not purchase or purchase.user_id != user_id:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Запись о покупке не найдена.")

        await self.del_instance_by_id(purchase_id)

    async def use_promocode(self, user_id: int, promocode_id: int, tariff_id: int) -> dict:
        """Использует промокод для покупки и возвращает данные о результате."""
        promocode_service = PromoCodeService(self.cache, self.storage)
        promocode = await promocode_service.get_valid_promocode(promocode_id, user_id)

        tariff: Tariff = await self.get_instance_by_id(tariff_id)
        if not tariff:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Тариф не найден")

        final_amount = await self.calculate_final_amount(tariff.price, promocode)

        purchase = Purchase(
            user_id=user_id,
            tariff_id=tariff_id,
            promocode_id=promocode.id,
            amount=final_amount,
            created_at=datetime.utcnow()
        )
        await self.create_new_instance(purchase)

        return {
            "discount_type": promocode.discount_type,
            "discount_value": promocode.discount,
            "final_amount": final_amount,
        }


async def get_purchase_service(
    redis: RedisCache = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
) -> PromoCodeService:
    return PromoCodeService(redis, db)
