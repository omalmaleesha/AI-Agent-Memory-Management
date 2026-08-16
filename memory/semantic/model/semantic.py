# app/memory/models/semantic.py

from datetime import datetime
from pydantic import BaseModel, Field


class SemanticMemory(BaseModel):

    id: str

    user_id: str

    content: str

    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0
    )

    created_at: datetime

    updated_at: datetime

    last_accessed_at: datetime | None = None

    access_count: int = 0

    embedding: list[float] | None = None