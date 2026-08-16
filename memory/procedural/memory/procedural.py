from pathlib import Path

from database.neo4j import Neo4jClient


class ProceduralMemoryManager:

    def __init__(
        self,
        db: Neo4jClient,
        memory_directory: str | Path | None = None
    ):

        self.db = db

        if memory_directory is None:
            self.memory_directory = Path(__file__).resolve().parents[2]
        else:
            self.memory_directory = Path(memory_directory)

    def get_procedure(
        self,
        name: str
    ):

        file_path = (
            self.memory_directory / f"{name}.md"
        )

        if not file_path.exists():
            return None

        return {
            "id": name,
            "name": name,
            "source": str(file_path),
            "content": file_path.read_text(
                encoding="utf-8"
            )
        }

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
                    )
                }
            )

        return procedures
    

    def search(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ):

        cypher = """
        MATCH (u:User {id: $user_id})
              -[:HAS_PROCEDURAL_MEMORY]->
              (m:ProceduralMemory)

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