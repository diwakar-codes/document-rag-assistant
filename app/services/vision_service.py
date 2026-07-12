import base64

from groq import Groq

from app.core.config import settings


class VisionService:

    client = Groq(api_key=settings.GROQ_API_KEY)

    OCR_PROMPT = (
        "Extract all text from this image exactly as written, including "
        "handwritten notes, tables, and numbers. Preserve line breaks where "
        "meaningful. Return only the extracted text with no commentary."
    )

    @staticmethod
    def extract_text_from_image(image_bytes: bytes, mime_type: str = "image/png") -> str:
        encoded = base64.b64encode(image_bytes).decode("utf-8")

        response = VisionService.client.chat.completions.create(
            model=settings.GROQ_VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VisionService.OCR_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{encoded}"
                            },
                        },
                    ],
                }
            ],
            temperature=0,
        )

        return response.choices[0].message.content.strip()
