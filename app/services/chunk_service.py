from app.core.config import settings

class ChunkService:
    @staticmethod
    def split(document: dict, document_id: str, filename: str):
        chunks = []

        chunk_id = 1

        for page in document["pages"]:

            text = page["text"]
            page_number = page["page"]

            start = 0

            while start < len(text):

                end = start + settings.CHUNK_SIZE

                chunk = text[start:end]

                chunks.append(
                    {
                        "document_id": document_id,
                        "filename": filename,
                        "page": page_number,
                        "chunk_id": chunk_id,
                        "text": chunk,
                    }
                )

                chunk_id += 1

                start += (
                    settings.CHUNK_SIZE
                    - settings.CHUNK_OVERLAP
                )

        return chunks