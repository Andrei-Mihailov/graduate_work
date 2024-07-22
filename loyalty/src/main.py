import sentry_sdk
import logging
from fastapi import FastAPI, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from models import Base, Promocode, PromoUsage
from database import engine, get_db
from config import pg_config_data
from sqlalchemy import create_engine
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

sentry_sdk.init(
    dsn="https://7e322a912461958b85dcdf23716aeff5@o4507457845592064.ingest.de.sentry.io/4507457848016976",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
sentry_sdk.init(
    dsn="https://7e322a912461958b85dcdf23716aeff5@o4507457845592064.ingest.de.sentry.io/4507457848016976",
    integrations=[sentry_logging],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = FastAPI()

DATABASE_URL = (
    f"postgresql+asyncpg://{pg_config_data.user}:{pg_config_data.password}@{pg_config_data.host}:"
    f"{pg_config_data.port}/{pg_config_data.dbname}"
)

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)


class ApplyPromocodeRequest(BaseModel):
    code: str
    user_id: int


@app.post("/apply_promocode/")
def apply_promocode(apply: ApplyPromocodeRequest, db: Session = Depends(get_db)):
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


@app.get("/get_active_promocodes")
def get_active_promocodes(db: Session = Depends(get_db)):
    active_promocodes = db.query(Promocode).filter(
        Promocode.is_active == True,
        Promocode.expiration_date >= datetime.utcnow().date()
    ).all()
    return active_promocodes


@app.get("/apply_promocode/")
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


@app.middleware("http")
async def sentry_exception_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e
    return response


app.add_middleware(SentryAsgiMiddleware)
