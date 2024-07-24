import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app
from models import Promocode, PromoUsage, User
from database import get_db
from utils.auth import create_jwt_token

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Создаем асинхронный движок и сессию для тестирования
async_engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
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
async def jwt_token():
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashed_password",
    )
    async with TestingSessionLocal() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    token = create_jwt_token(user_id=user.id)
    return token, user


@pytest.mark.asyncio
async def test_apply_promocode(async_client, override_get_db, jwt_token, db_session):
    token, user = jwt_token
    promocode = Promocode(
        code="TESTCODE",
        discount_type="percentage",
        discount_value=10,
        is_active=True,
        usage_limit=10,
        expiration_date=datetime.utcnow().date() + timedelta(days=1),
    )
    db_session.add(promocode)
    await db_session.commit()

    response = await async_client.post(
        "/api/v1/apply_promocode/",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "TESTCODE", "total_amount": 100},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["discount_type"] == "percentage"
    assert data["discount_value"] == 10
    assert data["final_amount"] == 90


@pytest.mark.asyncio
async def test_get_active_promocodes(
    async_client, override_get_db, jwt_token, db_session
):
    token, _ = jwt_token
    promocode = Promocode(
        code="ACTIVECODE",
        discount_type="percentage",
        discount_value=15,
        is_active=True,
        usage_limit=5,
        expiration_date=datetime.utcnow().date() + timedelta(days=1),
    )
    db_session.add(promocode)
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/get_active_promocodes", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "ACTIVECODE"
    assert data[0]["discount_value"] == 15


@pytest.mark.asyncio
async def test_apply_promocode_with_params(
    async_client, override_get_db, jwt_token, db_session
):
    token, user = jwt_token
    promocode = Promocode(
        id=1,
        code="PARAMCODE",
        discount_type="fixed",
        discount_value=20,
        is_active=True,
        usage_limit=10,
        expiration_date=datetime.utcnow().date() + timedelta(days=1),
    )
    db_session.add(promocode)
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/apply_promocode_with_params/",
        headers={"Authorization": f"Bearer {token}"},
        params={"promocode_id": promocode.id, "tariff": 100, "total_amount": 100},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["discount_type"] == "fixed"
    assert data["discount_value"] == 20
    assert data["final_amount"] == 80
