# app/agent/nodes/memory_retriever.py
from agent.state import AgentState


def memory_retriever_node(state: AgentState,memory_manager) -> dict:

    user_id = state["user_id"]
    user_input = state["user_input"]

    required_memories = state.get(
        "required_memories",
        []
    )

    semantic_memories = []
    episodic_memories = []
    procedural_memories = []

    if "semantic" in required_memories:

        semantic_memories = (
            memory_manager.search_semantic_memory(
                user_id=user_id,
                query=user_input,
                top_k=5
            )
        )

    if "episodic" in required_memories:

        episodic_memories = (
            memory_manager.search_episodic_memory(
                user_id=user_id,
                query=user_input,
                top_k=5
            )
        )

    if "procedural" in required_memories:

        procedural_memories = (
            memory_manager.search_procedural_memory(
                user_id=user_id,
                query=user_input,
                top_k=5
            )
        )

    return {
        "semantic_memories": semantic_memories,
        "episodic_memories": episodic_memories,
        "procedural_memories": procedural_memories
    }