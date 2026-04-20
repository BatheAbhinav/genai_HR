from typing import Any, TypedDict


class GraphState(TypedDict):
    question: str
    policy_type: str | None      # detected policy domain (leave, insurance, …)
    agent_type: str              # "policy" | "helpdesk"
    user_id: str
    session: Any
    normalized_question: str
    retrieved_rows: list[dict]
    confidence: float
    answer: str
    citations: list[dict]
    escalation_required: bool
    follow_up_questions: list[str]
