"""Helpdesk orchestrator: classifies incoming employee queries and routes them
to the appropriate specialist agent.

Routing targets
---------------
  leave          → LeaveAgent          (vacation, PTO, sick leave, parental leave …)
  insurance      → InsuranceAgent      (health/dental/vision, HSA/FSA, premiums …)
  hr-guidelines  → HRGuidelinesAgent   (conduct, harassment, onboarding, reviews …)
  compensation   → CompensationAgent   (salary, bonuses, equity, payroll …)
  remote-work    → RemoteWorkAgent     (WFH, hybrid, home-office expenses …)
  labour-law     → LabourLawAgent      (national/regional laws, FMLA, OSHA, ADA …)
  general        → GeneralAgent        (catch-all company policy questions)
"""

import logging

from app.llm.gemini_client import get_chat_model
from app.llm.output_parsers import OrchestratorRoutingSchema
from app.llm.prompts import ORCHESTRATOR_PROMPT

logger = logging.getLogger(__name__)


def helpdesk_agent_node(state: dict) -> dict:
    """LangGraph orchestrator node: classify the query and set routing state."""
    question = state["normalized_question"]

    prompt = ORCHESTRATOR_PROMPT.format_messages(question=question)
    llm = get_chat_model()
    result = llm.with_structured_output(OrchestratorRoutingSchema).invoke(prompt)

    logger.info("Orchestrator routed '%s...' → %s (reason: %s)", question[:60], result.route, result.reasoning)

    return {
        "policy_type": result.route,
        "agent_type": "policy" if result.route != "labour-law" else "helpdesk",
    }
