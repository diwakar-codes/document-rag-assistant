from groq import Groq

from app.core.config import settings

class GroqService:
    client = Groq(
        api_key=settings.GROQ_API_KEY
    )

    @staticmethod
    def build_prompt(question, chunks):

        context = "\n\n".join(
            chunk["text"]
            for chunk in chunks
        )

        return f"""
    You are an intelligent document assistant.

    Answer ONLY using the context below.

    If the answer is not present, say:

    "I couldn't find that information in the uploaded documents."

    Context:

    {context}

    Question:

    {question}
    """

    @staticmethod
    def generate(question, chunks, history=None):

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
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0,
        )

        return response.choices[0].message.content
