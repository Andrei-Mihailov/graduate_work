from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PromoCodeBase(BaseModel):
    code: str
    discount: float
    is_active: Optional[bool] = True
    expiry_date: Optional[datetime] = None


class PromoCodeCreate(PromoCodeBase):
    pass


class PromoCode(PromoCodeBase):
    id: int

    class Config:
        orm_mode = True


class TariffBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None


class TariffCreate(TariffBase):
    pass


class Tariff(TariffBase):
    id: int

    class Config:
        orm_mode = True


class PurchaseBase(BaseModel):
    user_id: int
    tariff_id: int
    promo_code_id: Optional[int] = None
    total_price: float


class PurchaseCreate(PurchaseBase):
    pass


class Purchase(PurchaseBase):
    id: int
    purchase_date: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: Optional[bool] = True
    group_id: Optional[int] = None

    class Config:
        orm_mode = True


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class Group(GroupBase):
    id: int

    class Config:
        orm_mode = True
