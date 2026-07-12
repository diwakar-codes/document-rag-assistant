from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/info")
def system_info():
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "embedding_model": settings.EMBEDDING_MODEL,
        "llm_model": settings.GROQ_MODEL,
        "vision_model": settings.GROQ_VISION_MODEL,
        "vector_db": "Pinecone",
        "pinecone_index": settings.PINECONE_INDEX,
    }
