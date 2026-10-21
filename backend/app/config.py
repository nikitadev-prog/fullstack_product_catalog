from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    database_url: str = "postgresql+asyncpg://shop:shop@localhost:5432/shop"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minio"
    minio_secret_key: str = "minio12345"
    minio_bucket: str = "products"
    minio_secure: bool = False
    minio_public_url: str = "http://localhost:9000"
    internal_token: str = "devtoken"
    cookie_secure: bool = False


settings = Settings()
