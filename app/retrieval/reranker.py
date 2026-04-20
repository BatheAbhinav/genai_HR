def diversity_rerank(rows: list[dict], top_k: int) -> list[dict]:
    """
    Diversity-aware reranking: greedily select top_k chunks, preferring
    results from different source documents to avoid redundant context.

    Strategy:
    1. Sort all candidates by similarity descending.
    2. First pass: pick the best chunk per unique doc_id.
    3. Second pass: fill any remaining slots with the next-best unused chunks.
    """
    if len(rows) <= top_k:
        return rows

    sorted_rows = sorted(rows, key=lambda r: -float(r.get("similarity", 0)))
    selected: list[dict] = []
    seen_docs: set = set()

    # First pass: one best chunk per document
    for row in sorted_rows:
        if row["doc_id"] not in seen_docs:
            selected.append(row)
            seen_docs.add(row["doc_id"])
        if len(selected) == top_k:
            return selected

    # Second pass: fill remaining slots from highest-similarity unused rows
    selected_set = set(id(r) for r in selected)
    for row in sorted_rows:
        if id(row) not in selected_set:
            selected.append(row)
            selected_set.add(id(row))
        if len(selected) == top_k:
            break

    return selected


def score_evidence(retrieved_rows: list[dict]) -> float:
    """Compute mean cosine similarity as a confidence proxy."""
    if not retrieved_rows:
        return 0.0
    similarities = [max(0.0, float(row.get("similarity", 0.0))) for row in retrieved_rows]
    return round(sum(similarities) / len(similarities), 3)
