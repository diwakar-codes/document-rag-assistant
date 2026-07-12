from typing import List, Optional

from pydantic import BaseModel


class FlashcardRequest(BaseModel):
    topic: str
    num_cards: int = 10


class StudyPlanRequest(BaseModel):
    topics: Optional[List[str]] = None
    hours_per_day: float = 2.0
