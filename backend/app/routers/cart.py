from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_sid
from app.s3 import image_url
from app.schemas import CartItemIn, CartOut, QtyIn
from app.services import cart as cart_service
from app.services.cart import CartLine

router = APIRouter(prefix="/cart", tags=["cart"])


def _out(lines: list[CartLine]) -> CartOut:
    return CartOut(
        items=[
            {
                "product_id": line.product_id,
                "name": line.name,
                "image_url": image_url(line.image_key),
                "qty": line.qty,
            }
            for line in lines
        ]
    )


@router.get("", response_model=CartOut)
async def get_cart(sid: UUID = Depends(get_sid), db: AsyncSession = Depends(get_db)):
    return _out(await cart_service.list_lines(db, sid))


@router.post("/items", response_model=CartOut)
async def add_item(
    body: CartItemIn,
    sid: UUID = Depends(get_sid),
    db: AsyncSession = Depends(get_db),
):
    try:
        await cart_service.add_item(db, sid, body.product_id, body.qty)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _out(await cart_service.list_lines(db, sid))


@router.patch("/items/{product_id}", response_model=CartOut)
async def set_qty(
    product_id: UUID,
    body: QtyIn,
    sid: UUID = Depends(get_sid),
    db: AsyncSession = Depends(get_db),
):
    try:
        await cart_service.set_qty(db, sid, product_id, body.qty)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _out(await cart_service.list_lines(db, sid))


@router.delete("/items/{product_id}", response_model=CartOut)
async def remove_item(
    product_id: UUID,
    sid: UUID = Depends(get_sid),
    db: AsyncSession = Depends(get_db),
):
    await cart_service.remove_item(db, sid, product_id)
    return _out(await cart_service.list_lines(db, sid))
