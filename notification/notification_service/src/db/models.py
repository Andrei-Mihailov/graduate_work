import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from db.postgres_db import base
from models.models import UserModel


class User(base):
    __tablename__ = "auth_user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    username = Column(String, unique=True, nullable=False)
    email = Column(String(255), unique=True)

    @property
    def serialize(self):
        return UserModel(id=self.id, username=self.username, email=self.email)
