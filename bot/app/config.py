from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    bot_token: str = ""
    admin_ids: str = ""
    api_url: str = "http://api:8000"
    internal_token: str = "devtoken"
    webapp_url: str = "http://localhost"
    bot_mode: str = "polling"
    webhook_base: str = ""

    def admin_set(self) -> set[int]:
        ids: set[int] = set()
        for part in self.admin_ids.split(","):
            part = part.strip()
            if not part:
                continue
            ids.add(int(part))
        return ids


settings = Settings()
