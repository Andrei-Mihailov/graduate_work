# models/entity.py
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.postgres_db import Base
from services.utils import hash_password, validate_password


class Roles(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    type: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    permissions: Mapped[list["Permissions"]] = relationship(
        "Permissions", back_populates="role"
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class Permissions(Base):
    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), default=None, nullable=True
    )
    role: Mapped[Roles] = relationship("Roles", back_populates="permissions")


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), default=None, nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), default=None, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    active: Mapped[Boolean] = mapped_column(Boolean, default=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), default=None, nullable=True
    )
    role: Mapped[Roles] = relationship("Roles", back_populates="users")
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    def __init__(
        self,
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        is_staff: bool = False,
        is_superuser: bool = False,
        active: bool = True
    ) -> None:
        self.email = email
        self.password = hash_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.active: bool = True

    def check_password(self, password: str) -> bool:
        return validate_password(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Authentication(Base):
    __tablename__ = "authentication"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user_agent: Mapped[str] = mapped_column(String(255), nullable=False)
    date_auth: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Authentication {self.id}>"
