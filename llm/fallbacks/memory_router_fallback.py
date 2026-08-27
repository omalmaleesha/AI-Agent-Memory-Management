class MemoryRouterFallback:
    """
    Local fallback for memory routing.

    Used when the LLM is unavailable.
    Determines which memory types may be
    required based on keyword matching.
    """

    def route(
        self,
        user_request: str,
    ) -> list[str]:

        text = user_request.lower()

        required: list[str] = []

        # -------------------------------------------------
        # SEMANTIC MEMORY
        # -------------------------------------------------

        if any(
            keyword in text
            for keyword in [
                "remember",
                "about me",
                "profile",
                "preference",
                "prefer",
                "skill",
                "technology",
                "stack",
                "name",
                "email",
            ]
        ):
            required.append("semantic")

        # -------------------------------------------------
        # EPISODIC MEMORY
        # -------------------------------------------------

        if any(
            keyword in text
            for keyword in [
                "yesterday",
                "last time",
                "previous",
                "earlier",
                "discuss",
                "conversation",
                "task",
                "meeting",
                "event",
                "what did we",
                "when did we",
            ]
        ):
            required.append("episodic")

        # -------------------------------------------------
        # PROCEDURAL MEMORY
        # -------------------------------------------------

        if any(
            keyword in text
            for keyword in [
                "how do i",
                "how should i",
                "how to",
                "deploy",
                "workflow",
                "rule",
                "instruction",
                "procedure",
                "setup",
                "configure",
                "implement",
                "fix",
            ]
        ):
            required.append("procedural")

        # Remove duplicates while preserving order
        return list(dict.fromkeys(required))