from http import HTTPStatus
from typing import Annotated, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from models import Promocode, PromoUsage
from database import get_db
from utils.auth import security_jwt

router = APIRouter()

class ApplyPromocodeRequest(BaseModel):
    code: str
    user_id: int

class PromocodeResponse(BaseModel):
    discount_type: str
    discount_value: int

@router.post(
    "/apply_promocode/",
    response_model=PromocodeResponse,
    summary="Применить промокод",
    description="Применить промокод к пользователю",
    response_description="Тип и значение скидки",
    tags=["Промокоды"],
)
async def apply_promocode(
    apply: ApplyPromocodeRequest,
    db: Session = Depends(get_db),
    user: Annotated[dict, Depends(security_jwt)]
) -> PromocodeResponse:
    promocode = db.query(Promocode).filter(
        Promocode.code == apply.code,
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

    promo_usage = PromoUsage(user_id=apply.user_id, promocode_id=promocode.id)
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return PromocodeResponse(
        discount_type=promocode.discount_type,
        discount_value=promocode.discount_value
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
    description="Применить промокод по ID с дополнительными параметрами",
    response_description="Тип и значение скидки",
    tags=["Промокоды"],
)
async def apply_promocode_with_params(
    promocode_id: int = Query(..., description="ID промокода"),
    tariff: int = Query(..., description="Тариф, связанный с промокодом"),
    user_id: int = Query(..., description="ID пользователя, применяющего промокод"),
    db: Session = Depends(get_db),
    user: Annotated[dict, Depends(security_jwt)]
) -> PromocodeResponse:
    promocode = db.query(Promocode).filter(
        Promocode.id == promocode_id,
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

    promo_usage = PromoUsage(user_id=user_id, promocode_id=promocode.id)
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return PromocodeResponse(
        discount_type=promocode.discount_type,
        discount_value=promocode.discount_value
    )
