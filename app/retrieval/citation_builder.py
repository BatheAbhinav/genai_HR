def build_citations(retrieved_rows: list[dict]):
    citations = []
    for row in retrieved_rows:
        citations.append(
            {
                "doc_id": str(row["doc_id"]),
                "title": row.get("title", "Policy Document"),
                "page": row.get("page_number"),
                "section": row.get("section"),
                "snippet": row.get("chunk_text", "")[:280],
                "version": row.get("version", "v1"),
            }
        )
    return citations
