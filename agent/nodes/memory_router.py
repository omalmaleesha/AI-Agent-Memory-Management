# Its job is:
# Decide which memories are actually needed.
# Examples:
# "What technologies do I use?"
# -> semantic
# "What did we discuss yesterday?"
# -> episodic
# "How should I deploy this application?"
# -> procedural

# app/agent/nodes/memory_router.py

import json
from typing import Literal
from pydantic import BaseModel, ValidationError
from agent.state import AgentState

class MemoryRouting(BaseModel):
    required_memories: list[
        Literal[
            "semantic",
            "episodic",
            "procedural",
        ]
    ]


def memory_router_node(state: AgentState,llm,) -> dict:

    print("\n========================================")
    print("[MEMORY ROUTER] START")
    print("========================================")

    user_input = state["user_input"]

    print(f"[MEMORY ROUTER] User input: {user_input}")

    prompt = f"""
    You are a memory routing system.

    Your job is to determine which memory types are
    actually useful for answering the user's request.

    Available memory types:

    semantic:
    Durable facts, preferences, profile information,
    skills, technologies, and knowledge about the user.

    episodic:
    Past conversations, previous events,
    previous tasks, meetings, and historical interactions.

    procedural:
    Instructions, workflows, rules,
    procedures, and how-to knowledge.

    Rules:

    1. Select ONLY memory types that are useful.
    2. Do not select a memory type just because it exists.
    3. You may select multiple memory types.
    4. Return an empty list if no memory is required.
    5. You MUST return valid JSON.
    6. Do not return markdown.
    7. Do not add explanations.

    Return exactly this format:

    {{
        "required_memories": [
            "semantic"
        ]
    }}

    User request:

    {user_input}
    """

    print("[MEMORY ROUTER] Sending request to LLM...")

    try:

        # IMPORTANT:
        # Do NOT use with_structured_output()
        # We use normal LLM invocation with JSON mode.
        response = llm.invoke(
            prompt,
            response_format={
                "type": "json_object"
            },
        )

        print("[MEMORY ROUTER] LLM response received")
        content = response.content
        print(f"[MEMORY ROUTER] Raw response: {content}")
        # Parse JSON
        data = json.loads(content)
        print(f"[MEMORY ROUTER] Parsed JSON: {data}")
        # Validate with Pydantic
        routing = MemoryRouting.model_validate(data)
        required_memories = routing.required_memories

        print(
            "[MEMORY ROUTER] Selected memories: "
            f"{required_memories}"
        )

        print("[MEMORY ROUTER] SUCCESS")
        print("========================================\n")

        return {
            "required_memories": required_memories
        }

    except json.JSONDecodeError as e:

        print(
            "[MEMORY ROUTER] JSON parsing failed:"
            f" {e}"
        )

        return {
            "required_memories": []
        }

    except ValidationError as e:

        print(
            "[MEMORY ROUTER] Memory routing validation failed:"
            f" {e}"
        )

        return {
            "required_memories": []
        }

    except Exception as e:

        print(
            "[MEMORY ROUTER] Unexpected error:"
            f" {type(e).__name__}: {e}"
        )

        return {
            "required_memories": []
        }