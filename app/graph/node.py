from app.services.retrieval_service import RetrievalService
from app.services.groq_service import GroqService

def retrieve_node(state):
    question = state["question"]
    sources = RetrievalService.retrieve(question)

    return {
        "sources": sources
    }


def generate_node(state):
    answer = GroqService.generate(
        state["question"],
        state["sources"]
    )

    return {
        "answer": answer
    }