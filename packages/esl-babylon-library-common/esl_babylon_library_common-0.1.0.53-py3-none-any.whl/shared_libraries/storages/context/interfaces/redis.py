import enum
import json
from typing import Any

from shared_libraries.core.logger.create_logger import logger
from shared_libraries.storages.cache import redis_async_manager
from shared_libraries.storages.cache.manager import RedisContextManager
from shared_libraries.storages.context.interfaces.base.shared_base import BaseSharedContext
from shared_libraries.storages.context.models.share import Context


class RedisSharedContext(BaseSharedContext):
    """Concrete interface, to communicate with Redis as Shared Context."""

    @staticmethod
    def search(query: str) -> str:
        raise NotImplementedError

    @staticmethod
    async def a_search(query: str) -> str:
        raise NotImplementedError

    CONTEXT_KEY: str | None = None
    redis_async_manager: RedisContextManager | None = None

    def add(self, current_ctx: Context) -> None:
        shared_ctx = self.get_from_shared_context()
        merged_ctx = self.merge_contexts(shared_ctx, current_ctx)

        self.update_at_shared_context(merged_ctx)

    def get(self, key: str) -> dict[str, Any] | None:
        ctx = self.get_from_shared_context()
        return ctx.get(key, None)

    def remove(self, key: str) -> None:
        ctx = self.get_from_shared_context()
        if key in ctx:
            del ctx[key]
            self.update_at_shared_context(ctx)

    async def a_add(self, current_ctx: Context) -> None:
        shared_ctx = await self.a_get_from_shared_context()
        merged_ctx = self.merge_contexts(shared_ctx, current_ctx)

        await self.a_update_at_shared_context(merged_ctx)

    async def a_get(self, key: str) -> dict[str, Any] | None:
        ctx = await self.a_get_from_shared_context()
        return ctx.get(key, None)

    async def a_remove(self, key: str) -> None:
        ctx = await self.a_get_from_shared_context()
        if key in ctx:
            del ctx[key]
            await self.a_update_at_shared_context(ctx)

    @staticmethod
    def get_from_shared_context() -> dict:
        with redis_async_manager as connector:
            ctx = connector.get(RedisSharedContext.CONTEXT_KEY)
        if ctx is None:
            logger.warning(f"Shared context with context key: {RedisSharedContext.CONTEXT_KEY} not found")
            return dict()
        return json.loads(ctx)

    @staticmethod
    def update_at_shared_context(value: dict[str, Any]) -> None:
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict got {type(value)}")
        with redis_async_manager as connector:
            connector.set(
                RedisSharedContext.CONTEXT_KEY,
                json.dumps(value, default=lambda obj: obj.value if isinstance(obj, enum.Enum) else str(obj)),
            )

    @staticmethod
    async def a_get_from_shared_context() -> dict:
        async with redis_async_manager as connector:
            ctx = await connector.get(RedisSharedContext.CONTEXT_KEY)
        if ctx is None:
            logger.warning(f"Shared context with context key: {RedisSharedContext.CONTEXT_KEY} not found")
            return dict()
        return json.loads(ctx)

    @staticmethod
    async def a_update_at_shared_context(value: dict[str, Any]) -> None:
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict got {type(value)}")
        async with redis_async_manager as connector:
            current_context = await RedisSharedContext.a_get_from_shared_context()
            current_context.update(value)
            await connector.set(
                RedisSharedContext.CONTEXT_KEY,
                json.dumps(current_context, default=lambda obj: obj.value if isinstance(obj, enum.Enum) else str(obj)),
            )

    @staticmethod
    async def a_get_ledger() -> list:
        async with redis_async_manager as connector:
            ctx = await connector.lrange(RedisSharedContext.CONTEXT_KEY, 0, -1)
            ctx = [json.loads(item) for item in ctx]
        if ctx is None:
            logger.warning(f"Shared context with context key: {RedisSharedContext.CONTEXT_KEY} not found")
            return []
        return ctx

    @staticmethod
    async def a_update_ledger(value: dict[str, Any]) -> None:
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict got {type(value)}")
        async with redis_async_manager as connector:
            await connector.rpush(
                RedisSharedContext.CONTEXT_KEY,
                json.dumps(value, default=lambda obj: obj.value if isinstance(obj, enum.Enum) else str(obj)),
            )
