from pathlib import Path
from database.neo4j import Neo4jClient

class ProceduralMemoryManager:

    def __init__(
        self,
        db: Neo4jClient,
        memory_directory: str | Path | None = None,
    ):
        self.db = db

        # Default procedural memory directory
        if memory_directory is None:
            self.memory_directory = (
                Path(__file__).resolve().parents[2]
                / "procedural_memory"
            )
        else:
            self.memory_directory = Path(memory_directory)

        # Create directory if it doesn't exist
        self.memory_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # GET SINGLE PROCEDURE

    def get_procedure(
        self,
        name: str,
    ):

        file_path = (
            self.memory_directory
            / f"{name}.md"
        )

        if not file_path.exists():
            return None

        return {
            "id": file_path.stem,
            "name": file_path.stem,
            "source": str(file_path),
            "content": file_path.read_text(
                encoding="utf-8"
            ),
        }

    # LIST ALL PROCEDURES

    def list_procedures(self):

        procedures = []

        for file in self.memory_directory.glob(
            "*.md"
        ):

            procedures.append(
                {
                    "id": file.stem,
                    "name": file.stem,
                    "source": str(file),
                    "content": file.read_text(
                        encoding="utf-8"
                    ),
                }
            )

        return procedures

    # SEARCH PROCEDURAL MEMORY

    def search(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ):
        """
        Search procedural memory Markdown files.

        Ranking:
            - Keyword coverage
            - Exact phrase match
            - Procedure name match

        Note:
            user_id is currently kept for interface consistency
            with other memory managers.
        """

        # Normalize query
        normalized_query = query.lower().strip()

        # Common words that provide little search value
        stop_words = {
            "what",
            "when",
            "where",
            "which",
            "with",
            "from",
            "that",
            "this",
            "does",
            "have",
            "about",
            "your",
            "user",
            "tell",
            "give",
            "show",
            "how",
            "can",
            "the",
            "and",
            "for",
            "are",
            "was",
            "were",
            "you",
            "use",
            "using",
            "into",
            "need",
            "want",
        }

        # Extract meaningful query words
        query_words = [
            word.strip()
            for word in normalized_query.split()
            if len(word.strip()) > 2
            and word.strip() not in stop_words
        ]

        results = []

        # Search every Markdown procedure
        for file in self.memory_directory.glob("*.md"):

            try:

                content = file.read_text(
                    encoding="utf-8"
                )

            except Exception:
                continue

            # Normalize searchable text
            normalized_content = content.lower()

            # Include procedure name in search
            normalized_name = file.stem.lower()

            searchable_content = (
                f"{normalized_name} "
                f"{normalized_content}"
            )

            # 1. KEYWORD COVERAGE
            matched_words = sum(
                1
                for word in query_words
                if word in searchable_content
            )

            if query_words:

                keyword_score = (
                    matched_words
                    / len(query_words)
                )

            else:

                keyword_score = 0.0

            # 2. EXACT PHRASE MATCH

            phrase_score = (
                1.0
                if normalized_query
                and normalized_query
                in searchable_content
                else 0.0
            )

            # 3. PROCEDURE NAME MATCH

            name_matches = sum(
                1
                for word in query_words
                if word in normalized_name
            )

            if query_words:

                name_score = (
                    name_matches
                    / len(query_words)
                )

            else:

                name_score = 0.0

            # FINAL SCORE

            final_score = (
                keyword_score * 0.50
                +
                phrase_score * 0.20
                +
                name_score * 0.30
            )

            # Ignore completely irrelevant procedures
            if final_score <= 0:
                continue

            results.append(
                {
                    "id": file.stem,
                    "name": file.stem,
                    "source": str(file),
                    "content": content,
                    "keyword_score": round(
                        keyword_score,
                        4,
                    ),
                    "phrase_score": phrase_score,
                    "name_score": round(
                        name_score,
                        4,
                    ),
                    "final_score": round(
                        final_score,
                        4,
                    ),
                }
            )

        # SORT BY BEST MATCH

        results.sort(
            key=lambda item: (
                item["final_score"],
                item["name_score"],
                item["keyword_score"],
            ),
            reverse=True,
        )

        # Return only top K procedures
        return results[:limit]