from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from models import Promocode, PromoUsage
from database import get_db

router = APIRouter()

class ApplyPromocodeRequest(BaseModel):
    code: str
    user_id: int

@router.post("/apply_promocode/")
def apply_promocode(apply: ApplyPromocodeRequest, db: Session = Depends(get_db)):
    promocode = db.query(Promocode).filter(Promocode.code == apply.code, Promocode.is_active == True).first()
    if not promocode:
        raise HTTPException(status_code=404, detail="Promocode not found or expired")

    if promocode.usage_limit is not None:
        usage_count = db.query(PromoUsage).filter_by(promocode_id=promocode.id, is_successful=True).count()
        if usage_count >= promocode.usage_limit:
            raise HTTPException(status_code=400, detail="Promocode usage limit reached")

    if promocode.expiration_date and promocode.expiration_date < datetime.utcnow().date():
        raise HTTPException(status_code=400, detail="Promocode expired")

    promo_usage = PromoUsage(user_id=apply.user_id, promocode_id=promocode.id)
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return {
        "discount_type": promocode.discount_type,
        "discount_value": promocode.discount_value,
    }

@router.get("/get_active_promocodes")
def get_active_promocodes(db: Session = Depends(get_db)):
    active_promocodes = db.query(Promocode).filter(
        Promocode.is_active == True,
        Promocode.expiration_date >= datetime.utcnow().date()
    ).all()
    return active_promocodes

@router.get("/apply_promocode/")
def apply_promocode_with_params(
    promocode_id: int = Query(..., description="ID of the promocode"),
    tariff: int = Query(..., description="Tariff associated with the promocode"),
    user_id: int = Query(..., description="User ID applying the promocode"),
    db: Session = Depends(get_db)
):
    promocode = db.query(Promocode).filter(Promocode.id == promocode_id, Promocode.is_active == True).first()
    if not promocode:
        raise HTTPException(status_code=404, detail="Promocode not found or expired")

    if promocode.usage_limit is not None:
        usage_count = db.query(PromoUsage).filter_by(promocode_id=promocode.id, is_successful=True).count()
        if usage_count >= promocode.usage_limit:
            raise HTTPException(status_code=400, detail="Promocode usage limit reached")

    if promocode.expiration_date and promocode.expiration_date < datetime.utcnow().date():
        raise HTTPException(status_code=400, detail="Promocode expired")

    promo_usage = PromoUsage(user_id=user_id, promocode_id=promocode.id)
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return {
        "discount_type": promocode.discount_type,
        "discount_value": promocode.discount_value,
        "tariff": tariff
    }
