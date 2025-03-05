from typing import Type

from shared_libraries.storages.context.interfaces.base.agent_base import BaseAgentContext
from shared_libraries.storages.context.interfaces.base.shared_base import BaseSharedContext


class Context:
    """Unified context"""

    MY_CONTEXT: Type[BaseAgentContext] | None = None
    SHARED_CONTEXT: Type[BaseSharedContext] | None = None

    def __init__(self, agent_context: BaseAgentContext, shared_context: BaseSharedContext):
        self.agent_context = agent_context
        self.shared_context = shared_context
        self.__class__.MY_CONTEXT = type(agent_context)
        self.__class__.SHARED_CONTEXT = type(shared_context)

    @staticmethod
    def my() -> Type[BaseAgentContext]:
        return Context.MY_CONTEXT

    @staticmethod
    def shared() -> Type[BaseSharedContext]:
        return Context.SHARED_CONTEXT

    @staticmethod
    async def search(query: str):
        shared_results = await Context.shared().search(query)
        agent_results = await Context.my().search(query)

        return f"Results from shared context: {shared_results}\nResults from agent context: {agent_results}"
