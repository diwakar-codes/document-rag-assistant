from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.schemas.quiz_schema import QuizEvaluateRequest, QuizGenerateRequest
from app.services.quiz_service import QuizService
from app.services.store_service import StoreService

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/generate")
def generate_quiz(request: QuizGenerateRequest):
    try:
        return QuizService.generate(
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            question_type=request.question_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/evaluate")
def evaluate_quiz(request: QuizEvaluateRequest):
    questions = [question.model_dump() for question in request.questions]
    answers = [answer.model_dump() for answer in request.answers]

    result = QuizService.evaluate(request.topic, questions, answers)

    StoreService.add_quiz_attempt({
        "topic": request.topic,
        "score": result["score"],
        "total": result["total"],
        "accuracy": result["accuracy"],
        "topic_results": {
            request.topic: {
                "correct": result["score"],
                "total": result["total"],
            },
        },
        "attempted_at": datetime.now(timezone.utc).isoformat(),
    })

    return result
