from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount = Column(Float)
    is_active = Column(Boolean, default=True)
    expiry_date = Column(DateTime, default=datetime.utcnow)


class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tariff_id = Column(Integer, ForeignKey("tariffs.id"))
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), nullable=True)
    total_price = Column(Float)
    purchase_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="purchases")
    tariff = relationship("Tariff")
    promo_code = relationship("PromoCode")


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


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)

    users = relationship("User", back_populates="group")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"))
    usage_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    promo_code = relationship("PromoCode")
