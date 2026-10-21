from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import CartItem, Order, OrderItem
from app.services.cart import list_lines


async def checkout(db: AsyncSession, session_id: UUID, name: str, phone: str) -> Order | None:
    lines = await list_lines(db, session_id)
    if not lines:
        return None

    order = Order(id=uuid4(), session_id=session_id, customer_name=name, phone=phone)
    db.add(order)
    await db.flush()
    for line in lines:
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=line.product_id,
                name=line.name,
                qty=line.qty,
            )
        )
    await db.execute(delete(CartItem).where(CartItem.session_id == session_id))
    await db.commit()

    result = await db.execute(select(Order).options(selectinload(Order.items)).where(Order.id == order.id))
    return result.scalar_one()


async def get_order(db: AsyncSession, session_id: UUID, order_id: UUID) -> Order | None:
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id, Order.session_id == session_id)
    )
    return result.scalar_one_or_none()
