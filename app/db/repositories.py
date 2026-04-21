from __future__ import annotations

from typing import Iterable

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document, QueryAudit


def create_document(
    session: Session,
    title: str,
    policy_type: str,
    version: str,
    uploaded_by: str,
    source_filename: str,
):
    document = Document(
        title=title,
        policy_type=policy_type,
        version=version,
        uploaded_by=uploaded_by,
        source_filename=source_filename,
    )
    session.add(document)
    session.flush()
    return document


def save_chunks(session: Session, chunks: Iterable[Chunk]) -> None:
    session.add_all(list(chunks))


def fetch_documents(session: Session, limit: int = 100):
    return (
        session.query(Document)
        .order_by(Document.created_at.desc())
        .limit(limit)
        .all()
    )


def fetch_document_by_id(session: Session, doc_id: str):
    return session.get(Document, doc_id)


# def semantic_search(
#     session: Session,
#     query_embedding: list[float],
#     top_k: int,
#     policy_type: str | None = None,
# ):
#     base_sql = """
#         SELECT
#             c.chunk_id,
#             c.doc_id,
#             c.chunk_text,
#             c.page_number,
#             c.section,
#             c.policy_type,
#             c.version,
#             d.title,
#             (1 - (c.embedding <=> :query_embedding::vector)) AS similarity
#         FROM chunks c
#         JOIN documents d ON d.doc_id = c.doc_id
#         WHERE d.status = 'active'
#     """

#     if policy_type:
#         base_sql += " AND c.policy_type = :policy_type "

#     base_sql += " ORDER BY c.embedding <=> :query_embedding::vector LIMIT :top_k"

#     params = {"query_embedding": str(query_embedding), "top_k": top_k}
#     if policy_type:
#         params["policy_type"] = policy_type

#     rows = session.execute(text(base_sql), params).mappings().all()
#     return [dict(row) for row in rows]

def semantic_search(
    session: Session,
    query_embedding: list[float],
    top_k: int,
    policy_type: str | None = None,
):
    # Change ::vector to CAST(:query_embedding AS vector)
    base_sql = """
        SELECT 
            c.chunk_id, 
            c.doc_id, 
            c.chunk_text, 
            c.page_number, 
            c.section, 
            c.policy_type, 
            c.version, 
            d.title,
            (1 - (c.embedding <=> CAST(:query_embedding AS vector))) AS similarity
        FROM chunks c
        JOIN documents d ON d.doc_id = c.doc_id
        WHERE d.status = 'active'
    """

    if policy_type:
        base_sql += " AND c.policy_type = :policy_type "

    # Apply the same CAST fix to the ORDER BY clause
    base_sql += " ORDER BY c.embedding <=> CAST(:query_embedding AS vector) LIMIT :top_k"

    # Note: Ensure query_embedding is passed as a string/list that pgvector understands
    params = {"query_embedding": str(query_embedding), "top_k": top_k}
    if policy_type:
        params["policy_type"] = policy_type

    rows = session.execute(text(base_sql), params).mappings().all()
    return [dict(row) for row in rows]


def save_query_audit(
    session: Session,
    user_id: str,
    question: str,
    answer: str,
    confidence: float,
    escalation_required: bool,
    retrieved_chunk_ids: list[str],
    latency_ms: int,
):
    audit = QueryAudit(
        user_id=user_id,
        question=question,
        answer=answer,
        confidence=confidence,
        escalation_required=escalation_required,
        retrieved_chunk_ids=retrieved_chunk_ids,
        latency_ms=latency_ms,
    )
    session.add(audit)
    session.flush()
    return audit
