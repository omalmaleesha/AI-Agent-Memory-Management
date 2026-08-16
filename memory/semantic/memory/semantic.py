import uuid
from datetime import datetime, timezone

from database.neo4j import Neo4jClient


class SemanticMemoryManager:

    def __init__(
        self,
        db: Neo4jClient
    ):
        self.db = db

    def create(
        self,
        user_id: str,
        content: str,
        importance: float = 0.5,
        confidence: float = 1.0,
        embedding: list[float] | None = None
    ):

        memory_id = str(uuid.uuid4())

        now = datetime.now(
            timezone.utc
        ).isoformat()

        query = """
        MATCH (u:User {id: $user_id})

        CREATE (m:SemanticMemory {
            id: $id,
            content: $content,
            importance: $importance,
            confidence: $confidence,
            created_at: $created_at,
            updated_at: $updated_at,
            access_count: 0,
            embedding: $embedding
        })

        CREATE (u)-[:HAS_SEMANTIC_MEMORY]->(m)

        RETURN m
        """

        result = self.db.execute(
            query,
            {
                "user_id": user_id,
                "id": memory_id,
                "content": content,
                "importance": importance,
                "confidence": confidence,
                "created_at": now,
                "updated_at": now,
                "embedding": embedding
            }
        )

        return result


    def get_by_user(
        self,
        user_id: str,
        limit: int = 10
    ):

        query = """
        MATCH (u:User {id: $user_id})
              -[:HAS_SEMANTIC_MEMORY]->
              (m:SemanticMemory)

        RETURN m
        ORDER BY m.importance DESC

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

        # Temporary implementation.
        # We will replace this with vector similarity
        # against Neo4j.

        cypher = """
        MATCH (u:User {id: $user_id})
              -[:HAS_SEMANTIC_MEMORY]->
              (m:SemanticMemory)

        RETURN
            m.id AS id,
            m.content AS content,
            m.importance AS importance,
            m.confidence AS confidence

        ORDER BY m.importance DESC

        LIMIT $limit
        """

        return self.db.execute(
            cypher,
            {
                "user_id": user_id,
                "limit": limit,
            },
        )   