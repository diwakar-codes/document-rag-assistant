from typing import Optional, TypedDict


class GraphState(TypedDict):
    question: str
    sources: list
    answer: str
    has_context: bool
    history: list
    mode: str
    top_k: int
    document_id: Optional[str]
    topic: Optional[str]
    similarity_threshold: Optional[float]
    temperature: Optional[float]
    max_tokens: Optional[int]
