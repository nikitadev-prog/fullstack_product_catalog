import secrets
from uuid import UUID, uuid4

from fastapi import Depends, Header, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import VisitorSession

COOKIE = "sid"


async def require_token(x_internal_token: str = Header()) -> None:
    if not secrets.compare_digest(x_internal_token, settings.internal_token):
        raise HTTPException(status_code=401, detail="Нет доступа")


async def get_sid(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> UUID:
    response.headers["Cache-Control"] = "no-store"
    raw = request.cookies.get(COOKIE) or request.headers.get("x-session-id")
    sid: UUID | None = None
    if raw:
        try:
            sid = UUID(raw)
        except ValueError:
            sid = None
    if sid is not None and await db.get(VisitorSession, sid):
        response.headers["X-Session-Id"] = str(sid)
        return sid

    sid = uuid4()
    db.add(VisitorSession(id=sid))
    await db.commit()
    response.set_cookie(
        COOKIE,
        str(sid),
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )
    response.headers["X-Session-Id"] = str(sid)
    return sid
