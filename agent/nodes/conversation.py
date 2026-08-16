# app/agent/nodes/conversation.py

from langchain_core.messages import HumanMessage

from agent.state import AgentState


def conversation_node(state: AgentState) -> dict:
    user_input = state["user_input"]

    messages = state.get("messages", [])

    return {
        "messages": [
            HumanMessage(content=user_input)
        ]
    }