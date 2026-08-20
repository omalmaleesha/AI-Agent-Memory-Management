# app/agent/nodes/memory_retriever.py
import time
from agent.state import AgentState
def memory_retriever_node(state: AgentState,memory_manager) -> dict:

    start_time = time.perf_counter()

    print("\n" + "=" * 70)
    print("[NODE START] memory_retriever")
    print("=" * 70)

    try:
        user_id = state["user_id"]
        user_input = state["user_input"]

        required_memories = state.get(
            "required_memories",
            [],
        )

        print(f"[RETRIEVER] user_id={user_id}")
        print(f"[RETRIEVER] query={user_input}")
        print(
            f"[RETRIEVER] required_memories="
            f"{required_memories}"
        )
        print("\n[MULTI MEMORY RETRIEVAL START]")

        # If the router provided required memory types,
        # we use them to decide which memory systems to search.
        # If the router returns an empty list, search all
        # memory types.

        if not required_memories:
            print(
                "[RETRIEVER] Router determined that "
                "no memory is required."
            )
            memories = {
                "semantic": [],
                "episodic": [],
                "procedural": [],
            }

        else:

            memories = {}
            if "semantic" in required_memories:
                memories["semantic"] = (
                    memory_manager.search_semantic_memory(
                        user_id=user_id,
                        query=user_input,
                        top_k=2,
                    )
                    or []
                )

            if "episodic" in required_memories:
                memories["episodic"] = (
                    memory_manager.search_episodic_memory(
                        user_id=user_id,
                        query=user_input,
                        top_k=2,
                    )
                    or []
                )

            if "procedural" in required_memories:
                memories["procedural"] = (
                    memory_manager.search_procedural_memory(
                        user_id=user_id,
                        query=user_input,
                        top_k=2,
                    )
                    or []
                )

        semantic_memories = memories.get(
            "semantic",
            [],
        )

        episodic_memories = memories.get(
            "episodic",
            [],
        )

        procedural_memories = memories.get(
            "procedural",
            [],
        )

        print("\n[RETRIEVAL RESULTS]")
        print(f"semantic={len(semantic_memories)}")
        print(f"episodic={len(episodic_memories)}")
        print(f"procedural={len(procedural_memories)}")
        # SCORE MEMORIES
        print("\n[MEMORY SCORING START]")

        scored_memories = (
            memory_manager.score_memories(
                memories
            )
        )

        print(
            f"[MEMORY SCORING SUCCESS] "
            f"candidates={len(scored_memories)}"
        )
        # MEMORY FUSION
        print("\n[MEMORY FUSION START]")

        fused_memories = (
            memory_manager.fuse_memories(
                scored_memories,
                top_k=2,
            )
        )

        print(
            f"[MEMORY FUSION SUCCESS] "
            f"selected={len(fused_memories)}"
        )
        # PRINT SELECTED MEMORIES

        print("\n[SELECTED MEMORIES]")

        for index, memory in enumerate(
            fused_memories,
            start=1,
        ):

            memory_type = memory.get(
                "memory_type",
                "unknown",
            )

            score = memory.get(
                "score",
                0.0,
            )

            print(
                f"{index}. "
                f"type={memory_type} "
                f"score={score:.4f}"
            )
            
        # SUCCESS

        elapsed = (
            time.perf_counter() - start_time
        )

        print(
            f"\n[NODE SUCCESS] memory_retriever "
            f"time={elapsed:.4f}s"
        )

        print("=" * 70)

        # STATE UPDATE

        return {
            # Original individual memory results
            "semantic_memories": semantic_memories,
            "episodic_memories": episodic_memories,
            "procedural_memories": procedural_memories,
            # New fused/ranked memories
            "scored_memories": scored_memories,
            "retrieved_memories": fused_memories,
        }

    except Exception as e:

        elapsed = (
            time.perf_counter() - start_time
        )
        print(f"\n[NODE ERROR] memory_retriever")
        print(f"[ERROR TYPE] {type(e).__name__}")
        print(f"[ERROR MESSAGE] {str(e)}")
        print(f"[NODE TIME] {elapsed:.4f}s")
        print("=" * 70)

        raise