from typing import Any
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

    # INDIVIDUAL MEMORY SEARCH
    def search_semantic_memory(
        self,
        user_id: str,
        query: str,
        limit: int = 2,
        top_k: int | None = None,
    ):
        if top_k is not None:
            limit = top_k

        return self.semantic.search(
            user_id=user_id,
            query=query,
            limit=limit,
        )

    def search_episodic_memory(
        self,
        user_id: str,
        query: str,
        limit: int = 2,
        top_k: int | None = None,
    ):
        if top_k is not None:
            limit = top_k

        return self.episodic.search(
            user_id=user_id,
            query=query,
            limit=limit,
        )

    def search_procedural_memory(
        self,
        user_id: str,
        query: str,
        limit: int = 2,
        top_k: int | None = None,
    ):
        if top_k is not None:
            limit = top_k

        return self.procedural.search(
            user_id=user_id,
            query=query,
            limit=limit,
        )

    # MULTI MEMORY RETRIEVAL
    def search_all_memories(
        self,
        user_id: str,
        query: str,
        limit_per_memory: int = 2,
    ) -> dict[str, list]:

        print("\n" + "=" * 70)
        print("[MULTI MEMORY SEARCH START]")
        print("=" * 70)

        results = {
            "semantic": [],
            "episodic": [],
            "procedural": [],
        }

        try:
            print("[SEMANTIC SEARCH START]")

            results["semantic"] = self.search_semantic_memory(
                user_id=user_id,
                query=query,
                limit=limit_per_memory,
            ) or []

            print(
                f"[SEMANTIC SEARCH SUCCESS] "
                f"count={len(results['semantic'])}"
            )

        except Exception as e:
            print(f"[SEMANTIC SEARCH ERROR] {repr(e)}")


        try:
            print("[EPISODIC SEARCH START]")

            results["episodic"] = self.search_episodic_memory(
                user_id=user_id,
                query=query,
                limit=limit_per_memory,
            ) or []

            print(
                f"[EPISODIC SEARCH SUCCESS] "
                f"count={len(results['episodic'])}"
            )

        except Exception as e:
            print(f"[EPISODIC SEARCH ERROR] {repr(e)}")

        try:
            print("[PROCEDURAL SEARCH START]")

            results["procedural"] = self.search_procedural_memory(
                user_id=user_id,
                query=query,
                limit=limit_per_memory,
            ) or []

            print(
                f"[PROCEDURAL SEARCH SUCCESS] "
                f"count={len(results['procedural'])}"
            )

        except Exception as e:
            print(f"[PROCEDURAL SEARCH ERROR] {repr(e)}")

        print("[MULTI MEMORY SEARCH COMPLETE]")

        return results
    
    # MEMORY SCORING
    def score_memories(
        self,
        memories: dict[str, list],
    ) -> list[dict[str, Any]]:

        print("\n" + "=" * 70)
        print("[MEMORY SCORING START]")
        print("=" * 70)

        scored_memories = []

        # Different memory types can have different importance.
        #
        # These are initial weights.
        # Later you can learn/tune these weights.

        memory_type_weights = {
            "semantic": 1.0,
            "episodic": 0.9,
            "procedural": 1.1,
        }

        for memory_type, items in memories.items():

            for item in items:
                similarity = self._get_score(
                    item,
                    "similarity",
                    default=0.0,
                )
                importance = self._get_score(
                    item,
                    "importance",
                    default=0.5,
                )
                confidence = self._get_score(
                    item,
                    "confidence",
                    default=0.5,
                )
                recency = self._get_score(
                    item,
                    "recency",
                    default=0.5,
                )
                type_weight = memory_type_weights.get(
                    memory_type,
                    1.0,
                )

                final_score = (
                    similarity * 0.50
                    + importance * 0.20
                    + confidence * 0.15
                    + recency * 0.15
                ) * type_weight

                scored_memories.append(
                    {
                        "memory_type": memory_type,
                        "memory": item,
                        "similarity": similarity,
                        "importance": importance,
                        "confidence": confidence,
                        "recency": recency,
                        "type_weight": type_weight,
                        "score": final_score,
                    }
                )

        print(
            f"[MEMORY SCORING COMPLETE] "
            f"candidates={len(scored_memories)}"
        )

        return scored_memories
    
    # MEMORY STORAGE

    def store_memory(
        self,
        user_id: str,
        memory_type: str,
        content: str,
        session_id: str | None = None,
        importance: str | None = None,
        confidence: str | None = None,
    ):

        print("\n" + "=" * 70)
        print("[MEMORY STORAGE START]")
        print("=" * 70)


        try:
            if memory_type == "semantic":

                result = self.semantic.create(
                    user_id=user_id,
                    content=content,
                    importance=importance,
                    confidence=confidence,
                    check_duplicate=True,
                )
                
            elif memory_type == "episodic":

                result = self.episodic.create(
                    user_id=user_id,
                    session_id=session_id,
                    content=content,
                    importance=importance,
                    confidence=confidence,
                    check_duplicate=True,
                )

            elif memory_type == "procedural":

                result = self.procedural.store(
                    user_id=user_id,
                    content=content,
                )

            else:

                raise ValueError(
                    f"Unsupported memory type: {memory_type}"
                )

            print(
                f"[MEMORY STORAGE SUCCESS] "
                f"type={memory_type} "
                f"user_id={user_id}"
            )

            print("=" * 70)

            return result

        except Exception as e:

            print(
                f"[MEMORY STORAGE ERROR] "
                f"type={memory_type} "
                f"error={repr(e)}"
            )

            raise

    # MEMORY FUSION

    def fuse_memories(
        self,
        scored_memories: list[dict[str, Any]],
        top_k: int = 2,
    ) -> list[dict[str, Any]]:

        print("\n" + "=" * 70)
        print("[MEMORY FUSION START]")
        print("=" * 70)

        # Highest score first

        ranked = sorted(
            scored_memories,
            key=lambda x: x["score"],
            reverse=True,
        )

        fused = ranked[:top_k]

        for index, memory in enumerate(fused, start=1):

            print(
                f"[FUSED MEMORY {index}] "
                f"type={memory['memory_type']} "
                f"score={memory['score']:.4f}"
            )

        print(
            f"[MEMORY FUSION COMPLETE] "
            f"selected={len(fused)}"
        )

        return fused

    # COMPLETE MEMORY RETRIEVAL PIPELINE

    def retrieve(
        self,
        user_id: str,
        query: str,
        limit_per_memory: int = 5,
        top_k: int = 8,
    ) -> list[dict[str, Any]]:

        print("\n")
        print("#" * 70)
        print("[MEMORY RETRIEVAL PIPELINE START]")
        print("#" * 70)

        # 1. Search all memory systems

        memories = self.search_all_memories(
            user_id=user_id,
            query=query,
            limit_per_memory=limit_per_memory,
        )

        # 2. Score candidates

        scored = self.score_memories(
            memories
        )

        # 3. Fuse and rank

        fused = self.fuse_memories(
            scored,
            top_k=top_k,
        )

        print("#" * 70)
        print("[MEMORY RETRIEVAL PIPELINE COMPLETE]")
        print("#" * 70)

        return fused

    # HELPERS

    @staticmethod
    def _get_score(
        item: Any,
        key: str,
        default: float = 0.0,
    ) -> float:

        if isinstance(item, dict):
            value = item.get(key, default)

        else:
            value = getattr(
                item,
                key,
                default,
            )

        try:
            value = float(value)
        except (TypeError, ValueError):
            value = default

        # Keep scores between 0 and 1

        return max(
            0.0,
            min(1.0, value),
        )


    # INITIALIZATION

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