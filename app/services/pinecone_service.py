from pinecone import Pinecone
from app.core.config import settings

class PineconeService:

    def __init__(self):
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = pc.Index(settings.PINECONE_INDEX)

    def upsert_chunks(self, chunks):
        vectors = []

        for chunk in chunks:

            vectors.append(
                {
                    "id": f"chunk-{chunk['chunk_id']}",
                    "values": chunk["embedding"],
                    "metadata": {
                        "page": chunk["page"],
                        "text": chunk["text"],
                    },
                }
            )

        self.index.upsert(vectors=vectors)