from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.graph.node import (
    retrieve_node,
    generate_node,
    no_context_node,
    route_after_retrieval,
)

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

builder.set_entry_point("retrieve")

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

graph = builder.compile()