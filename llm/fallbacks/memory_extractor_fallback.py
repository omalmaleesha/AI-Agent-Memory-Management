class MemoryExtractorFallback:
    """
    Local fallback for memory extraction.

    Used when the LLM is unavailable.
    Performs basic keyword-based detection
    to determine whether information should
    be stored as memory.
    """

    def extract(
        self,
        user_input: str,
        assistant_response: str,
    ) -> dict:

        combined = (
            f"{user_input}\n"
            f"{assistant_response}"
        ).lower()

        # -------------------------------------------------
        # DETERMINE IF MEMORY SHOULD BE SAVED
        # -------------------------------------------------

        should_save = any(
            keyword in combined
            for keyword in [
                "my name is",
                "i am",
                "i like",
                "i prefer",
                "remember",
                "my goal",
                "i work with",
                "i use",
                "always",
                "never",
            ]
        )

        memories = []

        if should_save:

            # Default memory type
            memory_type = "semantic"

            # ---------------------------------------------
            # PROCEDURAL MEMORY
            # ---------------------------------------------

            if any(
                keyword in combined
                for keyword in [
                    "workflow",
                    "how to",
                    "procedure",
                    "step",
                    "deploy",
                    "configure",
                    "setup",
                ]
            ):
                memory_type = "procedural"

            # ---------------------------------------------
            # EPISODIC MEMORY
            # ---------------------------------------------

            elif any(
                keyword in combined
                for keyword in [
                    "yesterday",
                    "today",
                    "last time",
                    "meeting",
                    "event",
                    "task",
                ]
            ):
                memory_type = "episodic"

            # ---------------------------------------------
            # CREATE MEMORY
            # ---------------------------------------------

            memories.append(
                {
                    "type": memory_type,
                    "content": (
                        user_input.strip()
                        or assistant_response.strip()
                    ),
                    "importance": 0.6,
                    "confidence": 0.5,
                }
            )

        return {
            "should_save": should_save,
            "memories": memories,
        }