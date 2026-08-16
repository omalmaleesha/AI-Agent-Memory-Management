from langgraph.graph import StateGraph, START, END

from agent.state import AgentState

from agent.nodes.conversation import conversation_node
from agent.nodes.memory_router import memory_router_node
from agent.nodes.memory_retriever import memory_retriever_node
from agent.nodes.context_builder import context_builder_node
from agent.nodes.agent import agent_node
from agent.nodes.memory_extractor import memory_extractor_node
from agent.nodes.memory_writer import memory_writer_node

from llm.llm import llm_service
from memory.manager import memory_manager


def create_agent_graph(memory_manager):

    graph = StateGraph(AgentState)

    graph.add_node(
        "conversation",
        conversation_node
    )

    graph.add_node(
        "memory_router",
        lambda state: memory_router_node(
            state,
            llm_service
        )
    )

    graph.add_node(
        "memory_retriever",
        lambda state: memory_retriever_node(
            state,
            memory_manager
        )
    )

    graph.add_node(
        "context_builder",
        context_builder_node
    )

    graph.add_node(
        "agent",
        lambda state: agent_node(
            state,
            llm_service
        )
    )

    graph.add_node(
        "memory_extractor",
        lambda state: memory_extractor_node(
            state,
            llm_service
        )
    )

    graph.add_node(
        "memory_writer",
        lambda state: memory_writer_node(
            state,
            memory_manager
        )
    )

    graph.add_edge(START, "conversation")
    graph.add_edge("conversation", "memory_router")
    graph.add_edge("memory_router", "memory_retriever")
    graph.add_edge("memory_retriever", "context_builder")
    graph.add_edge("context_builder", "agent")
    graph.add_edge("agent", "memory_extractor")
    graph.add_edge("memory_extractor", "memory_writer")
    graph.add_edge("memory_writer", END)

    return graph.compile()


agent_graph = create_agent_graph(
    memory_manager
)