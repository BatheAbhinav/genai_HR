from sqlalchemy.orm import Session

from app.config.settings import settings
from app.db.repositories import semantic_search
from app.ingestion.embedder import get_embedding_client
from app.retrieval.reranker import diversity_rerank


def retrieve_policy_context(
    session: Session,
    question: str,
    policy_type: str | None = None,
    top_k: int | None = None,
):
    k = top_k or settings.top_k
    fetch_k = k * settings.fetch_k_multiplier

    embedding_client = get_embedding_client()
    query_embedding = embedding_client.embed_query(question)

    candidates = semantic_search(
        session=session,
        query_embedding=query_embedding,
        top_k=fetch_k,
        policy_type=policy_type,
    )

    return diversity_rerank(candidates, top_k=k)
