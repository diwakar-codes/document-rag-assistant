"""
Standalone RAG evaluation harness, judged by Groq (no OpenAI key required).

Indexes a small fixture document under a throwaway document_id, runs each
sample question through the real retrieval + generation pipeline, scores
the results with DeepEval metrics (faithfulness, answer relevancy,
contextual precision, contextual recall), then removes the fixture data.

Usage (from the project root, with the venv active):
    python -m eval.evaluate_rag
"""
import json
import statistics
import time
import uuid
from pathlib import Path

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from app.services.embedding_service import EmbeddingService
from app.services.groq_service import GroqService
from app.services.pinecone_service import PineconeService
from app.services.retrieval_service import RetrievalService
from app.services.store_service import StoreService
from eval.groq_eval_model import GroqEvalModel

DATASET_PATH = Path(__file__).parent / "dataset.json"
FIXTURE_FILENAME = "eval_fixture_cpu_scheduling.txt"


def index_fixture(fixture_text: str) -> str:
    document_id = f"eval-{uuid.uuid4()}"

    chunks = [{
        "document_id": document_id,
        "filename": FIXTURE_FILENAME,
        "page": 1,
        "chunk_id": 1,
        "text": fixture_text,
        "topic": "Evaluation Fixture",
    }]

    embedded = EmbeddingService.embed_chunks(chunks)
    PineconeService().upsert_chunks(embedded)

    StoreService.add_document(
        document_id=document_id,
        filename=FIXTURE_FILENAME,
        file_type=".txt",
        total_pages=1,
        extraction_method="fixture",
    )
    StoreService.add_chunks(document_id, chunks)

    # Pinecone upserts are not always instantly queryable.
    time.sleep(2)

    return document_id


def cleanup_fixture(document_id: str):
    StoreService.delete_document(document_id)
    try:
        PineconeService().delete_by_document(document_id)
    except Exception:
        pass


def run():
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    fixture_text = dataset["fixture_text"]

    document_id = index_fixture(fixture_text)

    judge = GroqEvalModel()
    metrics = [
        FaithfulnessMetric(model=judge, include_reason=False),
        AnswerRelevancyMetric(model=judge, include_reason=False),
        ContextualPrecisionMetric(model=judge, include_reason=False),
        ContextualRecallMetric(model=judge, include_reason=False),
    ]

    results = []

    try:
        for item in dataset["questions"]:
            sources = RetrievalService.retrieve(
                item["question"], top_k=5, mode="dense", document_id=document_id
            )
            if not sources:
                sources = [{"text": fixture_text, "filename": FIXTURE_FILENAME, "page": 1}]

            contexts = [source["text"] for source in sources]
            answer = GroqService.generate(item["question"], sources)

            test_case = LLMTestCase(
                input=item["question"],
                actual_output=answer,
                expected_output=item["ground_truth"],
                retrieval_context=contexts,
            )

            row = {"question": item["question"], "answer": answer}

            for metric in metrics:
                name = metric.__class__.__name__
                try:
                    row[name] = round(metric.measure(test_case), 3)
                except Exception as exc:
                    row[name] = None
                    print(f"  [warning] {name} failed: {exc}")

            results.append(row)
    finally:
        cleanup_fixture(document_id)

    print("\n=== RAG Evaluation Results ===\n")
    for row in results:
        print(f"Q: {row['question']}")
        print(f"A: {row['answer'][:150]}")
        for metric in metrics:
            print(f"  {metric.__class__.__name__}: {row[metric.__class__.__name__]}")
        print()

    print("=== Averages ===")
    for metric in metrics:
        name = metric.__class__.__name__
        scored = [row[name] for row in results if row[name] is not None]
        avg = round(statistics.mean(scored), 3) if scored else None
        print(f"{name}: {avg}")


if __name__ == "__main__":
    run()
