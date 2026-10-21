from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CartItem, Product


@dataclass
class CartLine:
    product_id: UUID
    name: str
    image_key: str
    qty: int


async def list_lines(db: AsyncSession, session_id: UUID) -> list[CartLine]:
    stmt = (
        select(CartItem, Product)
        .join(Product, Product.id == CartItem.product_id)
        .where(CartItem.session_id == session_id)
        .order_by(Product.name)
    )
    rows = (await db.execute(stmt)).all()
    return [
        CartLine(product_id=product.id, name=product.name, image_key=product.image_key, qty=item.qty)
        for item, product in rows
    ]


async def add_item(db: AsyncSession, session_id: UUID, product_id: UUID, qty: int) -> None:
    product = await db.get(Product, product_id)
    if product is None:
        raise LookupError("Товар не найден")
    item = await db.get(CartItem, (session_id, product_id))
    if item is None:
        db.add(CartItem(session_id=session_id, product_id=product_id, qty=qty))
    else:
        item.qty = min(99, item.qty + qty)
    await db.commit()


async def set_qty(db: AsyncSession, session_id: UUID, product_id: UUID, qty: int) -> None:
    if qty < 1:
        await db.execute(
            delete(CartItem).where(
                CartItem.session_id == session_id,
                CartItem.product_id == product_id,
            )
        )
        await db.commit()
        return
    item = await db.get(CartItem, (session_id, product_id))
    if item is None:
        raise LookupError("В корзине нет такого товара")
    item.qty = qty
    await db.commit()


async def remove_item(db: AsyncSession, session_id: UUID, product_id: UUID) -> None:
    await db.execute(
        delete(CartItem).where(
            CartItem.session_id == session_id,
            CartItem.product_id == product_id,
        )
    )
    await db.commit()
