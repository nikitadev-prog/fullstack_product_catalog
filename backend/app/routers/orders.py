from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_sid
from app.schemas import CheckoutIn, OrderOut
from app.services import orders as order_service

router = APIRouter(prefix="/orders", tags=["orders"])


def _out(order) -> OrderOut:
    return OrderOut(
        id=order.id,
        customer_name=order.customer_name,
        phone=order.phone,
        items=[{"name": item.name, "qty": item.qty} for item in order.items],
    )


@router.post("", response_model=OrderOut)
async def checkout(
    body: CheckoutIn,
    sid: UUID = Depends(get_sid),
    db: AsyncSession = Depends(get_db),
):
    order = await order_service.checkout(db, sid, body.name, body.phone)
    if order is None:
        raise HTTPException(status_code=400, detail="Корзина пуста")
    return _out(order)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: UUID,
    sid: UUID = Depends(get_sid),
    db: AsyncSession = Depends(get_db),
):
    order = await order_service.get_order(db, sid, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return _out(order)
