# app/memory/models/episodic.py

from datetime import datetime
from pydantic import BaseModel, Field


class EpisodicMemory(BaseModel):

    id: str

    user_id: str

    session_id: str

    content: str

    timestamp: datetime

    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0
    )

    embedding: list[float] | None = None

    conversation_id: str | None = None