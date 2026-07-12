from app.core.config import settings
from app.services.retrieval_service import RetrievalService
from app.services.groq_service import GroqService
from app.memory.conversation import memory


def retrieve_node(state):
    question = state["question"]
    mode = state.get("mode") or "dense"
    top_k = state.get("top_k") or settings.DEFAULT_TOP_K
    document_id = state.get("document_id")

    sources = RetrievalService.retrieve(
        question,
        top_k=top_k,
        mode=mode,
        document_id=document_id,
    )

    if mode == "bm25":
        # Raw BM25 scores are unbounded, so the similarity threshold
        # (tuned for cosine similarity) does not apply in this mode.
        filtered_sources = sources
    else:
        filtered_sources = [
            source
            for source in sources
            if source.get("score", 0) >= settings.SIMILARITY_THRESHOLD
        ]

    return {
        "sources": filtered_sources,
        "has_context": len(filtered_sources) > 0,
    }


def generate_node(state):
    answer = GroqService.generate(
        question=state["question"],
        chunks=state["sources"],
        history=state["history"],
    )

    memory.add(
        "user",
        state["question"],
    )

    memory.add(
        "assistant",
        answer,
    )

    return {
        "answer": answer,
    }


def no_context_node(state):
    return {
        "answer": (
            "I couldn't find any relevant information "
            "in the uploaded documents."
        )
    }


def route_after_retrieval(state):
    if state["has_context"]:
        return "generate"

    return "no_context"


def memory_node(state):
    history = memory.get_history()

    return {
        "history": history,
    }