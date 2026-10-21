from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.s3 import put_image, remove_image

ALLOWED_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}
MAX_IMAGE_BYTES = 8 * 1024 * 1024


async def list_products(db: AsyncSession) -> list[Product]:
    result = await db.execute(select(Product).order_by(Product.created_at.desc()))
    return list(result.scalars().all())


async def get_product(db: AsyncSession, product_id: UUID) -> Product | None:
    return await db.get(Product, product_id)


async def create_product(
    db: AsyncSession,
    name: str,
    data: bytes,
    content_type: str,
) -> Product:
    name = name.strip()
    if not name or len(name) > 200:
        raise ValueError("Название: от 1 до 200 символов")
    if content_type == "image/jpg":
        content_type = "image/jpeg"
    ext = ALLOWED_TYPES.get(content_type)
    if ext is None:
        raise ValueError("Нужна картинка jpeg, png, webp или gif")
    if not data:
        raise ValueError("Пустой файл")
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError("Файл больше 8 МБ")

    key = f"{uuid4().hex}.{ext}"
    await put_image(key, data, content_type)
    product = Product(name=name, image_key=key)
    db.add(product)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        await remove_image(key)
        raise
    await db.refresh(product)
    return product
