from deepeval.models.base_model import DeepEvalBaseLLM

from app.core.config import settings
from app.services.groq_service import GroqService


class GroqEvalModel(DeepEvalBaseLLM):
    """Wraps Groq as a DeepEval judge model, avoiding an OpenAI dependency."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.GROQ_MODEL

    def load_model(self):
        return GroqService.client

    def generate(self, prompt: str) -> str:
        response = GroqService.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return self.model_name
