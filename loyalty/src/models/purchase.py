from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)


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
