from uuid import UUID, uuid4
from enum import Enum
from typing import Union

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default) -> str:
    return orjson.dumps(v, default=default).decode()


class OrjsonBaseModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UserModel(OrjsonBaseModel):
    id: UUID = uuid4()
    username: str
    email: str


class NotificationType(str, Enum):
    personal = "personal"
    group = "group"
    all = "all"


class RequestEventModel(OrjsonBaseModel):
    recipient: Union[str, list]
    type_event: NotificationType
    event: str
    template_name: str
    context: dict


class ResponseModel(OrjsonBaseModel):
    email: str
    event: str
    context: dict
