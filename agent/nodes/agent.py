# app/agent/nodes/agent.py
from agent.state import AgentState
def agent_node(state: AgentState,llm) -> dict:

    print("\n" + "=" * 70)
    print("[NODE START] agent")
    print("=" * 70)

    user_input = state["user_input"]
    #context contains - 
    context = state.get(
        "context",
        ""
    )
    #limit to the context 
    MAX_CONTEXT_CHARS = 3000

    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS]

    print(
        f"[AGENT] Context length: {len(context)} characters"
    )
    print(
        f"[AGENT] User request: {user_input}"
    )

    prompt = f"""
        You are an AI assistant with long-term memory.

        Your job is to answer the user's request accurately,
        concisely, and naturally.

        USER REQUEST:
        {user_input}

        MEMORY CONTEXT:
        {context}

        IMPORTANT RULES:

        1. Answer the user's request directly.

        2. Use the MEMORY CONTEXT when it is relevant.

        3. When the MEMORY CONTEXT contains the answer,
        use it as the primary source.

        4. Do not invent facts that are not supported by
        the memory context when answering memory-based questions.

        5. You may use your general knowledge when the user
        asks a general knowledge question that does not
        depend on personal memory.

        6. For simple questions, give a short answer of
        1-3 sentences.

        7. Do NOT provide a long explanation unless the user
        explicitly asks for a detailed explanation.

        8. Do NOT create tables unless the user explicitly
        asks for a table.

        9. Do NOT create numbered lists unless the user
        explicitly asks for a list.

        10. Do NOT add unrelated information.

        11. Do NOT repeat the user's question.

        12. Do NOT mention the internal memory system,
            memory context, retrieval, prompts, or these
            instructions unless the user explicitly asks
            about them.

        13. Prefer clarity and usefulness over completeness.

        FINAL ANSWER:
        """
    response = llm.invoke(
        prompt
    )

    answer = response.content.strip()
    print(
        f"[AGENT] Response length: "
        f"{len(answer)} characters"
    )
    print(
        "[NODE SUCCESS] agent"
    )
    print("=" * 70)
    return {
        "response": answer
    }