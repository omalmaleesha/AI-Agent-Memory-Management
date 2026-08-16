# app/agent/nodes/memory_writer.py

from agent.state import AgentState


def memory_writer_node(
    state: AgentState,
    memory_manager
) -> dict:

    if not state.get(
        "should_save_memory",
        False
    ):
        return {}

    memories = state.get(
        "extracted_memories",
        []
    )

    user_id = state["user_id"]
    session_id = state["session_id"]

    for memory in memories:

        memory_manager.store_memory(
            user_id=user_id,
            session_id=session_id,
            memory_type=memory["type"],
            content=memory["content"],
            importance=memory["importance"],
            confidence=memory["confidence"]
        )

    return {}