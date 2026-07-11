from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:

    # Load once when the application starts
    model = SentenceTransformer(settings.EMBEDDING_MODEL)

    @staticmethod
    def embed_chunks(chunks: list):
        embeddings = []

        for chunk in chunks:

            vector = EmbeddingService.model.encode(
                chunk["text"],
                normalize_embeddings=True
            )

            embeddings.append(
                {
                    **chunk,
                    "embedding": vector.tolist()
                }
            )

        return embeddings