import json

from ingestion.pdf_loader import load_pdf
from database.neo4j import Neo4jClient
from memory.semantic.memory.semantic import (
    SemanticMemoryManager,
)
from llm.llm import llm_service


def load_semantic_memory(
    pdf_path: str,
    user_id: str,
):

    print("\n====================================")
    print("[MEMORY LOADER] START")
    print("====================================")

    # =========================================================
    # 1. LOAD PDF
    # =========================================================

    print("\n[1/5] Loading PDF...")

    text = load_pdf(pdf_path)

    if not text.strip():

        print(
            "[MEMORY LOADER] PDF contains no "
            "extractable text."
        )

        return

    print(
        f"[MEMORY LOADER] PDF text loaded: "
        f"{len(text)} characters"
    )

    # =========================================================
    # 2. CONNECT TO NEO4J
    # =========================================================

    print("\n[2/5] Connecting to Neo4j...")

    neo4j_client = Neo4jClient()

    semantic_manager = SemanticMemoryManager(
        neo4j_client
    )

    # =========================================================
    # 3. ENSURE USER EXISTS
    # =========================================================

    print(
        f"[3/5] Ensuring user exists: {user_id}"
    )

    semantic_manager.ensure_user(
        user_id
    )

    # =========================================================
    # 4. EXTRACT SEMANTIC MEMORIES
    # =========================================================

    print(
        "\n[4/5] Asking LLM to extract "
        "semantic memories..."
    )

    prompt = f"""
You are a semantic memory extraction system.

Your job is to extract ONLY durable information
that should be remembered about the user.

Semantic memories include:

- facts
- user profile information
- preferences
- skills
- technologies
- goals
- stable knowledge
- long-term interests
- professional experience

Do NOT extract:

- temporary events
- one-time conversations
- procedures
- workflows
- instructions
- temporary tasks
- dates that are only relevant to a specific event
- document metadata
- assumptions that are not explicitly supported

Rules:

1. Only extract information explicitly supported
   by the document.

2. Do not invent information.

3. Do not create duplicate memories.

4. Keep memories concise and meaningful.

5. Each memory should represent one durable fact.

6. importance must be between 0 and 1.

7. confidence must be between 0 and 1.

8. category must be one of:

   fact
   profile
   preference
   skill
   technology
   goal

Return ONLY valid JSON.

Do not use markdown.

Required format:

{{
    "memories": [
        {{
            "content": "User has experience with React",
            "category": "technology",
            "importance": 0.9,
            "confidence": 0.95
        }}
    ]
}}

DOCUMENT:

{text}
"""

    response = llm_service.invoke(
        prompt
    )

    print(
        "[MEMORY LOADER] LLM extraction complete."
    )

    # =========================================================
    # 5. PARSE RESPONSE
    # =========================================================

    print(
        "\n[5/5] Parsing extracted memories..."
    )

    raw_response = response.content

    # ---------------------------------------------------------
    # Remove markdown code fences if model returns them
    # ---------------------------------------------------------

    raw_response = raw_response.strip()

    if raw_response.startswith(
        "```json"
    ):

        raw_response = raw_response[
            7:
        ]

    elif raw_response.startswith(
        "```"
    ):

        raw_response = raw_response[
            3:
        ]

    if raw_response.endswith(
        "```"
    ):

        raw_response = raw_response[
            :-3
        ]

    raw_response = raw_response.strip()

    # ---------------------------------------------------------
    # Parse JSON
    # ---------------------------------------------------------

    try:

        data = json.loads(
            raw_response
        )

    except json.JSONDecodeError as e:

        print(
            "\n[MEMORY LOADER] ERROR:"
        )

        print(
            "LLM returned invalid JSON."
        )

        print(
            "\nRAW RESPONSE:"
        )

        print(
            raw_response
        )

        raise ValueError(
            "LLM did not return valid JSON"
        ) from e

    # =========================================================
    # EXTRACT MEMORY ARRAY
    # =========================================================

    memories = data.get(
        "memories",
        []
    )

    if not isinstance(
        memories,
        list,
    ):

        raise ValueError(
            "'memories' must be a list"
        )

    print(
        f"\n[MEMORY LOADER] "
        f"Memories extracted: {len(memories)}"
    )

    # =========================================================
    # STORE MEMORIES
    # =========================================================

    saved_count = 0
    skipped_count = 0

    print(
        "\n[MEMORY LOADER] "
        "Saving memories to Neo4j..."
    )

    for index, memory in enumerate(
        memories,
        start=1,
    ):

        # -----------------------------------------------------
        # Validate memory object
        # -----------------------------------------------------

        if not isinstance(
            memory,
            dict,
        ):

            print(
                f"[MEMORY LOADER] "
                f"Skipping invalid memory #{index}"
            )

            skipped_count += 1

            continue

        content = memory.get(
            "content"
        )

        if not content:

            print(
                f"[MEMORY LOADER] "
                f"Skipping memory #{index}: "
                f"missing content"
            )

            skipped_count += 1

            continue

        content = str(
            content
        ).strip()

        if not content:

            skipped_count += 1

            continue

        # -----------------------------------------------------
        # Category
        # -----------------------------------------------------

        category = memory.get(
            "category",
            "fact",
        )

        allowed_categories = {
            "fact",
            "profile",
            "preference",
            "skill",
            "technology",
            "goal",
        }

        if category not in allowed_categories:

            category = "fact"

        # -----------------------------------------------------
        # Importance
        # -----------------------------------------------------

        try:

            importance = float(
                memory.get(
                    "importance",
                    0.5,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            importance = 0.5

        importance = max(
            0.0,
            min(
                1.0,
                importance,
            ),
        )

        # -----------------------------------------------------
        # Confidence
        # -----------------------------------------------------

        try:

            confidence = float(
                memory.get(
                    "confidence",
                    0.5,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            confidence = 0.5

        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

        # -----------------------------------------------------
        # Print
        # -----------------------------------------------------

        print(
            "\n------------------------------------"
        )

        print(
            f"[MEMORY {index}]"
        )

        print(
            f"Content: {content}"
        )

        print(
            f"Category: {category}"
        )

        print(
            f"Importance: {importance}"
        )

        print(
            f"Confidence: {confidence}"
        )

        # -----------------------------------------------------
        # Save
        # -----------------------------------------------------

        result = semantic_manager.create(
            user_id=user_id,
            content=content,
            category=category,
            importance=importance,
            confidence=confidence,
            embedding=None,
        )

        if result is not None:

            saved_count += 1

        else:

            skipped_count += 1

    # =========================================================
    # FINISHED
    # =========================================================

    print(
        "\n===================================="
    )

    print(
        "[MEMORY LOADER] COMPLETE"
    )

    print(
        f"Extracted : {len(memories)}"
    )

    print(
        f"Saved     : {saved_count}"
    )

    print(
        f"Skipped   : {skipped_count}"
    )

    print(
        "====================================\n"
    )

    return {
        "user_id": user_id,
        "extracted": len(memories),
        "saved": saved_count,
        "skipped": skipped_count,
    }