from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService
from app.services.groq_service import GroqService


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
            include_metadata=True,
        )

        response = []

        for match in results.matches:
            response.append({
                "score": match.score,
                "document_id": match.metadata.get("document_id"),
                "filename": match.metadata.get("filename"),
                "page": match.metadata.get("page"),
                "chunk_id": match.metadata.get("chunk_id"),
                "text": match.metadata.get("text"),
            })

        return response

    @staticmethod
    def chat(question: str):

        chunks = RetrievalService.retrieve(question)

        answer = GroqService.generate(
            question,
            chunks,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": chunks,
        }