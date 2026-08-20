from typing import Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

MemoryType = Literal[
    "semantic",
    "episodic",
    "procedural"
]

class AgentState(TypedDict):
    user_id: str
    session_id: str
    user_input: str

    #Conversation 
    messages: Annotated[list[BaseMessage], add_messages]

    #Memory Routing 
    required_memories: list[MemoryType]

    #Retrieved Memories 
    semantic_memories: list[dict]
    episodic_memories: list[dict]
    procedural_memories: list[dict]

    #Working Context
    context: str

    #Agent 
    response: str

    #Memory Writing 
    extracted_memories: list[dict]

    #Control 
    should_save_memory: bool
