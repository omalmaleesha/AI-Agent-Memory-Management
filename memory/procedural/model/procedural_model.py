# app/memory/models/procedural.py
from pydantic import BaseModel

class ProceduralMemory(BaseModel):
    id: str
    name: str
    description: str
    source: str
    content: str
    version: str = "1.0"
    enabled: bool = True