"""Factory that creates a LangGraph node function for a given policy domain.

Each generated node:
  1. Retrieves relevant chunks from the DB (filtered by policy_type).
  2. Grades the evidence (mean cosine similarity).
  3a. If confidence is sufficient  → generates an answer from DB context (with citations).
  3b. If confidence is too low     → falls back to a domain-scoped DuckDuckGo web search
                                     and generates an answer from those results (no citations,
                                     includes a disclaimer to verify with HR).
"""

import logging

from langchain_community.tools import DuckDuckGoSearchRun

from app.llm.gemini_client import get_chat_model
from app.llm.output_parsers import HelpdeskAnswerSchema, PolicyAnswerSchema
from app.llm.prompts import RAG_PROMPT, WEB_FALLBACK_PROMPT
from app.retrieval.citation_builder import build_citations
from app.retrieval.reranker import score_evidence
from app.retrieval.retriever import retrieve_policy_context

logger = logging.getLogger(__name__)

_search_tool = DuckDuckGoSearchRun()
_MAX_SEARCH_CHARS = 4000


_AGENT_DESCRIPTIONS: dict[str, str] = {
    "leave": (
        "You are a Leave Policy specialist. "
        "Your expertise covers vacation, sick leave, PTO, parental leave, sabbaticals, and absence management."
    ),
    "insurance": (
        "You are a Benefits and Insurance specialist. "
        "Your expertise covers health, dental, vision, medical coverage, HSA/FSA, premiums, deductibles, and claims."
    ),
    "hr-guidelines": (
        "You are an HR Guidelines specialist. "
        "Your expertise covers code of conduct, harassment policies, performance reviews, onboarding, "
        "disciplinary procedures, and workplace standards."
    ),
    "compensation": (
        "You are a Compensation and Payroll specialist. "
        "Your expertise covers salaries, bonuses, equity, overtime pay, payroll cycles, raises, and commissions."
    ),
    "remote-work": (
        "You are a Remote Work Policy specialist. "
        "Your expertise covers work-from-home guidelines, hybrid schedules, home office expenses, "
        "telecommuting eligibility, and distributed-team policies."
    ),
    "general": (
        "You are a general HR Policy assistant. "
        "You help employees find answers across all company policy areas."
    ),
}

_ESCALATION_FOLLOW_UPS: dict[str, list[str]] = {
    "leave": [
        "Would you like me to route this to the Leave Management team?",
        "Can you share more about the type of leave you need?",
        "Do you know which policy document this relates to?",
    ],
    "insurance": [
        "Would you like me to route this to the Benefits team?",
        "Can you clarify which type of coverage you are asking about?",
        "Do you have your benefits enrollment details handy?",
    ],
    "hr-guidelines": [
        "Would you like me to escalate this to HR?",
        "Can you provide more context about your situation?",
        "Is this related to a specific HR process or incident?",
    ],
    "compensation": [
        "Would you like me to connect you with Payroll or Finance?",
        "Can you share more about the compensation component in question?",
        "Is this about your current role or a future offer?",
    ],
    "remote-work": [
        "Would you like me to route this to your manager or HR?",
        "Can you clarify whether this is about a one-off arrangement or permanent setup?",
        "Do you know your team's current remote-work tier?",
    ],
    "general": [
        "Would you like me to route this to HR support?",
        "Can you share more context about your department or situation?",
        "Do you know which specific policy document this relates to?",
    ],
}


def make_policy_agent_node(policy_type: str):
    """Return a LangGraph node function bound to *policy_type*.

    The node name (used in graph routing) is derived from the policy_type string.
    """
    agent_description = _AGENT_DESCRIPTIONS.get(policy_type, _AGENT_DESCRIPTIONS["general"])
    escalation_follow_ups = _ESCALATION_FOLLOW_UPS.get(policy_type, _ESCALATION_FOLLOW_UPS["general"])

    def _agent_node(state: dict) -> dict:
        question = state["normalized_question"]
        session = state["session"]

        # --- Retrieval ---
        rows = retrieve_policy_context(
            session=session,
            question=question,
            policy_type=policy_type if policy_type != "general" else None,
        )

        # --- Evidence grading ---
        confidence = score_evidence(rows)
        if confidence < 0.45 or not rows:
            # DB didn't have enough — fall back to a domain-scoped web search.
            search_query = f"{policy_type} policy workplace {question}"
            try:
                raw = _search_tool.run(search_query)
                search_results = raw[:_MAX_SEARCH_CHARS]
            except Exception as exc:  # noqa: BLE001
                logger.warning("Web search fallback failed for %s agent: %s", policy_type, exc)
                search_results = (
                    "Web search is temporarily unavailable. "
                    "Please advise the employee to contact HR directly for this information."
                )

            prompt = WEB_FALLBACK_PROMPT.format_messages(
                agent_description=agent_description,
                question=question,
                policy_type=policy_type,
                search_results=search_results,
            )
            llm = get_chat_model()
            result = llm.with_structured_output(HelpdeskAnswerSchema).invoke(prompt)

            return {
                "retrieved_rows": [],
                "confidence": confidence,
                "escalation_required": False,
                "answer": result.answer,
                "citations": [],
                "follow_up_questions": result.follow_up_questions,
            }

        # --- Answer generation ---
        context_lines = [
            f"[Doc: {row.get('title')} | Page: {row.get('page_number')}] {row.get('chunk_text')}"
            for row in rows
        ]

        prompt = RAG_PROMPT.format_messages(
            question=question,
            policy_type=policy_type,
            context="\n\n".join(context_lines),
            agent_description=agent_description,
        )

        llm = get_chat_model()
        result = llm.with_structured_output(PolicyAnswerSchema).invoke(prompt)
        citations = build_citations(rows)

        return {
            "retrieved_rows": rows,
            "confidence": confidence,
            "escalation_required": False,
            "answer": result.answer,
            "citations": citations,
            "follow_up_questions": result.follow_up_questions,
        }

    _agent_node.__name__ = f"{policy_type.replace('-', '_')}_agent_node"
    return _agent_node


# Pre-built agent nodes — imported directly into the graph.
leave_agent_node = make_policy_agent_node("leave")
insurance_agent_node = make_policy_agent_node("insurance")
hr_guidelines_agent_node = make_policy_agent_node("hr-guidelines")
compensation_agent_node = make_policy_agent_node("compensation")
remote_work_agent_node = make_policy_agent_node("remote-work")
general_agent_node = make_policy_agent_node("general")
