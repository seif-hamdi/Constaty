"""LangGraph claim state — the graph state object passed between nodes."""
from __future__ import annotations
from typing import Optional, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from app.schemas.claim import Claim, ValidationIssue


class GraphState(TypedDict):
    """State carried through the claim collection graph.

    Each claim uses its claim_id as the LangGraph thread_id,
    so the graph can resume the exact claim after a pause.
    """
    claim_id: str
    language: str

    # Latest user input
    last_message: str
    last_input_type: str  # text, voice, document, image
    current_question_id: str

    # Workflow control
    next_question_id: Optional[str]
    clarification_count: int
    max_clarifications: int

    # Validation results
    missing_fields: list[str]
    validation_issues: list[dict]
    completeness_score: int
    ready_for_review: bool

    # Clarification
    pending_clarification: Optional[str]  # question id that needs clarification
    clarification_message: Optional[str]

    # Response
    assistant_message: Optional[str]
    finished: bool