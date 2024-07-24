from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from utils.auth import security_jwt, get_current_user
from models import Promocode, PromoUsage
from database import get_db

router = APIRouter()

class ApplyPromocodeRequest(BaseModel):
    promocode_id: int
    tariff: float

class PromocodeResponse(BaseModel):
    discount_type: str
    discount_value: float
    final_amount: float

@router.post(
    "/apply_promocode/",
    response_model=PromocodeResponse,
    summary="Применить промокод",
    description="Применить промокод к пользователю и рассчитать итоговую стоимость",
    response_description="Тип и значение скидки и итоговая стоимость",
    tags=["Промокоды"],
)
async def apply_promocode(
    apply: ApplyPromocodeRequest,
) -> PromocodeResponse:
    db = Depends(get_db)
    user = Annotated[dict, Depends(security_jwt)]
    promocode = db.query(Promocode).filter(
        Promocode.id == apply.promocode_id,
        Promocode.is_active == True
    ).first()

    if not promocode:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Промокод не найден или истек"
        )

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

    discount_value = promocode.discount_value
    final_amount = apply.tariff

    if promocode.discount_type == "percentage":
        final_amount = apply.tariff * (1 - discount_value / 100)
    elif promocode.discount_type == "fixed":
        final_amount = apply.tariff - discount_value

    if final_amount < 0:
        final_amount = 0

    promo_usage = PromoUsage(user_id=user['id'], promocode_id=promocode.id, is_successful=True)
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return PromocodeResponse(
        discount_type=promocode.discount_type,
        discount_value=discount_value,
        final_amount=final_amount
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
    description="Получить все активные промокоды",
    response_description="Список активных промокодов",
    tags=["Промокоды"],
)
async def get_active_promocodes(
    db: Session = Depends(get_db),
    user: Annotated[dict, Depends(security_jwt)]
) -> list[ActivePromocodeResponse]:
    active_promocodes = db.query(Promocode).filter(
        Promocode.is_active == True,
        Promocode.expiration_date >= datetime.utcnow().date()
    ).all()
    return active_promocodes

@router.get(
    "/use_promocode/",
    response_model=PromocodeResponse,
    summary="Покупка тарифа по промокоду",
    description="Покупка тарифа по промокоду",
    response_description="Тип и значение скидки и итоговая стоимость",
    tags=["Промокоды"],
)
async def use_promocode(
    promocode_id: int = Query(..., description="ID промокода"),
    tariff: float = Query(..., description="Тариф, связанный с промокодом"),
) -> PromocodeResponse:
    db = Depends(get_db)
    user = Annotated[dict, Depends(security_jwt)]
    promocode = db.query(Promocode).filter(
        Promocode.id == promocode_id,
        Promocode.is_active == True
    ).first()

    if not promocode:
        raise HTTPException(
            status_code


=HTTPStatus.NOT_FOUND,
            detail="Промокод не найден"
        )

    if promocode.expiration_date and promocode.expiration_date < datetime.utcnow().date():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Промокод истек"
        )

    discount_value = promocode.discount_value
    final_amount = tariff - discount_value

    if final_amount < 0:
        final_amount = 0

    promo_usage = PromoUsage(user_id=user['id'], promocode_id=promocode.id, is_successful=True)
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return PromocodeResponse(
        discount_type=promocode.discount_type,
        discount_value=discount_value,
        final_amount=final_amount
    )
