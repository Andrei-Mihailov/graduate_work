from enum import Enum
from uuid import UUID
import orjson

from pydantic import BaseModel as PydanticBaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseModel(PydanticBaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class EventType(str, Enum):
    registration = "users.registration"
    delete = "users.delete"


class UserResponce(BaseModel):
    """Модель пользователя для синхронизации"""
    uuid: UUID
    email: str
    is_active: bool
