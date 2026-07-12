import uuid

from pinecone import Pinecone

from app.core.config import settings


class PineconeService:

    def __init__(self):
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = pc.Index(settings.PINECONE_INDEX)

    def upsert_chunks(self, embeddings):
        vectors = []

        for embedding in embeddings:

            vectors.append(
                {
                    "id": str(uuid.uuid4()),
                    "values": embedding["embedding"],
                    "metadata": {
                        "document_id": embedding["document_id"],
                        "filename": embedding["filename"],
                        "page": embedding["page"],
                        "chunk_id": embedding["chunk_id"],
                        "text": embedding["text"],
                    },
                }
            )

        self.index.upsert(vectors=vectors)