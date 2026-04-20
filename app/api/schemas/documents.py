from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    doc_id: str
    title: str
    policy_type: str
    version: str
    uploaded_by: str


class DocumentResponse(BaseModel):
    doc_id: str
    title: str
    policy_type: str
    version: str
    status: str
    uploaded_by: str
    source_filename: str
    created_at: datetime
    effective_date: Optional[datetime] = None
