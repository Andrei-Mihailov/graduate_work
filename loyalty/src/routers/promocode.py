from http import HTTPStatus
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from utils.auth import security_jwt
from models.promocode import PromoCode, AvailableForUsers
from models.purchase import Tariff, Purchase
from db.database import get_db

router = APIRouter()


class ApplyPromocodeRequest(BaseModel):
    promocode_id: int
    tariff_id: int


class PromocodeResponse(BaseModel):
    discount_type: str
    discount_value: float
    final_amount: float


def get_valid_promocode(promocode_id: int, user_id: int, db: Session) -> PromoCode:
    promocode = (
        db.query(PromoCode)
        .filter(PromoCode.id == promocode_id, PromoCode.is_active == True)
        .first()
    )

    if not promocode:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Промокод не найден или истек"
        )

    user_promo_access = (
        db.query(AvailableForUsers)
        .filter(
            AvailableForUsers.promo_code_id == promocode_id,
            (AvailableForUsers.user.contains(user_id) | AvailableForUsers.group.contains(user_id))
        )
        .first()
    )

    if not user_promo_access:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="У вас нет доступа к этому промокоду"
        )

    if (
        promocode.expiration_date
        and promocode.expiration_date < datetime.utcnow().date()
    ):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Промокод истек")

    return promocode


def get_tariff(tariff_id: int, db: Session) -> Tariff:
    tariff = db.query(Tariff).filter(Tariff.id == tariff_id).first()
    if not tariff:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Тариф не найден")
    return tariff


def calculate_final_amount(original_amount: float, promocode: PromoCode) -> float:
    discount_value = promocode.discount
    if promocode.discount_type == PromoCode.DiscountType.PERCENTAGE:
        final_amount = original_amount * (1 - discount_value / 100)
    elif promocode.discount_type == PromoCode.DiscountType.FIXED:
        final_amount = original_amount - discount_value
    elif promocode.discount_type == PromoCode.DiscountType.TRIAL:
        final_amount = 0
    else:
        raise ValueError(f"Unsupported discount type: {promocode.discount_type}")

    return max(final_amount, 0)


@router.post("/apply_promocode/",
             response_model=PromocodeResponse,
             summary="Применить промокод",
             description="Применить промокод и рассчитать итоговую стоимость",
             response_description="Тип и значение скидки и итоговая стоимость",
             tags=["Промокоды"])
async def apply_promocode(
    user: Annotated[dict, Depends(security_jwt)],
    apply: ApplyPromocodeRequest,
    db: Session = Depends(get_db),
) -> PromocodeResponse:
    # Проверяем тариф
    tariff = get_tariff(apply.tariff_id, db)

    # Проверяем промокод
    promocode = get_valid_promocode(apply.promocode_id, user["id"], db)

    # Используем стоимость тарифа
    final_amount = calculate_final_amount(tariff.price, promocode)

    # Записываем данные в таблицу Purchase
    purchase = Purchase(
        user_id=user["id"],  # ID пользователя из JWT
        tariff_id=tariff.id,
        promocode_id=promocode.id,
        amount=final_amount,
        created_at=datetime.utcnow()
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    return PromocodeResponse(
        discount_type=promocode.discount_type,
        discount_value=promocode.discount,
        final_amount=final_amount,
    )


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
    db: Session = Depends(get_db),
) -> List[ActivePromocodeResponse]:
    active_promocodes = (
        db.query(PromoCode)
        .filter(
            PromoCode.is_active == True,
            PromoCode.expiration_date >= datetime.utcnow().date(),
        )
        .all()
    )

    # Логика фильтрации промокодов по доступности пользователю
    user_promocodes = [
        {
            "code": promo.code,
            "discount_type": promo.discount_type,
            "discount_value": promo.discount,
            "expiration_date": promo.expiration_date,
        }
        for promo in active_promocodes if db.query(AvailableForUsers).filter((AvailableForUsers.user.contains(user["id"]) |
                                                                              AvailableForUsers.group.contains(user["group_id"])),
                                                                             AvailableForUsers.promo_code_id == promo.id).count() > 0
    ]

    return user_promocodes


@router.post("/use_promocode/",
             response_model=PromocodeResponse,
             summary="Использовать промокод",
             description="Использовать промокод и получить итоговую стоимость",
             response_description="Тип и значение скидки и итоговая стоимость",
             tags=["Промокоды"])
async def use_promocode(
    user: Annotated[dict, Depends(security_jwt)],
    apply: ApplyPromocodeRequest,
    db: Session = Depends(get_db),
) -> PromocodeResponse:
    # Проверяем тариф
    tariff = get_tariff(apply.tariff_id, db)

    # Проверяем промокод
    promocode = get_valid_promocode(apply.promocode_id, user["id"], db)

    # Используем стоимость тарифа
    final_amount = calculate_final_amount(tariff.price, promocode)

    # Записываем данные в таблицу Purchase
    purchase = Purchase(
        user_id=user["id"],
        tariff_id=tariff.id,
        promocode_id=promocode.id,
        amount=final_amount,
        created_at=datetime.utcnow()
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    return PromocodeResponse(
        discount_type=promocode.discount_type,
        discount_value=promocode.discount,
        final_amount=final_amount,
    )


class CancelPromocodeRequest(BaseModel):
    promocode_id: int
    purchase_id: int


@router.post("/cancel_use_promocode/",
             summary="Отменить использование промокода",
             description="Отменить использование промокода",
             tags=["Промокоды"])
async def cancel_use_promocode(
    user: Annotated[dict, Depends(security_jwt)],
    cancel: CancelPromocodeRequest,
    db: Session = Depends(get_db),
):
    # Найдем запись о покупке
    purchase = db.query(Purchase).filter(Purchase.id == cancel.purchase_id, Purchase.user_id == user["id"]).first()

    if not purchase:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Запись о покупке не найдена"
        )

    # Удаляем запись о покупке
    db.delete(purchase)
    db.commit()

    return {"detail": "Использование промокода отменено и запись удалена"}
