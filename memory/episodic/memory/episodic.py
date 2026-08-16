import uuid
from datetime import datetime, timezone

from database.neo4j import Neo4jClient


class EpisodicMemoryManager:

    def __init__(
        self,
        db: Neo4jClient
    ):
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

    def get_recent(
        self,
        user_id: str,
        limit: int = 10
    ):

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

        cypher = """
        MATCH (u:User {id: $user_id})
              -[:HAS_EPISODIC_MEMORY]->
              (m:EpisodicMemory)

        RETURN
            m.id AS id,
            m.content AS content,
            m.importance AS importance,
            m.created_at AS created_at

        ORDER BY m.created_at DESC

        LIMIT $limit
        """

        return self.db.execute(
            cypher,
            {
                "user_id": user_id,
                "limit": limit,
            },
        )