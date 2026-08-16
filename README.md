# Memory Management System

A small FastAPI project that routes chat requests through an agent and a set of memory managers backed by Neo4j.

## Features

- Chat API built with FastAPI
- Agent graph for routing, retrieval, context building, and response generation
- Semantic, episodic, and procedural memory layers
- Neo4j integration for persistent memory storage

## Requirements

- Python 3.13+
- Neo4j running and reachable from the app
- API credentials configured in `.env` or your environment

## Setup

Install dependencies with your preferred tool. For example:

```bash
uv sync
```

If you are using the legacy requirements file:

```bash
pip install -r requirement.txt
```

## Run

Start the app with Uvicorn:

```bash
uvicorn main:app --reload
```

## Chat Endpoint

POST `/chat`

Example request body:

```json
{
	"user_id": "user-123",
	"session_id": "session-123",
	"message": "Hello, what do you remember about me?"
}
```

The response returns the assistant message as JSON.

## Notes

- If Neo4j is unavailable, the chat endpoint falls back to a direct LLM response.
- Memory retrieval and writing are handled through the agent graph.
