"""Labour Law agent: answers questions about national/regional workplace laws.

Uses DuckDuckGo web search to find relevant laws and regulations, then
generates a plain-language answer with an appropriate legal disclaimer.
"""

import logging

from langchain_community.tools import DuckDuckGoSearchRun

from app.llm.gemini_client import get_chat_model
from app.llm.output_parsers import HelpdeskAnswerSchema
from app.llm.prompts import HELPDESK_PROMPT

logger = logging.getLogger(__name__)

_search_tool = DuckDuckGoSearchRun()
_MAX_SEARCH_CHARS = 4000


def labour_law_agent_node(state: dict) -> dict:
    """LangGraph node: web-search-grounded answers for national/regional workplace-law queries."""
    question = state["normalized_question"]

    search_query = f"employee workplace law regulation rights: {question}"

    try:
        raw_results = _search_tool.run(search_query)
        search_results = raw_results[:_MAX_SEARCH_CHARS]
    except Exception as exc:  # noqa: BLE001
        logger.warning("DuckDuckGo search failed in labour_law_agent: %s", exc)
        search_results = (
            "Web search is temporarily unavailable. "
            "Please advise the employee to consult an official government labour website "
            "or an employment lawyer for authoritative information."
        )

    prompt = HELPDESK_PROMPT.format_messages(
        question=question,
        search_results=search_results,
    )

    llm = get_chat_model()
    result = llm.with_structured_output(HelpdeskAnswerSchema).invoke(prompt)

    return {
        "retrieved_rows": [],
        "confidence": 1.0,
        "escalation_required": False,
        "answer": result.answer,
        "citations": [],
        "follow_up_questions": result.follow_up_questions,
    }
