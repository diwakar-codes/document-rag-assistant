import json
import re
import uuid

from app.core.config import settings
from app.services.groq_service import GroqService
from app.services.store_service import StoreService

MAX_CONTEXT_CHUNKS = 30

QUESTION_TYPE_INSTRUCTIONS = {
    "mcq": "multiple choice questions with exactly 4 options each",
    "true_false": 'true/false questions (options must be exactly ["True", "False"])',
    "fill_blank": "fill-in-the-blank questions (no options; correct_answer is the missing word/phrase)",
    "mixed": "a mix of multiple choice, true/false, and fill-in-the-blank questions",
}


class QuizService:

    @staticmethod
    def _build_prompt(topic, context, difficulty, num_questions, question_type):
        type_instructions = QUESTION_TYPE_INSTRUCTIONS.get(
            question_type, QUESTION_TYPE_INSTRUCTIONS["mixed"]
        )

        return f"""You are an expert quiz creator for a student studying "{topic}".

Using ONLY the study notes below, generate {num_questions} {difficulty}-difficulty \
quiz questions ({type_instructions}).

Study notes:

{context}

Return ONLY a JSON array with this exact structure, no commentary, no markdown fences:
[
  {{
    "type": "mcq | true_false | fill_blank",
    "question": "...",
    "options": ["...", "..."] or null,
    "correct_answer": "...",
    "explanation": "why this is correct, referencing the notes"
  }}
]"""

    @staticmethod
    def _parse(content: str) -> list:
        cleaned = re.sub(
            r"^```(json)?|```$", "", content.strip(), flags=re.MULTILINE
        ).strip()
        return json.loads(cleaned)

    @staticmethod
    def generate(topic, difficulty="medium", num_questions=5, question_type="mixed"):
        chunks = StoreService.list_chunks(topic=topic)

        if not chunks:
            raise ValueError(f"No content found for topic '{topic}'.")

        context = "\n\n".join(
            chunk["text"] for chunk in chunks[:MAX_CONTEXT_CHUNKS]
        )
        reference = chunks[0]["filename"]

        prompt = QuizService._build_prompt(
            topic, context, difficulty, num_questions, question_type
        )

        response = GroqService.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        raw_questions = QuizService._parse(response.choices[0].message.content)

        questions = []
        for index, raw in enumerate(raw_questions[:num_questions], start=1):
            questions.append({
                "id": index,
                "type": raw.get("type", "mcq"),
                "question": raw.get("question", ""),
                "options": raw.get("options"),
                "correct_answer": str(raw.get("correct_answer", "")),
                "explanation": raw.get("explanation", ""),
                "reference": reference,
            })

        return {
            "quiz_id": str(uuid.uuid4()),
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions,
        }

    @staticmethod
    def evaluate(topic: str, questions: list, answers: list) -> dict:
        answer_map = {answer["question_id"]: answer["answer"] for answer in answers}

        results = []
        correct_count = 0

        for question in questions:
            given = answer_map.get(question["id"], "")
            is_correct = (
                given.strip().lower()
                == str(question["correct_answer"]).strip().lower()
            )

            if is_correct:
                correct_count += 1

            results.append({
                "question_id": question["id"],
                "question": question["question"],
                "given_answer": given,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
                "explanation": question.get("explanation", ""),
                "reference": question.get("reference"),
            })

        total = len(questions)
        accuracy = round(correct_count / total * 100, 1) if total else 0.0

        return {
            "topic": topic,
            "score": correct_count,
            "total": total,
            "accuracy": accuracy,
            "results": results,
        }
