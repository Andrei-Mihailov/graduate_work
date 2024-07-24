from http import HTTPStatus
from typing import Annotated, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from utils.auth import security_jwt
from models import Promocode, PromoUsage
from database import get_db

router = APIRouter()


class ApplyPromocodeRequest(BaseModel):
    code: str
    total_amount: float


class PromocodeResponse(BaseModel):
    final_amount: float
    discount_type: str
    discount_value: float


@router.post(
    "/apply_promocode/",
    response_model=PromocodeResponse,
    summary="Применить промокод",
    description="Применить промокод к пользователю и рассчитать итоговую стоимость",
    response_description="Итоговая стоимость, тип и значение скидки",
    tags=["Промокоды"],
)
async def apply_promocode(
        apply: ApplyPromocodeRequest,
        db: Session = Depends(get_db),
        user: Annotated[dict, Depends(security_jwt)]
) -> PromocodeResponse:
    user_id = user.get("user_id")

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

    # Рассчитать итоговую стоимость с учетом промокода
    if promocode.discount_type == "percentage":
        discount = (apply.total_amount * promocode.discount_value) / 100
    else:  # "fixed"
        discount = promocode.discount_value

    final_amount = apply.total_amount - discount

    promo_usage = PromoUsage(user_id=user_id, promocode_id=promocode.id)
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return PromocodeResponse(
        final_amount=final_amount,
        discount_type=promocode.discount_type,
        discount_value=promocode.discount_value
    )
