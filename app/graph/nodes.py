"""Top-level graph nodes.

Exposes the single shared node used by every query path:

  normalize_question_node — cleans the raw question string before it reaches
                            the helpdesk orchestrator.

Query classification and routing is handled by helpdesk_agent_node.
"""


def normalize_question_node(state: dict) -> dict:
    normalized = " ".join(state["question"].split()).strip()
    return {"normalized_question": normalized}
