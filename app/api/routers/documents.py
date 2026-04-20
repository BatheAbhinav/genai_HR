import tempfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas.documents import DocumentResponse, DocumentUploadResponse
from app.db.engine import get_db_session
from app.db.repositories import fetch_document_by_id, fetch_documents
from app.ingestion.pipeline import ingest_policy_pdf


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(
    title: str = Form(...),
    policy_type: str = Form(...),
    version: str = Form("v1"),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can upload policy documents",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
            tmp.write(file.file.read())
            tmp.flush()
            document = ingest_policy_pdf(
                session=session,
                file_path=tmp.name,
                title=title,
                policy_type=policy_type,
                version=version,
                uploaded_by=current_user["user_id"],
            )
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {exc}",
        ) from exc

    return {
        "doc_id": str(document.doc_id),
        "title": document.title,
        "policy_type": document.policy_type,
        "version": document.version,
        "uploaded_by": document.uploaded_by,
    }


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    _ = current_user
    docs = fetch_documents(session)
    return [
        {
            "doc_id": str(doc.doc_id),
            "title": doc.title,
            "policy_type": doc.policy_type,
            "version": doc.version,
            "status": doc.status,
            "uploaded_by": doc.uploaded_by,
            "source_filename": doc.source_filename,
            "created_at": doc.created_at,
            "effective_date": doc.effective_date,
        }
        for doc in docs
    ]


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    _ = current_user
    doc = fetch_document_by_id(session, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return {
        "doc_id": str(doc.doc_id),
        "title": doc.title,
        "policy_type": doc.policy_type,
        "version": doc.version,
        "status": doc.status,
        "uploaded_by": doc.uploaded_by,
        "source_filename": doc.source_filename,
        "created_at": doc.created_at,
        "effective_date": doc.effective_date,
    }
