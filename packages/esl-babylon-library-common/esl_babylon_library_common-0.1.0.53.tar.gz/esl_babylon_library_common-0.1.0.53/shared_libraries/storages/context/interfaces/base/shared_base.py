from abc import ABC
from typing import Any

from shared_libraries.storages.context.interfaces.base.base import BaseContext
from shared_libraries.storages.context.models.share import Context


class BaseSharedContext(BaseContext, ABC):
    """
    Mixin class, which stands as a layer
    between BaseContext and SomeConcreteInterface.
    """

    CONTEXT_KEY: str | None = None

    def __init__(self, context_key: str) -> None:
        self.__class__.CONTEXT_KEY = context_key

    @staticmethod
    def merge_contexts(shared_context: dict[str, Any], context: Context) -> dict:
        """
        Method, which merges agents' shared and agents' current contexts.
        Args:
            shared_context: data from all agents from remote shared context (redis)
            context: concrete agents' current context
        """
        agent_id = context.agent_id
        ctx_exists_in_remote = agent_id in shared_context
        new_context = context.context

        if ctx_exists_in_remote:
            historical = shared_context[agent_id]
            historical.update(new_context)
            payload = historical
        else:
            payload = context.context

        shared_context[agent_id] = new_context
        return shared_context
