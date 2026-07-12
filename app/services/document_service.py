from pathlib import Path

from app.services.pdf_service import PDFService


class DocumentService:

    @staticmethod
    def extract(file_path: str, document_id, filename):
        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return PDFService.extract_text(file_path)

        raise ValueError("Unsupported document type.")