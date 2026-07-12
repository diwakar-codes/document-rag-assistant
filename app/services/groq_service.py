from groq import Groq

from app.core.config import settings

class GroqService:
    client = Groq(
        api_key=settings.GROQ_API_KEY
    )

    @staticmethod
    def build_prompt(question, chunks):

        context = "\n\n".join(
            f"[Source {index}: {chunk.get('filename', 'Unknown')}"
            f"{', Page ' + str(chunk['page']) if chunk.get('page') else ''}]\n"
            f"{chunk['text']}"
            for index, chunk in enumerate(chunks, start=1)
        )

        return f"""
    You are an intelligent document assistant.

    Answer ONLY using the context below. When your answer relies on a
    specific source, mention it inline as (Source N).

    If the answer is not present, say:

    "I couldn't find that information in the uploaded documents."

    Context:

    {context}

    Question:

    {question}
    """

    @staticmethod
    def generate(question, chunks, history=None, temperature=None, max_tokens=None):

        prompt = GroqService.build_prompt(
            question,
            chunks
        )

        messages = list(history) if history else []
        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = GroqService.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=(
                settings.DEFAULT_TEMPERATURE if temperature is None else temperature
            ),
            max_tokens=(
                settings.DEFAULT_MAX_TOKENS if max_tokens is None else max_tokens
            ),
        )

        return response.choices[0].message.content
