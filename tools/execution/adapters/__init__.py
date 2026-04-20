"""Adapters for driving external agent runtimes."""
from tools.execution.adapters.openclaw_adapter import (
    AgentType,
    AgentResponse,
    TaskResult,
    OpenClawAdapter,
    create_adapter,
    load_memory_snapshot,
)

__all__ = [
    "AgentType",
    "AgentResponse",
    "TaskResult",
    "OpenClawAdapter",
    "create_adapter",
    "load_memory_snapshot",
]