from sqlalchemy import Column, String, Integer, Boolean, ForeignKey,  DateTime
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    group_id = Column(Integer, ForeignKey("groups.id"))

    purchases = relationship("Purchase", back_populates="user")
    group = relationship("Group", back_populates="users")


class PromoUsage(Base):
    __tablename__ = 'promo_usage'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Предположим, что у вас есть таблица 'users'
    promocode_id = Column(Integer, ForeignKey('promocodes.id'),
                          nullable=False)  # Предположим, что у вас есть таблица 'promocodes'
    is_successful = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    promocode = relationship("Promocode")