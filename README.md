# 🧠 AI Agent Memory Management

> **A production-oriented AI Agent architecture that gives LLMs long-term memory.**

Most LLM applications are **stateless** — they forget previous conversations and repeatedly receive the same context. This project explores how to solve that problem by building a **memory management layer** that decides what the AI should remember, what it should retrieve, and what context should be given to the LLM.

Built with **Python, LangGraph, FastAPI, Groq, and Neo4j**, the system separates memory into **Semantic, Episodic, and Procedural memory** and uses an agent workflow to retrieve relevant information before generating a response.

### 🚀 What I Built

```text
User Request
     ↓
Memory Router
     ↓
Memory Retrieval
     ↓
Context Builder
     ↓
AI Agent
     ↓
Memory Extraction
     ↓
Neo4j Persistent Memory
```

### 💡 Key Capabilities

* 🧠 **Long-term AI memory** across conversations
* 🧭 **Memory routing** — decides which memory type is relevant
* 🔎 **Context-aware retrieval** — retrieves only useful information
* 🕸️ **Neo4j knowledge graph** for persistent memory
* 🔄 **LangGraph agent workflow** with multiple processing nodes
* 📄 **PDF/document ingestion**
* ⚡ **FastAPI backend** for exposing the agent as an API
* 🧩 Modular architecture designed for future memory strategies

### 🛠️ Tech Stack

**Python · LangGraph · LangChain · Groq · FastAPI · Neo4j · PyMuPDF**

### 🎯 Why I Built This

I created this project as a **hobby project in my free time** to explore how AI agents can maintain useful long-term memory instead of starting from zero in every conversation.

While building it, I wanted to strengthen my practical skills in **AI agents, LangGraph, LLM workflows, memory management, Neo4j, retrieval systems, and backend architecture** by solving a problem that I find interesting.

This project is continuously evolving as I experiment with better ways to **store, retrieve, organize, and use memory in AI agents**.


### 🔮 Future Work

Memory scoring • Deduplication • Memory lifecycle • Hybrid Graph + Vector Retrieval • Token/Latency Monitoring • Memory Evaluation

---

⭐ **Interested in AI Agents, LLM systems, or backend engineering? Explore the code and architecture.**

**GitHub:** https://github.com/omalmaleesha/AI-Agent-Memory-Management
