import uuid
from datetime import datetime, timezone
from database.neo4j import Neo4jClient

class EpisodicMemoryManager:
    def __init__(self,db: Neo4jClient):
        self.db = db

    def create(
        self,
        user_id: str,
        session_id: str,
        content: str,
        importance: float = 0.5,
        embedding: list[float] | None = None
    ):

        episode_id = str(uuid.uuid4())
        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        query = """
        MATCH (u:User {id: $user_id})

        MERGE (
            c:Conversation {
                id: $session_id
            }
        )

        CREATE (e:Episode {
            id: $episode_id,
            content: $content,
            timestamp: $timestamp,
            importance: $importance,
            embedding: $embedding
        })

        CREATE (u)-[:HAS_EPISODE]->(e)

        CREATE (e)-[:PART_OF]->(c)

        RETURN e
        """
        return self.db.execute(
            query,
            {
                "user_id": user_id,
                "session_id": session_id,
                "episode_id": episode_id,
                "content": content,
                "timestamp": timestamp,
                "importance": importance,
                "embedding": embedding
            }
        )

    def get_recent(self,user_id: str,limit: int = 10):
        query = """
        MATCH (u:User {id: $user_id})
              -[:HAS_EPISODE]->
              (e:Episode)

        RETURN e

        ORDER BY e.timestamp DESC

        LIMIT $limit
        """

        return self.db.execute(
            query,
            {
                "user_id": user_id,
                "limit": limit
            }
        )

    def search(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ):
        """
        Retrieve relevant episodic memories.

        Ranking factors:
            - Keyword coverage
            - Exact phrase match
            - Importance
            - Recency
        """

        cypher = """
        MATCH (u:User {id: $user_id})
            -[:HAS_EPISODIC_MEMORY]->
            (m:EpisodicMemory)

        WITH
            m,
            toLower(trim(m.content)) AS content,
            toLower(trim($query)) AS search_query

        // Extract meaningful query words
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

        // Calculate keyword matches
        WITH
            m,
            content,
            search_query,
            query_words,

            size([
                word IN query_words
                WHERE content CONTAINS word
            ]) AS matched_words

        // Normalize keyword coverage
        WITH
            m,
            content,
            search_query,
            query_words,
            matched_words,

            CASE
                WHEN size(query_words) = 0
                THEN 0.0

                ELSE toFloat(matched_words) / size(query_words)
            END AS keyword_score

        // Exact phrase boost
        WITH
            m,
            query_words,
            keyword_score,

            CASE
                WHEN size(search_query) > 2
                AND toLower(m.content) CONTAINS search_query
                THEN 1.0

                ELSE 0.0
            END AS phrase_score

        // Recency score
        WITH
            m,
            keyword_score,
            phrase_score,

            CASE
                WHEN m.created_at IS NULL
                THEN 0.0

                WHEN duration.inDays(
                    datetime(m.created_at),
                    datetime()
                ).days <= 1
                THEN 1.0

                WHEN duration.inDays(
                    datetime(m.created_at),
                    datetime()
                ).days <= 7
                THEN 0.8

                WHEN duration.inDays(
                    datetime(m.created_at),
                    datetime()
                ).days <= 30
                THEN 0.5

                ELSE 0.2
            END AS recency_score

        // Calculate relevance first
        WITH
            m,
            keyword_score,
            phrase_score,
            recency_score,

            (
                keyword_score * 0.75
                +
                phrase_score * 0.25
            ) AS relevance_score

        // Only include actually relevant episodic memories
        WHERE relevance_score > 0

        // Final episodic ranking
        WITH
            m,
            relevance_score,
            recency_score,

            (
                relevance_score * 0.60
                +
                coalesce(m.importance, 0.5) * 0.15
                +
                recency_score * 0.25
            ) AS final_score

        RETURN
            m.id AS id,
            m.content AS content,
            m.importance AS importance,
            m.created_at AS created_at,

            relevance_score,
            recency_score,
            final_score

        ORDER BY
            final_score DESC,
            relevance_score DESC,
            m.created_at DESC

        LIMIT $limit
        """

        return self.db.execute(
            cypher,
            {
                "user_id": user_id,
                "query": query,
                "limit": limit,
            },
        )