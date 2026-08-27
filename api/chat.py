from fastapi import APIRouter
from pydantic import BaseModel
from neo4j.exceptions import ServiceUnavailable
from agent.graph import agent_graph
from llm.llm import llm_service

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("",response_model=ChatResponse)
def chat(request: ChatRequest):
    initial_state = {
        "user_id": request.user_id,
        "session_id": request.session_id,
        "user_input": request.message,
        "messages": [],
        "required_memories": [],
        "semantic_memories": [],
        "episodic_memories": [],
        "procedural_memories": [],
        "context": "",
        "response": "",
        "extracted_memories": [],
        "should_save_memory": False
    }

    try:
        result = agent_graph.invoke(
            initial_state
        )

        return ChatResponse(
            response=result["response"]
        )

    except ServiceUnavailable:
        fallback = llm_service.invoke(
            request.message
        )

        return ChatResponse(
            response=getattr(
                fallback,
                "content",
                str(fallback)
            )
        )