from app.services.retrieval_service import RetrievalService
from app.services.groq_service import GroqService

def retrieve_node(state):
    question = state["question"]
    sources = RetrievalService.retrieve(question)

    return {
        "sources": sources,
        "has_context": len(sources) > 0
    }


def generate_node(state):
    answer = GroqService.generate(
        state["question"],
        state["sources"]
    )

    return {
        "answer": answer
    }

def no_context_node(state):
    return {
        "answer": (
            "I couldn't find any relevant information "
            "in the uploaded documents"
        )
    }

def route_after_retrieval(state):

    if state["has_context"]:
        return "generate"

    return "no_context"

    