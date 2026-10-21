import httpx

from app.config import settings


async def create_product(name: str, data: bytes, content_type: str) -> dict:
    url = settings.api_url.rstrip("/") + "/products"
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            data={"name": name},
            files={"file": ("photo.jpg", data, content_type)},
            headers={"X-Internal-Token": settings.internal_token},
        )
    if response.status_code >= 400:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except Exception:
            pass
        raise RuntimeError(str(detail))
    return response.json()
