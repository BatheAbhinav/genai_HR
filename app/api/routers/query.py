from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas.query import QueryRequest, QueryResponse
from app.db.engine import get_db_session
from app.graph.workflow import run_policy_query


router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def query_policy_assistant(
    payload: QueryRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    try:
        result = run_policy_query(
            session=session,
            question=payload.question,
            user_id=current_user["user_id"],
            policy_type=payload.policy_type,
        )
        return result
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {exc}",
        ) from exc
