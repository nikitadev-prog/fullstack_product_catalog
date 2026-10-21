from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import require_token
from app.schemas import ProductOut
from app.services import products as product_service
from app.s3 import image_url

router = APIRouter(prefix="/products", tags=["products"])


def _out(product) -> ProductOut:
    return ProductOut(id=product.id, name=product.name, image_url=image_url(product.image_key))


@router.get("", response_model=list[ProductOut])
async def list_products(db: AsyncSession = Depends(get_db)):
    rows = await product_service.list_products(db)
    return [_out(row) for row in rows]


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    product = await product_service.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return _out(product)


@router.post("", response_model=ProductOut)
async def create_product(
    name: str = Form(),
    file: UploadFile = File(),
    _: None = Depends(require_token),
    db: AsyncSession = Depends(get_db),
):
    data = await file.read()
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    try:
        product = await product_service.create_product(db, name, data, content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _out(product)
