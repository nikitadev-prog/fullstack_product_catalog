from aiogram.fsm.storage.base import BaseStorage, StorageKey


class StatelessStorage(BaseStorage):
    # Диалог не храним: товар приходит одним сообщением, реплики бота друг другу не нужны.

    async def set_state(self, key: StorageKey, state=None) -> None:
        return None

    async def get_state(self, key: StorageKey):
        return None

    async def set_data(self, key: StorageKey, data) -> None:
        return None

    async def get_data(self, key: StorageKey):
        return {}

    async def close(self) -> None:
        return None
