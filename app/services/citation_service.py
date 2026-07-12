class CitationService:

    @staticmethod
    def format_sources(sources: list) -> list:
        formatted = []

        for index, source in enumerate(sources, start=1):
            filename = source.get("filename") or "Unknown document"
            page = source.get("page")

            reference = filename if not page else f"{filename} (Page {page})"

            formatted.append({
                **source,
                "label": f"Source {index}",
                "reference": reference,
                "score": round(source.get("score") or 0.0, 4),
            })

        return formatted
