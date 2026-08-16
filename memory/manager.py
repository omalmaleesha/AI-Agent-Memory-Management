from database.neo4j import Neo4jClient

from memory.semantic.memory.semantic import SemanticMemoryManager
from memory.episodic.memory.episodic import EpisodicMemoryManager
from memory.procedural.memory.procedural import ProceduralMemoryManager


class MemoryManager:

    def __init__(
        self,
        semantic_manager: SemanticMemoryManager,
        episodic_manager: EpisodicMemoryManager,
        procedural_manager: ProceduralMemoryManager,
    ):
        self.semantic = semantic_manager
        self.episodic = episodic_manager
        self.procedural = procedural_manager

    # =========================================================
    # SEMANTIC MEMORY
    # =========================================================

    def search_semantic_memory(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        top_k: int | None = None,
    ):
        if top_k is not None:
            limit = top_k

        return self.semantic.search(
            user_id=user_id,
            query=query,
            limit=limit,
        )

    # =========================================================
    # EPISODIC MEMORY
    # =========================================================

    def search_episodic_memory(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        top_k: int | None = None,
    ):
        if top_k is not None:
            limit = top_k

        return self.episodic.search(
            user_id=user_id,
            query=query,
            limit=limit,
        )

    # =========================================================
    # PROCEDURAL MEMORY
    # =========================================================

    def search_procedural_memory(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        top_k: int | None = None,
    ):
        if top_k is not None:
            limit = top_k

        return self.procedural.search(
            user_id=user_id,
            query=query,
            limit=limit,
        )


# =============================================================
# INITIALIZATION
# =============================================================

neo4j_client = Neo4jClient()

semantic_manager = SemanticMemoryManager(
    neo4j_client
)

episodic_manager = EpisodicMemoryManager(
    neo4j_client
)

procedural_manager = ProceduralMemoryManager(
    neo4j_client
)


memory_manager = MemoryManager(
    semantic_manager=semantic_manager,
    episodic_manager=episodic_manager,
    procedural_manager=procedural_manager,
)