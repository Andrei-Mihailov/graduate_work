import sentry_sdk

from http import HTTPStatus
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime

from utils.auth import security_jwt
from models.purchase import Tariff
from services.purchase_service import PurchaseService, get_purchase_service
from services.promo_code_service import PromoCodeService, get_promo_code_service

router = APIRouter()


class ApplyPromocodeRequest(BaseModel):
    promocode: str
    tariff_id: int


class PromocodeResponse(BaseModel):
    discount_type: str
    discount_value: float
    final_amount: float


@router.post("/apply_promocode/",
             response_model=PromocodeResponse,
             summary="Применить промокод",
             description="Применить промокод и рассчитать итоговую стоимость",
             response_description="Тип и значение скидки и итоговая стоимость",
             tags=["Промокоды"])
async def apply_promocode(
    user: Annotated[dict, Depends(security_jwt)],
    apply: ApplyPromocodeRequest,
    promo_code_service: PromoCodeService = Depends(get_promo_code_service),
    purchase_service: PurchaseService = Depends(get_purchase_service)
) -> PromocodeResponse:
    try:
        tariff: Tariff = await purchase_service.get_instance_by_id(apply.tariff_id)

        if not tariff:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Тариф не найден")

        promocode = await promo_code_service.get_valid_promocode(apply.promocode, user["id"])

        final_amount = await purchase_service.calculate_final_amount(tariff.price, promocode)

        return PromocodeResponse(
            discount_type=promocode.discount_type,
            discount_value=promocode.discount,
            final_amount=final_amount,
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e


class ActivePromocodeResponse(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    expiration_date: datetime


@router.get("/get_active_promocodes/",
            response_model=List[ActivePromocodeResponse],
            summary="Получить активные промокоды пользователя",
            description="Получить все активные промокоды, доступные пользователю",
            response_description="Список активных промокодов",
            tags=["Промокоды"])
async def get_active_promocodes(
    user: Annotated[dict, Depends(security_jwt)],
    promo_code_service: PromoCodeService = Depends(get_promo_code_service),
) -> List[ActivePromocodeResponse]:
    return await promo_code_service.get_active_promocodes_for_user(user["id"])


@router.post("/use_promocode/",
             response_model=PromocodeResponse,
             summary="Покупка с промокодом",
             description="Использовать промокод и сделать запись о покупке",
             response_description="Тип и значение скидки и итоговая стоимость",
             tags=["Промокоды"])
async def use_promocode(
    user: Annotated[dict, Depends(security_jwt)],
    apply: ApplyPromocodeRequest,
    purchase_service: PurchaseService = Depends(get_purchase_service),
    promo_code_service: PromoCodeService = Depends(get_promo_code_service)
) -> PromocodeResponse:
    try:
        result = await purchase_service.use_promocode(user["id"], apply.promocode, apply.tariff_id)

        return PromocodeResponse(
            discount_type=result["discount_type"],
            discount_value=result["discount_value"],
            final_amount=result["final_amount"],
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e


class CancelPromocodeRequest(BaseModel):
    promocode: int
    purchase_id: int


@router.post("/cancel_use_promocode/",
             response_model=PromocodeResponse,
             summary="Отменить использование промокода",
             description="Отменить использование промокода и вернуть реальную стоимость",
             response_description="Тип и значение скидки и итоговая стоимость",
             tags=["Промокоды"])
async def cancel_use_promocode(
    user: Annotated[dict, Depends(security_jwt)],
    cancel: CancelPromocodeRequest,
    purchase_service: PurchaseService = Depends(get_purchase_service),
) -> PromocodeResponse:
    try:
        purchase = await purchase_service.get_purchase(cancel.purchase_id, user["id"])

        # Обновляем стоимость покупки на стандартную
        final_amount = await purchase_service.cancel_purchase(purchase.id)

        return PromocodeResponse(
            discount_type=None,  # Поскольку промокод был отменен
            discount_value=0,    # Скидка 0
            final_amount=final_amount,  # Итоговая стоимость равна стандартной цене тарифа
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e
