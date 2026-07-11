import pdfplumber
from app.utils.text_cleaner import TextCleaner

class PDFService:

    @staticmethod
    def extract_text(pdf_path:str) -> dict:
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                text = TextCleaner.clean(text)
                pages.append(
                    {
                        "page": page_number,
                        "text": text.strip()
                    }
                )
        return {
            "total_pages": len(pages),
            "pages": pages
        }