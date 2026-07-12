from typing import List, Optional

from pydantic import BaseModel


class QuizGenerateRequest(BaseModel):
    topic: str
    difficulty: str = "medium"  # easy | medium | hard
    num_questions: int = 5
    question_type: str = "mixed"  # mcq | true_false | fill_blank | mixed


class QuizQuestion(BaseModel):
    id: int
    type: str
    question: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    reference: Optional[str] = None


class QuizAnswer(BaseModel):
    question_id: int
    answer: str


class QuizEvaluateRequest(BaseModel):
    topic: str
    questions: List[QuizQuestion]
    answers: List[QuizAnswer]
