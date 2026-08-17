import uuid
from datetime import datetime, timezone

from database.neo4j import Neo4jClient


class SemanticMemoryManager:

    def __init__(
        self,
        db: Neo4jClient,
    ):
        self.db = db

    # =========================================================
    # ENSURE USER
    # =========================================================

    def ensure_user(
        self,
        user_id: str,
    ):
        """
        Make sure the user exists in Neo4j.
        """

        query = """
        MERGE (u:User {id: $user_id})

        RETURN u
        """

        return self.db.execute(
            query,
            {
                "user_id": user_id,
            },
        )

    # =========================================================
    # CREATE
    # =========================================================

    def create(
        self,
        user_id: str,
        content: str,
        category: str | None = None,
        importance: float = 0.5,
        confidence: float = 1.0,
        embedding: list[float] | None = None,
    ):
        """
        Create a semantic memory and connect it to the user.
        """

        # -----------------------------------------------------
        # Validate content
        # -----------------------------------------------------

        if not content or not content.strip():
            print(
                "[SEMANTIC MEMORY] "
                "Skipping empty memory"
            )
            return None

        content = content.strip()

        # -----------------------------------------------------
        # Validate scores
        # -----------------------------------------------------

        importance = max(
            0.0,
            min(1.0, float(importance)),
        )

        confidence = max(
            0.0,
            min(1.0, float(confidence)),
        )

        # -----------------------------------------------------
        # Generate ID / timestamp
        # -----------------------------------------------------

        memory_id = str(uuid.uuid4())

        now = datetime.now(
            timezone.utc
        ).isoformat()

        # -----------------------------------------------------
        # Create memory
        # -----------------------------------------------------

        query = """
        MATCH (u:User {id: $user_id})

        CREATE (m:SemanticMemory {
            id: $id,
            content: $content,
            category: $category,
            importance: $importance,
            confidence: $confidence,
            created_at: $created_at,
            updated_at: $updated_at,
            access_count: 0,
            embedding: $embedding
        })

        CREATE (u)-[:HAS_SEMANTIC_MEMORY]->(m)

        RETURN
            m.id AS id,
            m.content AS content,
            m.category AS category,
            m.importance AS importance,
            m.confidence AS confidence,
            m.created_at AS created_at,
            m.updated_at AS updated_at,
            m.access_count AS access_count
        """

        return self.db.execute(
            query,
            {
                "user_id": user_id,
                "id": memory_id,
                "content": content,
                "category": category,
                "importance": importance,
                "confidence": confidence,
                "created_at": now,
                "updated_at": now,
                "embedding": embedding,
            },
        )

    # =========================================================
    # GET USER MEMORIES
    # =========================================================

    def get_by_user(
        self,
        user_id: str,
        limit: int = 10,
    ):
        """
        Retrieve semantic memories belonging to a user.
        """

        query = """
        MATCH (u:User {id: $user_id})
              -[:HAS_SEMANTIC_MEMORY]->
              (m:SemanticMemory)

        RETURN
            m.id AS id,
            m.content AS content,
            m.category AS category,
            m.importance AS importance,
            m.confidence AS confidence,
            m.created_at AS created_at,
            m.updated_at AS updated_at,
            m.access_count AS access_count

        ORDER BY
            m.importance DESC,
            m.created_at DESC

        LIMIT $limit
        """

        return self.db.execute(
            query,
            {
                "user_id": user_id,
                "limit": limit,
            },
        )

    # =========================================================
    # SEARCH
    # =========================================================

    def search(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ):
        """
        Retrieve semantic memories relevant to the query.

        Current implementation:
            Keyword matching
            + importance
            + confidence

        Future implementation:
            Neo4j vector similarity search.
        """

        cypher = """
        MATCH (u:User {id: $user_id})
              -[:HAS_SEMANTIC_MEMORY]->
              (m:SemanticMemory)

        WITH
            m,
            toLower(m.content) AS content,
            toLower($query) AS search_query

        WITH
            m,
            content,
            search_query,
            [
                word IN split(search_query, " ")
                WHERE size(trim(word)) > 2
            ] AS query_words

        WITH
            m,
            query_words,

            reduce(
                score = 0.0,
                word IN query_words |

                score +
                CASE
                    WHEN content CONTAINS trim(word)
                    THEN 1.0
                    ELSE 0.0
                END
            ) AS keyword_score

        WITH
            m,
            keyword_score,

            CASE
                WHEN size(query_words) = 0
                THEN 0.0

                ELSE
                    keyword_score / size(query_words)
            END AS relevance_score

        WITH
            m,
            relevance_score,

            (
                relevance_score * 0.60
                +
                coalesce(m.importance, 0.5) * 0.25
                +
                coalesce(m.confidence, 0.5) * 0.15
            ) AS final_score

        RETURN
            m.id AS id,
            m.content AS content,
            m.category AS category,
            m.importance AS importance,
            m.confidence AS confidence,
            m.created_at AS created_at,
            m.updated_at AS updated_at,
            m.access_count AS access_count,

            relevance_score,
            final_score

        ORDER BY final_score DESC

        LIMIT $limit
        """

        results = self.db.execute(
            cypher,
            {
                "user_id": user_id,
                "query": query,
                "limit": limit,
            },
        )

        # -----------------------------------------------------
        # Track memory access
        # -----------------------------------------------------

        if results:

            for memory in results:

                memory_id = memory.get("id")

                if memory_id:

                    self.increment_access_count(
                        memory_id
                    )

        return results

    # =========================================================
    # INCREMENT ACCESS COUNT
    # =========================================================

    def increment_access_count(
        self,
        memory_id: str,
    ):
        """
        Increment the number of times a memory was retrieved.
        """

        query = """
        MATCH (m:SemanticMemory {id: $memory_id})

        SET
            m.access_count =
                coalesce(m.access_count, 0) + 1,

            m.updated_at = $updated_at

        RETURN m
        """

        return self.db.execute(
            query,
            {
                "memory_id": memory_id,
                "updated_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        )