from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import Chunk
from app.db.repositories import create_document, save_chunks
from app.ingestion.embedder import get_embedding_client
from app.ingestion.loader import load_pdf_documents
from app.ingestion.splitter import split_documents
from app.observability.tracing import log_ingestion


def ingest_policy_pdf(
    session: Session,
    file_path: str,
    title: str,
    policy_type: str,
    version: str,
    uploaded_by: str,
):
    docs = load_pdf_documents(file_path)
    chunks = split_documents(docs)

    document = create_document(
        session=session,
        title=title,
        policy_type=policy_type,
        version=version,
        uploaded_by=uploaded_by,
        source_filename=Path(file_path).name,
    )

    embedding_client = get_embedding_client()
    chunk_texts = [chunk.page_content for chunk in chunks]
    vectors = embedding_client.embed_documents(chunk_texts)

    chunk_records = []
    for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=False)):
        chunk_records.append(
            Chunk(
                doc_id=document.doc_id,
                chunk_index=index,
                chunk_text=chunk.page_content,
                page_number=chunk.metadata.get("page"),
                section=chunk.metadata.get("section"),
                policy_type=policy_type,
                version=version,
                embedding=vector,
                metadata_json={
                    "source": chunk.metadata.get("source"),
                    "page": chunk.metadata.get("page"),
                },
            )
        )

    save_chunks(session, chunk_records)
    session.commit()

    log_ingestion(title=title, policy_type=policy_type, chunk_count=len(chunk_records))
    return document
