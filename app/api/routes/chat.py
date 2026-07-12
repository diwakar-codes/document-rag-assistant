from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.graph.graph import graph
from app.memory.conversation import memory

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    question: str
    mode: str = "dense"  # dense | bm25 | hybrid
    top_k: int = settings.DEFAULT_TOP_K
    document_id: Optional[str] = None


@router.post("/")
def chat(request: ChatRequest):
    result = graph.invoke(
        {
            "question": request.question,
            "sources": [],
            "answer": "",
            "has_context": False,
            "mode": request.mode,
            "top_k": request.top_k,
            "document_id": request.document_id,
        }
    )
    return result


@router.post("/clear")
def clear_conversation():
    memory.clear()
    return {"message": "Conversation history cleared."}
