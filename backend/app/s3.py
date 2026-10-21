import asyncio
import io
import json

from minio import Minio
from minio.error import S3Error

from app.config import settings


def client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def image_url(key: str) -> str:
    # Тот же адрес, что у сайта. Иначе Mini App на https не показывает картинку с localhost.
    return f"/api/media/{key}"


async def get_image(key: str) -> tuple[bytes, str]:
    def _get() -> tuple[bytes, str]:
        obj = client().get_object(settings.minio_bucket, key)
        try:
            data = obj.read()
            content_type = obj.headers.get("Content-Type", "image/jpeg")
        finally:
            obj.close()
            obj.release_conn()
        return data, content_type

    return await asyncio.to_thread(_get)


async def put_image(key: str, data: bytes, content_type: str) -> None:
    def _put() -> None:
        client().put_object(
            settings.minio_bucket,
            key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    await asyncio.to_thread(_put)


async def remove_image(key: str) -> None:
    def _remove() -> None:
        client().remove_object(settings.minio_bucket, key)

    await asyncio.to_thread(_remove)


def ensure_bucket() -> None:
    s3 = client()
    bucket = settings.minio_bucket
    if not s3.bucket_exists(bucket):
        try:
            s3.make_bucket(bucket)
        except S3Error:
            if not s3.bucket_exists(bucket):
                raise
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket}/*"],
            }
        ],
    }
    s3.set_bucket_policy(bucket, json.dumps(policy))


async def wait_for_bucket() -> None:
    delay = 1
    last: Exception | None = None
    for _ in range(20):
        try:
            await asyncio.to_thread(ensure_bucket)
            return
        except Exception as exc:
            last = exc
            await asyncio.sleep(delay)
            delay = min(delay * 2, 5)
    raise RuntimeError("MinIO не поднялся") from last
