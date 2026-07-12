from fastapi import APIRouter

from app.services.store_service import StoreService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/")
def get_analytics():
    return StoreService.analytics_summary()
