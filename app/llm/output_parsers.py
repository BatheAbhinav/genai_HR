from typing import Literal

from pydantic import BaseModel, Field


class PolicyAnswerSchema(BaseModel):
    answer: str = Field(description="Concise answer based solely on the provided policy context")
    follow_up_questions: list[str] = Field(
        description="2-3 relevant follow-up questions the user might want to ask next",
        min_length=2,
        max_length=3,
    )


class OrchestratorRoutingSchema(BaseModel):
    route: Literal[
        "leave",
        "insurance",
        "hr-guidelines",
        "compensation",
        "remote-work",
        "general",
        "labour-law",
    ] = Field(description="The specialist agent that should handle this query")
    reasoning: str = Field(description="Brief explanation of why this route was chosen")


class HelpdeskAnswerSchema(BaseModel):
    answer: str = Field(
        description=(
            "Plain-language answer grounded in the web search results. "
            "Includes a disclaimer that this is general information, not legal advice."
        )
    )
    follow_up_questions: list[str] = Field(
        description="2-3 relevant follow-up questions the employee might want to explore",
        min_length=2,
        max_length=3,
    )
