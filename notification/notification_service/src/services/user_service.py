from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from requests.exceptions import Timeout, ConnectionError
from backoff import on_exception, expo

from db.postgres_db import get_db
from db.models import User
from models.models import UserModel


class UserService:
    _model = User

    def __init__(self, session: AsyncSession):
        self._session = session

    @on_exception(expo, (ConnectionError, Timeout), max_tries=10)
    async def get_user_by_id(self, id: str) -> UserModel:
        query = select(self._model).where(self._model.id == id)
        result = await self._session.execute(query)
        user_db = result.scalar_one_or_none()
        if user_db:
            return user_db.serialize
        else:
            return None

    @on_exception(expo, (ConnectionError, Timeout), max_tries=10)
    async def get_users(self, user_list: Union[list, None]) -> list[UserModel]:
        if not user_list:
            query = select(self._model)
        else:
            query = select(self._model).filter(self._model.id.in_(user_list))

        result = await self._session.execute(query)
        users_db = result.scalars().all()
        list_users_model = []
        for item in users_db:
            list_users_model.append(item.serialize)

        return list_users_model


def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)
