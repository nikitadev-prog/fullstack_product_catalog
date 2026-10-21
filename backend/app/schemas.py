from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ProductOut(BaseModel):
    id: UUID
    name: str
    image_url: str


class CartItemIn(BaseModel):
    product_id: UUID
    qty: int = Field(default=1, ge=1, le=99)


class QtyIn(BaseModel):
    qty: int = Field(ge=0, le=99)


class CartItemOut(BaseModel):
    product_id: UUID
    name: str
    image_url: str
    qty: int


class CartOut(BaseModel):
    items: list[CartItemOut]


class CheckoutIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=5, max_length=30)

    @field_validator("name", "phone")
    @classmethod
    def strip(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("пусто")
        return value


class OrderItemOut(BaseModel):
    name: str
    qty: int


class OrderOut(BaseModel):
    id: UUID
    customer_name: str
    phone: str
    items: list[OrderItemOut]
