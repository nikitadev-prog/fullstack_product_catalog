from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app import models  # noqa: F401
from app.db import engine
from app.models import Base
from app.routers import cart, media, orders, products
from app.s3 import wait_for_bucket


@asynccontextmanager
async def lifespan(app: FastAPI):
    await wait_for_bucket()
    async with engine.begin() as conn:
        # Две реплики на старте не должны создавать таблицы одновременно.
        await conn.execute(text("SELECT pg_advisory_xact_lock(842610)"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Каталог", lifespan=lifespan)
app.include_router(products.router)
app.include_router(media.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/health")
async def health():
    return {"ok": True}
