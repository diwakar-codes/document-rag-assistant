from rank_bm25 import BM25Okapi


class BM25Service:

    @staticmethod
    def retrieve(question: str, chunks: list, top_k: int = 5):
        """
        Perform BM25 keyword retrieval over a list of chunk dicts.
        Each chunk must contain a "text" key.
        """

        if not chunks:
            return []

        tokenized_chunks = [
            chunk["text"].lower().split()
            for chunk in chunks
        ]

        bm25 = BM25Okapi(tokenized_chunks)

        tokenized_query = question.lower().split()

        scores = bm25.get_scores(tokenized_query)

        ranked = sorted(
            zip(chunks, scores),
            key=lambda pair: pair[1],
            reverse=True,
        )

        return [
            {**chunk, "bm25_score": float(score)}
            for chunk, score in ranked[:top_k]
        ]
