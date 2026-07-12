from app.services.retrieval_service import RetrievalService
from app.services.groq_service import GroqService
from app.memory.conversation import memory

SIMILARITY_THRESHOLD = 0.10


def retrieve_node(state):
    question = state["question"]

    sources = RetrievalService.retrieve(question)

    print("Retrieved Sources:", sources)

    filtered_sources = [
        source
        for source in sources
        if source["score"] >= SIMILARITY_THRESHOLD
    ]

    print("Filtered Sources:", filtered_sources)

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