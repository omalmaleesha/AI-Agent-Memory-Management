# app/agent/nodes/context_builder.py

# Neo4j
#   ↓
# 20 memories
#   ↓
# Ranking
#   ↓
# Context Builder
#   ↓
# 3 useful memories
#   ↓
# LLM

# rather than passing all retrieved memories to the LLM, we can build a context string that includes only the most relevant information. This can help reduce token usage and improve response quality.
from agent.state import AgentState


def context_builder_node(state: AgentState) -> dict:
    sections = []

    semantic_memories = state.get(
        "semantic_memories",
        []
    )

    episodic_memories = state.get(
        "episodic_memories",
        []
    )

    procedural_memories = state.get(
        "procedural_memories",
        []
    )

    if semantic_memories:

        semantic_text = "\n".join(
            f"- {memory['content']}"
            for memory in semantic_memories
        )

        sections.append(
            f"""
SEMANTIC MEMORY:

{semantic_text}
"""
        )

    if episodic_memories:

        episodic_text = "\n".join(
            f"- {memory['content']}"
            for memory in episodic_memories
        )

        sections.append(
            f"""
EPISODIC MEMORY:

{episodic_text}
"""
        )

    if procedural_memories:

        procedural_text = "\n".join(
            f"- {memory['content']}"
            for memory in procedural_memories
        )

        sections.append(
            f"""
PROCEDURAL MEMORY:

{procedural_text}
"""
        )

    context = "\n".join(sections)

    return {
        "context": context
    }