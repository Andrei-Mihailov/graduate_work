from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import string
from datetime import datetime
from pydantic import BaseModel, validator

from models import Base, Promocode, PromoUsage
from database import engine, get_db
from config import pg_config_data
from sqlalchemy import create_engine

app = FastAPI()

DATABASE_URL = (
    f"postgresql+asyncpg://{pg_config_data.user}:{pg_config_data.password}@{pg_config_data.host}:"
    f"{pg_config_data.port}/{pg_config_data.dbname}"
)

engine = create_engine(DATABASE_URL)

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)


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


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is running!"}
