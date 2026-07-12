from app.core.config import settings
from app.services.bm25_service import BM25Service
from app.services.embedding_service import EmbeddingService
from app.services.groq_service import GroqService
from app.services.pinecone_service import PineconeService
from app.services.store_service import StoreService


class RetrievalService:

    @staticmethod
    def retrieve_dense(query: str, top_k: int = 5, document_id: str = None):

        query_embedding = EmbeddingService.model.encode(
            query,
            normalize_embeddings=True
        ).tolist()

        pinecone = PineconeService()

        query_kwargs = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True,
        }

        if document_id:
            query_kwargs["filter"] = {"document_id": {"$eq": document_id}}

        results = pinecone.index.query(**query_kwargs)

        response = []

        for match in results.matches:
            response.append({
                "score": match.score,
                "document_id": match.metadata.get("document_id"),
                "filename": match.metadata.get("filename"),
                "page": match.metadata.get("page"),
                "chunk_id": match.metadata.get("chunk_id"),
                "topic": match.metadata.get("topic"),
                "text": match.metadata.get("text"),
            })

        return response

    @staticmethod
    def retrieve_bm25(query: str, top_k: int = 5, document_id: str = None):

        chunks = StoreService.list_chunks(document_id=document_id)

        results = BM25Service.retrieve(query, chunks, top_k=top_k)

        for result in results:
            result["score"] = result["bm25_score"]

        return results

    @staticmethod
    def _normalize(values):
        if not values:
            return []

        lo, hi = min(values), max(values)

        if hi == lo:
            return [1.0 for _ in values]

        return [(value - lo) / (hi - lo) for value in values]

    @staticmethod
    def retrieve_hybrid(
        query: str,
        top_k: int = 5,
        document_id: str = None,
        alpha: float = None,
    ):
        """
        Combine dense (Pinecone) and BM25 (local corpus) retrieval.

        Both candidate pools are min-max normalized to [0, 1] and merged
        with a weighted sum: score = alpha * dense + (1 - alpha) * bm25.
        """

        alpha = settings.HYBRID_ALPHA if alpha is None else alpha
        candidate_pool = settings.BM25_CANDIDATE_POOL

        dense_results = RetrievalService.retrieve_dense(
            query, top_k=candidate_pool, document_id=document_id
        )
        bm25_results = RetrievalService.retrieve_bm25(
            query, top_k=candidate_pool, document_id=document_id
        )

        def key_of(result):
            return (result["document_id"], result["chunk_id"])

        merged = {}

        dense_scores = RetrievalService._normalize(
            [result["score"] for result in dense_results]
        )
        for result, norm_score in zip(dense_results, dense_scores):
            merged[key_of(result)] = {
                **result,
                "dense_score": norm_score,
                "bm25_score": 0.0,
            }

        bm25_scores = RetrievalService._normalize(
            [result["score"] for result in bm25_results]
        )
        for result, norm_score in zip(bm25_results, bm25_scores):
            key = key_of(result)
            if key in merged:
                merged[key]["bm25_score"] = norm_score
            else:
                merged[key] = {
                    **result,
                    "dense_score": 0.0,
                    "bm25_score": norm_score,
                }

        for entry in merged.values():
            entry["score"] = round(
                alpha * entry["dense_score"] + (1 - alpha) * entry["bm25_score"],
                4,
            )

        ranked = sorted(
            merged.values(),
            key=lambda entry: entry["score"],
            reverse=True,
        )

        return ranked[:top_k]

    @staticmethod
    def retrieve(
        query: str,
        top_k: int = 5,
        mode: str = "dense",
        document_id: str = None,
    ):
        if mode == "bm25":
            return RetrievalService.retrieve_bm25(
                query, top_k=top_k, document_id=document_id
            )

        if mode == "hybrid":
            return RetrievalService.retrieve_hybrid(
                query, top_k=top_k, document_id=document_id
            )

        return RetrievalService.retrieve_dense(
            query, top_k=top_k, document_id=document_id
        )

    @staticmethod
    def chat(question: str, mode: str = "dense", top_k: int = 5):

        chunks = RetrievalService.retrieve(question, top_k=top_k, mode=mode)

        answer = GroqService.generate(
            question,
            chunks,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": chunks,
        }
