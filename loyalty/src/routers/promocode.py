from http import HTTPStatus
from typing import Annotated, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from utils.auth import security_jwt
from models import Promocode, PromoUsage
from database import get_db

router = APIRouter()


class ApplyPromocodeRequest(BaseModel):
    code: str
    total_amount: float


class PromocodeResponse(BaseModel):
    discount_type: str
    discount_value: float
    final_amount: float


async def get_promocode(db: Session, code: str) -> Promocode:
    promocode = db.query(Promocode).filter(
        Promocode.code == code,
        Promocode.is_active == True
    ).first()
    return promocode


async def check_promocode_validity(promocode: Promocode, db: Session) -> None:
    if promocode.usage_limit is not None:
        usage_count = db.query(PromoUsage).filter_by(
            promocode_id=promocode.id,
            is_successful=True
        ).count()
        if usage_count >= promocode.usage_limit:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Достигнут лимит использования промокода"
            )

    if promocode.expiration_date and promocode.expiration_date < datetime.utcnow().date():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Промокод истек"
        )


@router.post(
    "/apply_promocode/",
    response_model=PromocodeResponse,
    summary="Применить промокод",
    description="Применить промокод к пользователю и рассчитать итоговую стоимость",
    response_description="Тип и значение скидки, итоговая стоимость",
    tags=["Промокоды"],
)
async def apply_promocode(
        apply: ApplyPromocodeRequest,
        db: Session = Depends(get_db),
        user: Annotated[dict, Depends(security_jwt)],
) -> PromocodeResponse:
    user_id = user["user_id"]

    promocode = await get_promocode(db, apply.code)

    if not promocode:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Промокод не найден или истек"
        )

    await check_promocode_validity(promocode, db)

    # Применение промокода
    discount_value = promocode.discount_value
    if promocode.discount_type == "percentage":
        discount_value = apply.total_amount * (promocode.discount_value / 100)

    final_amount = apply.total_amount - discount_value

    # Запись использования промокода
    promo_usage = PromoUsage(user_id=user_id, promocode_id=promocode.id, is_successful=True)
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return PromocodeResponse(
        discount_type=promocode.discount_type,
        discount_value=discount_value,
        final_amount=final_amount
    )


@router.get(
    "/get_active_promocodes",
    response_model=list[Promocode],
    summary="Получить активные промокоды",
    description="Получить все активные промокоды",
    response_description="Список активных промокодов",
    tags=["Промокоды"],
)
async def get_active_promocodes(
        db: Session = Depends(get_db),
        user: Annotated[dict, Depends(security_jwt)]
) -> list[Promocode]:
    active_promocodes = db.query(Promocode).filter(
        Promocode.is_active == True,
        Promocode.expiration_date >= datetime.utcnow().date()
    ).all()
    return active_promocodes


@router.get(
    "/apply_promocode_with_params/",
    response_model=PromocodeResponse,
    summary="Применить промокод с параметрами",
    description="Применить промокод по ID с дополнительными параметрами и рассчитать итоговую стоимость",
    response_description="Тип и значение скидки, итоговая стоимость",
    tags=["Промокоды"],
)
async def apply_promocode_with_params(
        promocode_id: int = Query(..., description="ID промокода"),
        tariff: int = Query(..., description="Тариф, связанный с промокодом"),
        total_amount: float = Query(..., description="Изначальная стоимость"),
        db: Session = Depends(get_db),
        user: Annotated[dict, Depends(security_jwt)]
) -> PromocodeResponse:
    user_id = user["user_id"]

    promocode = db.query(Promocode).filter(
        Promocode.id == promocode_id,
        Promocode.is_active == True
    ).first()

    if not promocode:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Промокод не найден или истек"
        )

    await check_promocode_validity(promocode, db)

    # Применение промокода
    discount_value = promocode.discount_value
    if promocode.discount_type == "percentage":
        discount_value = total_amount * (promocode.discount_value / 100)

    final_amount = total_amount - discount_value

    # Запись использования промокода
    promo_usage = PromoUsage(user_id=user_id, promocode_id=promocode.id, is_successful=True)
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return PromocodeResponse(
        discount_type=promocode.discount_type,
        discount_value=discount_value,
        final_amount=final_amount
    )
