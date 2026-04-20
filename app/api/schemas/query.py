from typing import Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    policy_type: Optional[str] = None


class Citation(BaseModel):
    doc_id: str
    title: str
    page: Optional[int] = None
    section: Optional[str] = None
    snippet: str
    version: str


class QueryResponse(BaseModel):
    request_id: str
    answer: str
    citations: list[Citation]
    confidence: float
    escalation_required: bool
    follow_up_questions: list[str]
