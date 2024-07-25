import pytest
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from main import app
from db.database import get_db
from models.base import Base
from models.promocode import Promocode, PromoUsage
from models.user import User
from datetime import datetime, timedelta
from utils.auth import create_access_token

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

async_engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)


@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def db_session():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        await session.close()
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def override_get_db(db_session):
    async def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides[get_db] = get_db


@pytest.fixture(scope="function")
async def test_user(db_session):
    user = User(id=1, username="testuser", password="testpassword")
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.mark.asyncio
async def test_use_promocode_success(
    async_client, override_get_db, db_session, test_user
):
    promocode = Promocode(
        id=1,
        code="PROMO",
        discount_type="percentage",
        discount_value=10,
        is_active=True,
        usage_limit=None,
        expiration_date=datetime.utcnow() + timedelta(days=1),
    )
    db_session.add(promocode)
    await db_session.commit()

    token = create_access_token(data={"sub": test_user.username})
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get(
        "/use_promocode/", params={"promocode_id": 1, "tariff": 100}, headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["discount_type"] == "percentage"
    assert data["discount_value"] == 10
    assert data["final_amount"] == 90


@pytest.mark.asyncio
async def test_cancel_use_promocode_success(
    async_client, override_get_db, db_session, test_user
):
    promocode = Promocode(
        id=1,
        code="PROMO",
        discount_type="percentage",
        discount_value=10,
        is_active=True,
        usage_limit=None,
        expiration_date=datetime.utcnow() + timedelta(days=1),
    )
    db_session.add(promocode)
    await db_session.commit()

    promo_usage = PromoUsage(
        user_id=test_user.id, promocode_id=promocode.id, is_successful=True
    )
    db_session.add(promo_usage)
    await db_session.commit()

    token = create_access_token(data={"sub": test_user.username})
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get(
        "/cancel_use_promocode/", params={"promocode_id": 1}, headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Использование промокода успешно отменено"

    # Проверка, что статус промокода обновился
    updated_promo_usage = (
        db_session.query(PromoUsage)
        .filter_by(user_id=test_user.id, promocode_id=promocode.id)
        .first()
    )
    assert updated_promo_usage is not None
    assert not updated_promo_usage.is_successful
