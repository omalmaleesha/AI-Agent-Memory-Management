# app/agent/nodes/agent.py

from agent.state import AgentState


def agent_node(
    state: AgentState,
    llm
) -> dict:

    user_input = state["user_input"]

    context = state.get(
        "context",
        ""
    )

    messages = state.get(
        "messages",
        []
    )

    prompt = f"""
You are an AI assistant with long-term memory.

Use the provided memory only when it is
relevant to the user's request.

Do not mention the internal memory system
unless the user explicitly asks about it.

MEMORY CONTEXT:

{context}

USER REQUEST:

{user_input}
"""

    response = llm.invoke(prompt)

    return {
        "response": response.content
    }