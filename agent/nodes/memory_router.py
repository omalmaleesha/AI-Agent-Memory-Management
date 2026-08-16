# Its job is:
# Decide which memories are actually needed.
# For example:
# "What technologies do I use?"
# → sematic
# or:
# "What did we discuss yesterday?"
# → episodic
# or:
# "How should I deploy this application?"
# → proceural


# app/agent/nodes/memory_router.py

from typing import Literal
from pydantic import BaseModel
from agent.state import AgentState


class MemoryRouting(BaseModel):

    required_memories: list[
        Literal[
            "semantic",
            "episodic",
            "procedural"
        ]
    ]


def memory_router_node(state: AgentState,llm) -> dict:

    user_input = state["user_input"]
    structured_llm = llm.with_structured_output(
        MemoryRouting
    )
    result = structured_llm.invoke(
        f"""
You are a memory routing system.

Determine which types of memory are useful
for answering the user's request.

Memory types:

semantic:
Durable facts, preferences, profile information,
skills and knowledge about the user.

episodic:
Past conversations, previous events,
previous tasks and historical interactions.

procedural:
Instructions, workflows, rules and
how-to knowledge.

User request:
{user_input}

Select only the memory types that are actually
useful.
"""
    )

    return {
        "required_memories": result.required_memories
    }