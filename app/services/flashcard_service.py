import json
import re

from app.core.config import settings
from app.services.groq_service import GroqService
from app.services.store_service import StoreService

MAX_CONTEXT_CHUNKS = 30


class FlashcardService:

    @staticmethod
    def _parse(content: str) -> list:
        cleaned = re.sub(
            r"^```(json)?|```$", "", content.strip(), flags=re.MULTILINE
        ).strip()
        return json.loads(cleaned)

    @staticmethod
    def generate(topic: str, num_cards: int = 10):
        chunks = StoreService.list_chunks(topic=topic)

        if not chunks:
            raise ValueError(f"No content found for topic '{topic}'.")

        context = "\n\n".join(
            chunk["text"] for chunk in chunks[:MAX_CONTEXT_CHUNKS]
        )

        prompt = f"""Create {num_cards} concise flashcards for the topic "{topic}" \
using ONLY the study notes below. Each flashcard front should be a short \
question or term, and the back a concise answer or definition.

Study notes:

{context}

Return ONLY a JSON array, no commentary, no markdown fences:
[{{"front": "...", "back": "..."}}]"""

        response = GroqService.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        raw_cards = FlashcardService._parse(response.choices[0].message.content)

        return {
            "topic": topic,
            "flashcards": [
                {
                    "front": card.get("front", ""),
                    "back": card.get("back", ""),
                }
                for card in raw_cards[:num_cards]
            ],
        }
