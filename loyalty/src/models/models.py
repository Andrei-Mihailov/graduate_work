from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    DECIMAL,
    ForeignKey,
    TIMESTAMP,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Promocode(Base):
    __tablename__ = "promocodes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    discount_type = Column(String, nullable=False)  # "fixed", "percentage", "trial"
    discount_value = Column(DECIMAL, nullable=False)  # сумма скидки или процент
    expiration_date = Column(Date)
    usage_limit = Column(
        Integer
    )  # ограничение на количество использований (NULL для неограниченного)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")


class PromoUsage(Base):
    __tablename__ = "promo_usage"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    promocode_id = Column(Integer, ForeignKey("promocodes.id"), nullable=False)
    used_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    is_successful = Column(Boolean, default=False)

    promocode = relationship("Promocode", back_populates="usages")


Promocode.usages = relationship(
    "PromoUsage", order_by=PromoUsage.id, back_populates="promocode"
)
