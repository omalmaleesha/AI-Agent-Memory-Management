from multiprocessing.reduction import duplicate
import uuid
from datetime import datetime, timezone
from database.neo4j import Neo4jClient


class SemanticMemoryManager:

    def __init__(
        self,
        db: Neo4jClient,
    ):
        self.db = db
    # ENSURE USER
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

    # CREATE
    def create(
        self,
        user_id: str,
        content: str,
        category: str | None = None,
        importance: float = 0.5,
        confidence: float = 1.0,
        embedding: list[float] | None = None,
        check_duplicate: bool = True,
    ):
        """
        Create a semantic memory and connect it to the user.
        """
        # Validate content
        if check_duplicate:
            duplicate = self.check_duplicate(
                user_id=user_id,
                content=content,
            )

        if duplicate:

            print(
                "[SEMANTIC MEMORY] Duplicate found. "
                "Skipping storage."
            )

            return {
                "status": "duplicate",
                "existing_memory": duplicate,
            }

        if not content or not content.strip():
            print(
                "[SEMANTIC MEMORY] "
                "Skipping empty memory"
            )
            return None

        content = content.strip()

        # Validate scores
        importance = max(
            0.0,
            min(1.0, float(importance)),
        )

        confidence = max(
            0.0,
            min(1.0, float(confidence)),
        )
        # Generate ID / timestamp
        memory_id = str(uuid.uuid4())

        now = datetime.now(
            timezone.utc
        ).isoformat()
        # Create memory
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
        
    def check_duplicate(
        self,
        user_id: str,
        content: str,
        threshold: float = 0.90,
    ) -> dict | None:
        """
        Check whether a semantically similar memory
        already exists for this user.
        """

        print("\n" + "=" * 70)
        print("[SEMANTIC DUPLICATE CHECK START]")
        print("=" * 70)

        # Search for the closest existing semantic memory
        results = self.search(
            user_id=user_id,
            query=content,
            limit=1,
        )

        if not results:
            print("[SEMANTIC DUPLICATE CHECK] No existing memory found")
            return None

        best_match = results[0]

        # Adjust this depending on your search result structure
        similarity = float(
            best_match.get("relevance_score", 0.0)
        )

        print(
            f"[SEMANTIC DUPLICATE CHECK] "
            f"similarity={similarity:.4f}"
        )

        if similarity >= threshold:

            print(
                "[SEMANTIC DUPLICATE DETECTED] "
                f"threshold={threshold}"
            )

            return best_match

        print("[SEMANTIC DUPLICATE CHECK] No duplicate detected")

        return None
    
    # GET USER MEMORIES
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

    # SEARCH - Query Search
    # In Future Implemet the sematic search using Neo4j vector similarity search.
    def search(
        self,
        user_id: str,
        query: str,
        limit: int = 2,
    ):
        """
        Retrieve the most relevant semantic memories.

        Current implementation:
            - Exact phrase matching
            - Keyword coverage
            - Keyword frequency
            - Importance
            - Confidence
            - Light recency boost

        Future implementation:
            Neo4j vector similarity search.
        """

        cypher = """
        MATCH (u:User {id: $user_id})
            -[:HAS_SEMANTIC_MEMORY]->
            (m:SemanticMemory)

        WITH
            m,
            toLower(trim(m.content)) AS content,
            toLower(trim($query)) AS search_query

        // Extract useful query words
        WITH
            m,
            content,
            search_query,
            [
                word IN split(search_query, " ")
                WHERE size(trim(word)) > 2
                AND trim(word) NOT IN [
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
                    "show"
                ]
            ] AS query_words

        // Count how many query words appear in the memory
        WITH
            m,
            content,
            search_query,
            query_words,
            size([
                word IN query_words
                WHERE content CONTAINS word
            ]) AS matched_words

        // Calculate keyword coverage
        WITH
            m,
            content,
            search_query,
            query_words,
            matched_words,

            CASE
                WHEN size(query_words) = 0 THEN 0.0
                ELSE toFloat(matched_words) / size(query_words)
            END AS keyword_coverage

        // Exact full query / phrase matching
        WITH
            m,
            content,
            search_query,
            query_words,
            matched_words,
            keyword_coverage,

            CASE
                WHEN content CONTAINS search_query
                THEN 1.0
                ELSE 0.0
            END AS exact_phrase_score

        // Reward multiple keyword occurrences slightly
        WITH
            m,
            content,
            search_query,
            query_words,
            matched_words,
            keyword_coverage,
            exact_phrase_score,

            reduce(
                frequency_score = 0.0,
                word IN query_words |

                frequency_score +
                CASE
                    WHEN size(split(content, word)) > 1
                    THEN 1.0
                    ELSE 0.0
                END
            ) AS raw_frequency_score

        WITH
            m,
            keyword_coverage,
            exact_phrase_score,

            CASE
                WHEN size(query_words) = 0 THEN 0.0
                ELSE raw_frequency_score / size(query_words)
            END AS frequency_score

        // Main relevance score
        WITH
            m,

            (
                keyword_coverage * 0.65
                +
                exact_phrase_score * 0.25
                +
                frequency_score * 0.10
            ) AS relevance_score

        // Only rank memories that actually match the query
        WHERE relevance_score > 0

        WITH
            m,
            relevance_score,

            (
                relevance_score * 0.75
                +
                coalesce(m.importance, 0.5) * 0.15
                +
                coalesce(m.confidence, 0.5) * 0.10
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

        ORDER BY
            final_score DESC,
            relevance_score DESC,
            m.importance DESC

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

        if results:
            for memory in results:
                memory_id = memory.get("id")

                if memory_id:
                    self.increment_access_count(memory_id)

        return results
        
    # INCREMENT ACCESS COUNT
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