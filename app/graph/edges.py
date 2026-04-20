"""Build the multi-agent LangGraph workflow.

Graph topology
--------------

  normalize_question
        │
  helpdesk_agent  (orchestrator — LLM classifies query and sets routing state)
        │
  ┌─────┴──────────────────────────────────────────────────────────────────┐
  │  (policy_type == "leave")          leave_agent ──────────────────── END│
  │  (policy_type == "insurance")      insurance_agent ───────────────── END│
  │  (policy_type == "hr-guidelines")  hr_guidelines_agent ────────────── END│
  │  (policy_type == "compensation")   compensation_agent ─────────────── END│
  │  (policy_type == "remote-work")    remote_work_agent ──────────────── END│
  │  (policy_type == "general")        general_agent ──────────────────── END│
  │  (policy_type == "labour-law")     labour_law_agent ───────────────── END│
  └────────────────────────────────────────────────────────────────────────┘

Each *_agent node handles retrieval, evidence grading, answer generation, and
citation building for its domain. The labour_law_agent uses web search instead
of the internal DB.
"""

from langgraph.graph import END, StateGraph

from app.graph.agents.helpdesk_agent import helpdesk_agent_node
from app.graph.agents.labour_law_agent import labour_law_agent_node
from app.graph.agents.policy_agent import (
    compensation_agent_node,
    general_agent_node,
    hr_guidelines_agent_node,
    insurance_agent_node,
    leave_agent_node,
    remote_work_agent_node,
)
from app.graph.nodes import normalize_question_node


# ---------------------------------------------------------------------------
# Routing function (called after helpdesk_agent orchestrator)
# ---------------------------------------------------------------------------

_POLICY_TYPE_TO_NODE: dict[str, str] = {
    "leave": "leave_agent",
    "insurance": "insurance_agent",
    "hr-guidelines": "hr_guidelines_agent",
    "compensation": "compensation_agent",
    "remote-work": "remote_work_agent",
    "general": "general_agent",
    "labour-law": "labour_law_agent",
}


def _route_after_orchestrator(state: dict) -> str:
    policy_type = state.get("policy_type") or "general"
    return _POLICY_TYPE_TO_NODE.get(policy_type, "general_agent")


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph(graph_state_type):
    builder = StateGraph(graph_state_type)

    # Shared nodes
    builder.add_node("normalize_question", normalize_question_node)
    builder.add_node("helpdesk_agent", helpdesk_agent_node)

    # Specialist agent nodes
    builder.add_node("leave_agent", leave_agent_node)
    builder.add_node("insurance_agent", insurance_agent_node)
    builder.add_node("hr_guidelines_agent", hr_guidelines_agent_node)
    builder.add_node("compensation_agent", compensation_agent_node)
    builder.add_node("remote_work_agent", remote_work_agent_node)
    builder.add_node("general_agent", general_agent_node)
    builder.add_node("labour_law_agent", labour_law_agent_node)

    # Edges
    builder.set_entry_point("normalize_question")
    builder.add_edge("normalize_question", "helpdesk_agent")

    builder.add_conditional_edges(
        "helpdesk_agent",
        _route_after_orchestrator,
        {
            "leave_agent": "leave_agent",
            "insurance_agent": "insurance_agent",
            "hr_guidelines_agent": "hr_guidelines_agent",
            "compensation_agent": "compensation_agent",
            "remote_work_agent": "remote_work_agent",
            "general_agent": "general_agent",
            "labour_law_agent": "labour_law_agent",
        },
    )

    # All specialist agents terminate the graph.
    for node in (
        "leave_agent",
        "insurance_agent",
        "hr_guidelines_agent",
        "compensation_agent",
        "remote_work_agent",
        "general_agent",
        "labour_law_agent",
    ):
        builder.add_edge(node, END)

    return builder.compile()
