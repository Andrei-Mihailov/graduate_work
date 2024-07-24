from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    promo_code_id = Column(Integer, ForeignKey("promocodes.id"))
    usage_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    promo_code = relationship("Promocode")
