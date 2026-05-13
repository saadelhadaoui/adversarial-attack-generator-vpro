from typing import Any

from memory.structured_memory import StructuredMemory
from orchestration.graph import DefenseGraph


_MEMORY: StructuredMemory | None = None
_GRAPH: DefenseGraph | None = None


def _get_memory() -> StructuredMemory:
    global _MEMORY
    if _MEMORY is None:
        _MEMORY = StructuredMemory()
    return _MEMORY


def _get_graph(mode: str = "PROTECTION") -> DefenseGraph:
    global _GRAPH
    memory = _get_memory()
    if _GRAPH is None:
        _GRAPH = DefenseGraph(structured_memory=memory, mode=mode)
    else:
        _GRAPH.set_mode(mode)
    return _GRAPH


def empty_learned_memory() -> dict[str, Any]:
    return {"patterns": {}, "rules": [], "events": []}


def process_chatbot_message(
    message: str,
    source: str = "user",
    chat_history: list[dict[str, Any]] | None = None,
    learned_memory: dict[str, Any] | None = None,
    use_backend_agents: bool = True,
    mode: str = "PROTECTION",
) -> dict[str, Any]:
    graph = _get_graph(mode)
    if source == "attacker_agent":
        return graph.run_attack_round(learned_memory=learned_memory)
    return graph.process_user_message(message, chat_history=chat_history, learned_memory=learned_memory)


def get_learned_patterns() -> list[dict[str, Any]]:
    return _get_memory().get_patterns()


def get_defender_rules() -> list[dict[str, Any]]:
    return _get_memory().get_rules()


def get_metrics() -> dict[str, Any]:
    return _get_memory().get_metrics()


def get_recent_interactions(limit: int = 20) -> list[dict[str, Any]]:
    return _get_memory().get_recent_interactions(limit)


def get_rag_events(limit: int = 50) -> list[dict[str, Any]]:
    return _get_memory().get_rag_events(limit)


def clear_learned_memory() -> bool:
    return _get_memory().clear_learned_memory()
