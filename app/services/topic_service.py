import json
import re

from app.core.config import settings
from app.services.groq_service import GroqService

BATCH_SIZE = 8
DEFAULT_TOPIC = "General"


class TopicService:

    @staticmethod
    def _build_prompt(batch: list) -> str:
        chunk_blocks = "\n\n".join(
            f"Chunk {chunk['chunk_id']}:\n{chunk['text'][:800]}"
            for chunk in batch
        )

        return f"""You are labeling study notes with short, consistent topic names \
(2-4 words each, e.g. "CPU Scheduling", "Deadlocks", "Memory Management"). \
Use the SAME topic name for chunks covering the same subject.

Assign ONE topic to each chunk below.

{chunk_blocks}

Return ONLY a JSON array, no commentary, in this exact form:
[{{"chunk_id": <id>, "topic": "<topic>"}}]"""

    @staticmethod
    def _parse_response(content: str) -> dict:
        cleaned = re.sub(
            r"^```(json)?|```$", "", content.strip(), flags=re.MULTILINE
        ).strip()

        try:
            parsed = json.loads(cleaned)
        except (json.JSONDecodeError, TypeError):
            return {}

        return {
            item["chunk_id"]: item["topic"]
            for item in parsed
            if isinstance(item, dict) and "chunk_id" in item and "topic" in item
        }

    @staticmethod
    def assign_topics(chunks: list) -> list:
        if not chunks:
            return chunks

        for start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[start:start + BATCH_SIZE]

            try:
                response = GroqService.client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": TopicService._build_prompt(batch),
                        }
                    ],
                    temperature=0,
                )
                topic_map = TopicService._parse_response(
                    response.choices[0].message.content
                )
            except Exception:
                topic_map = {}

            for chunk in batch:
                chunk["topic"] = topic_map.get(chunk["chunk_id"], DEFAULT_TOPIC)

        return chunks
