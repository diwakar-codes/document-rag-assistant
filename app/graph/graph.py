from langgraph.graph import StateGraph, END
from app.graph.node import (
    memory_node,
    retrieve_node,
    generate_node,
    no_context_node,
    route_after_retrieval,
)
from app.graph.state import GraphState

builder = StateGraph(GraphState)

builder.add_node(
    "retrieve",
    retrieve_node,
)

builder.add_node(
    "generate",
    generate_node,
)

builder.add_node(
    "no_context",
    no_context_node,
)

builder.add_conditional_edges(
    "retrieve",
    route_after_retrieval,
    {
        "generate": "generate",
        "no_context": "no_context",
    },
)

builder.add_edge(
    "generate",
    END,
)

builder.add_edge(
    "no_context",
    END,
)

builder.add_node("memory", memory_node)

builder.set_entry_point("memory")

builder.add_edge("memory", "retrieve")

graph = builder.compile()