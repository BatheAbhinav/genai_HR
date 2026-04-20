import time

from app.db.repositories import save_query_audit
from app.graph.edges import build_graph
from app.graph.state import GraphState
from app.observability.tracing import log_query


policy_graph = build_graph(GraphState)


def run_policy_query(session, question: str, user_id: str, policy_type: str | None = None):
    started = time.time()

    initial_state = {
        "question": question,
        "policy_type": policy_type,
        "agent_type": "",
        "user_id": user_id,
        "session": session,
        "normalized_question": "",
        "retrieved_rows": [],
        "confidence": 0.0,
        "answer": "",
        "citations": [],
        "escalation_required": False,
        "follow_up_questions": [],
    }

    output = policy_graph.invoke(initial_state)
    latency_ms = int((time.time() - started) * 1000)

    log_query(
        user_id=user_id,
        question=question,
        confidence=output["confidence"],
        escalated=output["escalation_required"],
        latency_ms=latency_ms,
    )

    audit = save_query_audit(
        session=session,
        user_id=user_id,
        question=question,
        answer=output["answer"],
        confidence=output["confidence"],
        escalation_required=output["escalation_required"],
        retrieved_chunk_ids=[str(row["chunk_id"]) for row in output.get("retrieved_rows", [])],
        latency_ms=latency_ms,
    )
    session.commit()

    return {
        "request_id": str(audit.request_id),
        "answer": output["answer"],
        "citations": output["citations"],
        "confidence": output["confidence"],
        "escalation_required": output["escalation_required"],
        "follow_up_questions": output.get("follow_up_questions", []),
    }
