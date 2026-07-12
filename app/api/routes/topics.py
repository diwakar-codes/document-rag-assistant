from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.services.groq_service import GroqService
from app.services.store_service import StoreService

router = APIRouter(prefix="/topics", tags=["Topics"])

MAX_SUMMARY_CHUNKS = 40


@router.get("/")
def list_topics():
    return StoreService.list_topics()


@router.get("/{topic}/summary")
def topic_summary(topic: str):
    chunks = StoreService.list_chunks(topic=topic)

    if not chunks:
        raise HTTPException(status_code=404, detail="Topic not found.")

    context = "\n\n".join(
        chunk["text"] for chunk in chunks[:MAX_SUMMARY_CHUNKS]
    )

    prompt = f"""Summarize the following study notes on the topic "{topic}" into \
a clear, well-organized study summary. Use headings and bullet points where helpful.

Notes:

{context}"""

    response = GroqService.client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.DEFAULT_TEMPERATURE,
    )

    return {
        "topic": topic,
        "summary": response.choices[0].message.content,
        "source_chunks": len(chunks),
    }
