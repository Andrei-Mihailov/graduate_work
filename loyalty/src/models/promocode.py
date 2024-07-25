from datetime import datetime

from sqlalchemy import Column, String, Float, Integer, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(length=255), unique=True, nullable=False)
    discount = Column(Float, default=0)
    discount_type = Column(String(length=15), default="fixed")
    num_uses = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    creation_date = Column(Date, nullable=False, default=datetime.utcnow)
    expiration_date = Column(Date, nullable=True)
    is_deleted = Column(Boolean, default=False)


class AvailableForUsers(Base):
    __tablename__ = "available_for_users"

    id = Column(Integer, primary_key=True, index=True)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), nullable=False)
    promo_code = relationship("PromoCode", back_populates="available_for_users")

    users = relationship(
        "User",
        secondary="available_users",
        back_populates="available_promo_codes",
    )
    groups = relationship(
        "Group",
        secondary="available_groups",
        back_populates="available_promo_codes",
    )


class AvailableUsers(Base):
    __tablename__ = "available_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    available_for_users_id = Column(Integer, ForeignKey("available_for_users.id"))


class AvailableGroups(Base):
    __tablename__ = "available_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    available_for_users_id = Column(Integer, ForeignKey("available_for_users.id"))
