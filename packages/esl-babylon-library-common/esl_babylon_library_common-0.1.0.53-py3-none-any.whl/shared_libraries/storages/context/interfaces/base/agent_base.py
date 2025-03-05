import threading
from abc import ABC, abstractmethod
from typing import Any

from shared_libraries.storages.context.interfaces.base.base import BaseContext


class BaseAgentContext(BaseContext, ABC):
    _thread_locals = threading.local()

    def __init__(self):
        self.current_context = None
        self.context = dict()

    @abstractmethod
    def add(self, data: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def a_add(self, data: dict[str, Any]) -> None:
        raise NotImplementedError

    def set_current_context(self, current_context_key: str) -> None:
        raise NotImplementedError

    @staticmethod
    def clear_current_context() -> None:
        raise NotImplementedError

    @staticmethod
    def get_current_task_context() -> str:
        raise NotImplementedError
