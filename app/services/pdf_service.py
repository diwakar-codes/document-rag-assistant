import io
from pathlib import Path

import pdfplumber
import pypdfium2 as pdfium

from app.core.config import settings
from app.services.vision_service import VisionService
from app.utils.text_cleaner import TextCleaner


class PDFService:

    @staticmethod
    def extract_text(pdf_path: str) -> dict:
        pages = []
        low_text_pages = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                text = TextCleaner.clean(text).strip()

                pages.append({"page": page_number, "text": text})

                if len(text) < settings.OCR_MIN_CHARS_PER_PAGE:
                    low_text_pages.append(page_number)

        extraction_method = "pdfplumber"

        if low_text_pages:
            extraction_method = (
                "groq_vision"
                if len(low_text_pages) == len(pages)
                else "pdfplumber+groq_vision"
            )

            pdf_doc = pdfium.PdfDocument(pdf_path)

            for page_number in low_text_pages:
                pdf_page = pdf_doc[page_number - 1]
                bitmap = pdf_page.render(scale=2)
                pil_image = bitmap.to_pil()

                buffer = io.BytesIO()
                pil_image.save(buffer, format="PNG")

                ocr_text = VisionService.extract_text_from_image(buffer.getvalue())
                pages[page_number - 1]["text"] = TextCleaner.clean(ocr_text).strip()

            pdf_doc.close()

        return {
            "total_pages": len(pages),
            "pages": pages,
            "extraction_method": extraction_method,
        }

    @staticmethod
    def extract_text_from_image_file(image_path: str) -> dict:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        extension = Path(image_path).suffix.lower().lstrip(".")
        mime_type = f"image/{'jpeg' if extension == 'jpg' else extension}"

        text = VisionService.extract_text_from_image(image_bytes, mime_type=mime_type)
        text = TextCleaner.clean(text).strip()

        return {
            "total_pages": 1,
            "pages": [{"page": 1, "text": text}],
            "extraction_method": "groq_vision",
        }
