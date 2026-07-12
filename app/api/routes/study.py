from fastapi import APIRouter, HTTPException

from app.schemas.study_schema import FlashcardRequest, StudyPlanRequest
from app.services.flashcard_service import FlashcardService
from app.services.planner_service import PlannerService

router = APIRouter(tags=["Study Tools"])


@router.post("/flashcards/generate")
def generate_flashcards(request: FlashcardRequest):
    try:
        return FlashcardService.generate(request.topic, request.num_cards)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/study/plan")
def generate_study_plan(request: StudyPlanRequest):
    try:
        return PlannerService.generate_plan(request.topics, request.hours_per_day)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
