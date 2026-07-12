from fastapi import APIRouter
from app.graph.graph import graph

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/")
def chat(question: str):
    result = graph.invoke(
        {
            "question": question,
            "sources": [],
            "answer": "",
        }
    )
    return result
