from fastapi import APIRouter
from app.services.retrieval_service import RetrievalService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/")
def ask(question: str):
    result = RetrievalService.retrieve(question)
    return result

