from enum import Enum
from pydantic import BaseModel as PydanticBaseModel
import orjson
from uuid import UUID


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseModel(PydanticBaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class EventType(str, Enum):
    registration = "registration"
    delete = "delete"


class UserResponce(BaseModel):
    """Модель пользователя для синхронизации"""
    uuid: UUID
    email: str
    is_deleted: bool
