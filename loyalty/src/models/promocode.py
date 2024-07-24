from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from datetime import datetime
from .base import Base

class Promocode(Base):
    __tablename__ = 'promocodes'
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount_type = Column(String)
    discount_value = Column(Integer)
    is_active = Column(Boolean, default=True)
    usage_limit = Column(Integer)
    expiration_date = Column(DateTime)
