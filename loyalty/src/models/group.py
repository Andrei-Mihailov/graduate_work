from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from .base import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)

    users = relationship("User", back_populates="group")
