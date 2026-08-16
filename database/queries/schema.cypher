CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT semantic_memory_id_unique IF NOT EXISTS
FOR (m:SemanticMemory)
REQUIRE m.id IS UNIQUE;

CREATE CONSTRAINT episode_id_unique IF NOT EXISTS
FOR (e:Episode)
REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT conversation_id_unique IF NOT EXISTS
FOR (c:Conversation)
REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT procedure_id_unique IF NOT EXISTS
FOR (p:Procedure)
REQUIRE p.id IS UNIQUE;