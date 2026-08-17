from neo4j import GraphDatabase
from config.settings import settings


print("URI:", settings.NEO4J_URI)
print("USERNAME:", settings.NEO4J_USERNAME)
print("PASSWORD LOADED:", bool(settings.NEO4J_PASSWORD))


driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(
        settings.NEO4J_USERNAME,
        settings.NEO4J_PASSWORD,
    ),
)


try:
    driver.verify_connectivity()
    print("✅ Neo4j connection successful!")

except Exception as e:
    print("❌ Neo4j connection failed:")
    print(e)

finally:
    driver.close()