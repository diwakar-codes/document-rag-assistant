import json
import threading
from datetime import datetime, timezone
from pathlib import Path

STORE_PATH = Path("app/data/store.json")
STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()

_EMPTY_STORE = {
    "documents": {},
    "chunks": [],
    "quiz_attempts": [],
}


class StoreService:
    """Lightweight JSON-file persistence for document/chunk/quiz metadata.

    There is no database in this project by design. Embeddings live in
    Pinecone; this store only keeps the metadata needed to browse documents,
    run BM25/hybrid retrieval over the full corpus, and track quiz history.
    """

    @staticmethod
    def _read():
        if not STORE_PATH.exists():
            return json.loads(json.dumps(_EMPTY_STORE))

        with open(STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _write(data):
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def add_document(document_id, filename, file_type, total_pages, extraction_method):
        with _lock:
            data = StoreService._read()

            data["documents"][document_id] = {
                "document_id": document_id,
                "filename": filename,
                "file_type": file_type,
                "total_pages": total_pages,
                "total_chunks": 0,
                "topics": [],
                "extraction_method": extraction_method,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            }

            StoreService._write(data)

    @staticmethod
    def add_chunks(document_id, chunks):
        with _lock:
            data = StoreService._read()

            data["chunks"].extend(chunks)

            if document_id in data["documents"]:
                doc_chunks = [
                    c for c in data["chunks"] if c["document_id"] == document_id
                ]

                data["documents"][document_id]["total_chunks"] = len(doc_chunks)

                topics = sorted(
                    {c["topic"] for c in doc_chunks if c.get("topic")}
                )

                data["documents"][document_id]["topics"] = topics

            StoreService._write(data)

    @staticmethod
    def list_documents():
        data = StoreService._read()
        return sorted(
            data["documents"].values(),
            key=lambda d: d["uploaded_at"],
            reverse=True,
        )

    @staticmethod
    def get_document(document_id):
        return StoreService._read()["documents"].get(document_id)

    @staticmethod
    def delete_document(document_id):
        with _lock:
            data = StoreService._read()
            data["documents"].pop(document_id, None)
            data["chunks"] = [
                c for c in data["chunks"] if c["document_id"] != document_id
            ]
            StoreService._write(data)

    @staticmethod
    def list_chunks(document_id: str = None, topic: str = None):
        chunks = StoreService._read()["chunks"]

        if document_id:
            chunks = [c for c in chunks if c["document_id"] == document_id]

        if topic:
            chunks = [c for c in chunks if c.get("topic") == topic]

        return chunks

    @staticmethod
    def list_topics():
        chunks = StoreService._read()["chunks"]

        topics = {}

        for chunk in chunks:
            topic = chunk.get("topic")

            if not topic:
                continue

            entry = topics.setdefault(
                topic,
                {"topic": topic, "documents": set(), "chunks": 0},
            )

            entry["documents"].add(chunk["filename"])
            entry["chunks"] += 1

        return [
            {
                "topic": entry["topic"],
                "documents": sorted(entry["documents"]),
                "chunks": entry["chunks"],
            }
            for entry in sorted(topics.values(), key=lambda t: t["topic"])
        ]

    @staticmethod
    def add_quiz_attempt(attempt: dict):
        with _lock:
            data = StoreService._read()
            data["quiz_attempts"].append(attempt)
            StoreService._write(data)

    @staticmethod
    def list_quiz_attempts():
        return StoreService._read()["quiz_attempts"]

    @staticmethod
    def analytics_summary():
        data = StoreService._read()

        documents = data["documents"]
        chunks = data["chunks"]
        attempts = data["quiz_attempts"]

        topics = {c["topic"] for c in chunks if c.get("topic")}

        scored_attempts = [a for a in attempts if a.get("total")]
        average_score = (
            sum(a["score"] / a["total"] for a in scored_attempts)
            / len(scored_attempts)
            * 100
            if scored_attempts
            else 0.0
        )

        weak_topics = {}
        for attempt in attempts:
            for topic, correct in attempt.get("topic_results", {}).items():
                stats = weak_topics.setdefault(topic, {"correct": 0, "total": 0})
                stats["correct"] += correct["correct"]
                stats["total"] += correct["total"]

        weakest = sorted(
            (
                {"topic": t, "accuracy": round(s["correct"] / s["total"] * 100, 1)}
                for t, s in weak_topics.items()
                if s["total"]
            ),
            key=lambda x: x["accuracy"],
        )[:5]

        return {
            "total_documents": len(documents),
            "total_chunks": len(chunks),
            "topics_learned": len(topics),
            "quizzes_taken": len(attempts),
            "average_score": round(average_score, 1),
            "weak_topics": weakest,
        }
