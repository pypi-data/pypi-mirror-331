from typing import Any

from pydantic import BaseModel


class Context(BaseModel):
    agent_id: int | str
    context: dict[str, Any]
