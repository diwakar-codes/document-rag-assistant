from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService


class RetrievalService:

    @staticmethod
    def retrieve(query: str, top_k: int = 5):

        query_embedding = EmbeddingService.model.encode(
            query,
            normalize_embeddings=True
        ).tolist()

        pinecone = PineconeService()

        results = pinecone.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        response = []

        for match in results.matches:
            response.append(
                {
                    "score": match.score,
                    "page": match.metadata.get("page"),
                    "text": match.metadata.get("text"),
                }
            )
        
        return response