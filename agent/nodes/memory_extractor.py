# app/agent/nodes/memory_extractor.py

from typing import Literal

from pydantic import BaseModel, Field

from agent.state import AgentState


class ExtractedMemory(BaseModel):

    type: Literal[
        "semantic",
        "episodic",
        "procedural"
    ]

    content: str

    importance: float = Field(
        ge=0.0,
        le=1.0
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )


class MemoryExtraction(BaseModel):

    should_save: bool

    memories: list[ExtractedMemory]


def memory_extractor_node(state: AgentState,llm) -> dict:

    user_input = state["user_input"]

    response = state["response"]

    structured_llm = llm.with_structured_output(
        MemoryExtraction
    )

    result = structured_llm.invoke(
        f"""
You are a memory extraction system.

Determine whether this conversation contains
information worth storing for future interactions.

Store durable information such as:

- user preferences
- user profile information
- important facts
- long-term goals
- important events
- reusable procedures
- important decisions

Do NOT store:

- casual conversation
- temporary questions
- greetings
- generic information
- information that has no future value

USER:
{user_input}

ASSISTANT:
{response}
"""
    )

    return {
        "should_save_memory": result.should_save,
        "extracted_memories": [
            memory.model_dump()
            for memory in result.memories
        ]
    }