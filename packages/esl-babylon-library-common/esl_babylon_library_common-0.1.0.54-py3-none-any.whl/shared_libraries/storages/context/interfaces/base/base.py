from abc import ABC, abstractmethod
from typing import Any

from shared_libraries.storages.context.models.share import Context


class BaseContext(ABC):
    @abstractmethod
    def add(self, data: Context) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def remove(self, key: str) -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def search(query: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def a_add(self, data: Context) -> None:
        raise NotImplementedError

    @abstractmethod
    async def a_get(self, key: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    async def a_remove(self, key: str) -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def a_search(query: str) -> str:
        raise NotImplementedError
