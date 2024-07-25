from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from utils.auth import security_jwt
from models.promocode import Promocode
from models.user import (
    PromoUsage,
    Tariff,
)  # Добавьте модель Tariff, если она существует
from db.database import get_db

router = APIRouter()


class ApplyPromocodeRequest(BaseModel):
    promocode_id: int
    tariff_id: int


class PromocodeResponse(BaseModel):
    discount_type: str
    discount_value: float
    final_amount: float


def get_valid_promocode(promocode_id: int, db: Session) -> Promocode:
    promocode = (
        db.query(Promocode)
        .filter(Promocode.id == promocode_id, Promocode.is_active == True)
        .first()
    )

    if not promocode:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Промокод не найден или истек"
        )

    if promocode.usage_limit is not None:
        usage_count = (
            db.query(PromoUsage)
            .filter_by(promocode_id=promocode.id, is_successful=True)
            .count()
        )
        if usage_count >= promocode.usage_limit:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Достигнут лимит использования промокода",
            )

    if (
        promocode.expiration_date
        and promocode.expiration_date < datetime.utcnow().date()
    ):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Промокод истек")

    return promocode


def calculate_final_amount(tariff_amount: float, promocode: Promocode) -> float:
    discount_value = promocode.discount_value
    if promocode.discount_type == "percentage":
        final_amount = tariff_amount * (1 - discount_value / 100)
    elif promocode.discount_type == "fixed":
        final_amount = tariff_amount - discount_value
    elif promocode.discount_type == "trial":
        final_amount = 0
    else:
        raise ValueError(f"Unsupported discount type: {promocode.discount_type}")

    return max(final_amount, 0)


@router.post(
    "/apply_promocode/",
    response_model=PromocodeResponse,
    summary="Применить промокод",
    description="Применить промокод к пользователю и рассчитать итоговую стоимость",
    response_description="Тип и значение скидки и итоговая стоимость",
    tags=["Промокоды"],
)
async def apply_promocode(
    user: Annotated[dict, Depends(security_jwt)],
    apply: ApplyPromocodeRequest,
    db: Session = Depends(get_db),
) -> PromocodeResponse:
    # Получаем тариф по ID
    tariff = db.query(Tariff).filter(Tariff.id == apply.tariff_id).first()
    if not tariff:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Тариф не найден")

    # Проверяем промокод
    promocode = get_valid_promocode(apply.promocode_id, db)
    final_amount = calculate_final_amount(tariff.amount, promocode)

    # Создаем запись о применении промокода
    promo_usage = PromoUsage(
        user_id=user["id"],  # Используем ID из JWT
        promocode_id=promocode.id,
        is_successful=True,
    )
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return PromocodeResponse(
        discount_type=promocode.discount_type,
        discount_value=promocode.discount_value,
        final_amount=final_amount,
    )


class ActivePromocodeResponse(BaseModel):
    id: int
    code: str
    discount_type: str
    discount_value: float
    expiration_date: datetime


@router.get(
    "/get_active_promocodes/",
    response_model=list[ActivePromocodeResponse],
    summary="Получить активные промокоды",
    description="Получить все активные промокоды, доступные пользователю",
    response_description="Список активных промокодов",
    tags=["Промокоды"],
)
async def get_active_promocodes(
    user: Annotated[dict, Depends(security_jwt)],
    db: Session = Depends(get_db),
) -> list[ActivePromocodeResponse]:
    active_promocodes = (
        db.query(Promocode)
        .filter(
            Promocode.is_active == True,
            Promocode.expiration_date >= datetime.utcnow().date(),
        )
        .all()
    )

    # Логика фильтрации промокодов по доступности пользователю
    user_promocodes = [
        promo for promo in active_promocodes if promo.user_id == user["id"]
    ]

    return user_promocodes


@router.get(
    "/use_promocode/",
    response_model=PromocodeResponse,
    summary="Покупка тарифа по промокоду",
    description="Покупка тарифа по промокоду",
    response_description="Тип и значение скидки и итоговая стоимость",
    tags=["Промокоды"],
)
async def use_promocode(
    user: Annotated[dict, Depends(security_jwt)],
    promocode_id: int = Query(..., description="ID промокода"),
    tariff_id: int = Query(..., description="ID тарифа"),
    db: Session = Depends(get_db),
) -> PromocodeResponse:
    # Получаем тариф по ID
    tariff = db.query(Tariff).filter(Tariff.id == tariff_id).first()
    if not tariff:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Тариф не найден")

    # Проверяем промокод
    promocode = get_valid_promocode(promocode_id, db)
    final_amount = calculate_final_amount(tariff.amount, promocode)

    promo_usage = PromoUsage(
        user_id=user["id"],  # Используем ID из JWT
        promocode_id=promocode.id,
        is_successful=True,
    )
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return PromocodeResponse(
        discount_type=promocode.discount_type,
        discount_value=promocode.discount_value,
        final_amount=final_amount,
    )


class CancelPromocodeRequest(BaseModel):
    promocode_id: int


@router.post(
    "/cancel_use_promocode/",
    summary="Отменить использование промокода",
    description="Отменить использование промокода",
    tags=["Промокоды"],
)
async def cancel_use_promocode(
    user: Annotated[dict, Depends(security_jwt)],
    cancel: CancelPromocodeRequest,
    db: Session = Depends(get_db),
):
    promo_usage = (
        db.query(PromoUsage)
        .filter_by(
            promocode_id=cancel.promocode_id, user_id=user["id"], is_successful=True
        )
        .first()
    )

    if not promo_usage:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Использование промокода не найдено",
        )

    promo_usage.is_successful = False
    db.commit()
    db.refresh(promo_usage)

    return {"detail": "Использование промокода отменено"}
