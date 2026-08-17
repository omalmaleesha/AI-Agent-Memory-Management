from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application
    APP_NAME: str = "AI Memory System"
    DEBUG: bool = True

    # Neo4j
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str

    # Groq
    GROQ_API_KEY: str 
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Embedding
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Memory
    SEMANTIC_MEMORY_TOP_K: int = 5
    EPISODIC_MEMORY_TOP_K: int = 5
    PROCEDURAL_MEMORY_TOP_K: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()