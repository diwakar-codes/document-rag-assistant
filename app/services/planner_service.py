from app.core.config import settings
from app.services.groq_service import GroqService
from app.services.store_service import StoreService


class PlannerService:

    @staticmethod
    def generate_plan(topics: list = None, hours_per_day: float = 2.0):
        analytics = StoreService.analytics_summary()
        all_topics = [entry["topic"] for entry in StoreService.list_topics()]

        if not all_topics:
            raise ValueError(
                "No topics available yet. Upload and process documents first."
            )

        target_topics = topics or all_topics
        weak_topic_names = {entry["topic"] for entry in analytics["weak_topics"]}

        topic_lines = "\n".join(
            f"- {topic}" + (" (weak area, prioritize)" if topic in weak_topic_names else "")
            for topic in target_topics
        )

        prompt = f"""Create a personalized study plan for a student covering these topics:

{topic_lines}

The student can study {hours_per_day} hours per day. Prioritize weak areas first.
Return a concise day-by-day plan with an estimated total study time. Use clear
headings and bullet points. No preamble."""

        response = GroqService.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.DEFAULT_TEMPERATURE,
        )

        return {
            "topics": target_topics,
            "weak_topics": sorted(weak_topic_names),
            "plan": response.choices[0].message.content,
        }
