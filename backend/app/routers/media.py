import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.s3 import get_image

router = APIRouter(tags=["media"])
KEY = re.compile(r"^[a-f0-9]{32}\.(jpg|png|webp|gif)$")


@router.get("/media/{key}")
async def media(key: str):
    if not KEY.match(key):
        raise HTTPException(status_code=404, detail="Нет файла")
    try:
        data, content_type = await get_image(key)
    except Exception:
        raise HTTPException(status_code=404, detail="Нет файла")
    return Response(content=data, media_type=content_type, headers={"Cache-Control": "public, max-age=86400"})
