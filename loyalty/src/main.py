from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import string
from datetime import datetime
from pydantic import BaseModel, validator

from database import engine, get_db

app = FastAPI()


from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    DECIMAL,
    ForeignKey,
    TIMESTAMP,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Promocode(Base):
    __tablename__ = "promocodes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    discount_type = Column(String, nullable=False)  # "fixed", "percentage", "trial"
    discount_value = Column(DECIMAL, nullable=False)  # сумма скидки или процент
    expiration_date = Column(Date)
    usage_limit = Column(
        Integer
    )  # ограничение на количество использований (NULL для неограниченного)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")


class PromoUsage(Base):
    __tablename__ = "promo_usage"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    promocode_id = Column(Integer, ForeignKey("promocodes.id"), nullable=False)
    used_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    is_successful = Column(Boolean, default=False)

    promocode = relationship("Promocode", back_populates="usages")


Promocode.usages = relationship(
    "PromoUsage", order_by=PromoUsage.id, back_populates="promocode"
)


# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)


class PromocodeCreate(BaseModel):
    discount_type: str
    discount_value: float
    expiration_date: datetime = None
    usage_limit: int = None

    @validator("discount_type")
    def validate_discount_type(cls, v):
        if v not in ("fixed", "percentage", "trial"):
            raise ValueError("Invalid discount type")
        return v


@app.post("/generate_promocode/")
def generate_promocode(promo: PromocodeCreate, db: Session = Depends(get_db)):
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    new_promocode = Promocode(
        code=code,
        discount_type=promo.discount_type,
        discount_value=promo.discount_value,
        expiration_date=promo.expiration_date,
        usage_limit=promo.usage_limit,
    )
    db.add(new_promocode)
    db.commit()
    db.refresh(new_promocode)
    return {"code": new_promocode.code}


class ApplyPromocode(BaseModel):
    code: str
    user_id: int


@app.post("/apply_promocode/")
def apply_promocode(apply: ApplyPromocode, db: Session = Depends(get_db)):
    promocode = (
        db.query(Promocode)
        .filter(Promocode.code == apply.code, Promocode.is_active == True)
        .first()
    )
    if not promocode:
        raise HTTPException(status_code=404, detail="Promocode not found or expired")

    if promocode.usage_limit is not None:
        usage_count = (
            db.query(PromoUsage)
            .filter_by(promocode_id=promocode.id, is_successful=True)
            .count()
        )
        if usage_count >= promocode.usage_limit:
            raise HTTPException(status_code=400, detail="Promocode usage limit reached")

    if (
        promocode.expiration_date
        and promocode.expiration_date < datetime.utcnow().date()
    ):
        raise HTTPException(status_code=400, detail="Promocode expired")

    promo_usage = PromoUsage(user_id=apply.user_id, promocode_id=promocode.id)
    db.add(promo_usage)
    db.commit()
    db.refresh(promo_usage)

    return {
        "discount_type": promocode.discount_type,
        "discount_value": promocode.discount_value,
    }


class CancelPromocode(BaseModel):
    user_id: int
    promocode_id: int


@app.post("/cancel_promocode/")
def cancel_promocode(cancel: CancelPromocode, db: Session = Depends(get_db)):
    promo_usage = (
        db.query(PromoUsage)
        .filter_by(
            user_id=cancel.user_id,
            promocode_id=cancel.promocode_id,
            is_successful=False,
        )
        .first()
    )
    if not promo_usage:
        raise HTTPException(status_code=404, detail="Promocode usage not found")

    db.delete(promo_usage)
    db.commit()

    return {"message": "Promocode usage canceled"}


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is running!"}
