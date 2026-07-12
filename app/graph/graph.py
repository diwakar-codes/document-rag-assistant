from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.graph.node import (
    retrieve_node,
    generate_node,
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

builder.set_entry_point("retrieve")

builder.add_edge(
    "retrieve",
    "generate"
)

builder.add_edge(
    "generate",
    END
)

graph = builder.compile()