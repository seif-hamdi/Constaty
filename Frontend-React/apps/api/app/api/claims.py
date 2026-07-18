"""Claims endpoints — Phase 3: LangGraph orchestrated guided flow."""
from __future__ import annotations
import uuid
import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schemas.claim import Claim, ClaimStatus, Language, YesNo
from app.schemas.question import Question
from app.repositories.claims import store
from app.workflows.question_catalogue import (
    QUESTION_MAP, QUESTION_ORDER,
    first_question_id, to_question,
)
from app.workflows.claim_graph import get_claim_graph
from app.services.claim_validation import (
    get_field, set_field, missing_mandatory, validate_claim,
    completeness_score, ready_for_review,
)

router = APIRouter(prefix="/claims", tags=["claims"])


# ── Request / Response models ──

class CreateClaimRequest(BaseModel):
    language: str = "fr"


class TurnRequest(BaseModel):
    message: str = ""
    input_type: str = "text"
    question_id: Optional[str] = None


# ── Helpers ──

def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def _current_question_id(claim: Claim) -> str:
    """Return the first unanswered question id, or empty string if all done."""
    for qid in QUESTION_ORDER:
        q = QUESTION_MAP[qid]
        val = get_field(claim, q["field_path"])
        if val is None or (isinstance(val, str) and val.strip() == ""):
            return qid
    return ""


def _claim_response(claim: Claim, lang: str = "fr", assistant_msg: str | None = None):
    qid = _current_question_id(claim)
    next_q = to_question(qid, lang).model_dump(mode="json") if qid else None
    return {
        "id": claim.id,
        "public_token": claim.public_token,
        "status": claim.status.value,
        "claim": claim.model_dump(mode="json"),
        "next_question": next_q,
        "assistant_message": assistant_msg,
        "missing_fields": missing_mandatory(claim),
        "validation_issues": validate_claim(claim),
        "progress": completeness_score(claim),
    }


# ── Endpoints ──

@router.post("")
async def create_claim(body: CreateClaimRequest):
    cid = f"claim_{uuid.uuid4().hex[:10]}"
    now = _now()
    claim = Claim(
        id=cid,
        public_token=cid,
        status=ClaimStatus.COLLECTING,
        language=Language(body.language),
        created_at=now,
        updated_at=now,
    )
    store[cid] = claim

    # Initialize the LangGraph thread for this claim
    graph = get_claim_graph()
    initial_state = {
        "claim_id": cid,
        "language": body.language,
        "last_message": "",
        "last_input_type": "text",
        "current_question_id": "",
        "next_question_id": first_question_id(),
        "clarification_count": 0,
        "max_clarifications": 3,
        "missing_fields": missing_mandatory(claim),
        "validation_issues": [],
        "completeness_score": 0,
        "ready_for_review": False,
        "pending_clarification": None,
        "clarification_message": None,
        "assistant_message": None,
        "finished": False,
    }
    config = {"configurable": {"thread_id": cid}}
    graph.invoke(initial_state, config=config)

    return _claim_response(claim, body.language)


@router.get("/{claim_id}")
async def get_claim(claim_id: str):
    claim = store.get(claim_id)
    if not claim:
        raise HTTPException(
            status_code=404,
            detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found.", "retryable": False},
        )
    return _claim_response(claim, claim.language.value)


@router.post("/{claim_id}/turn")
async def submit_turn(claim_id: str, body: TurnRequest):
    claim = store.get(claim_id)
    if not claim:
        raise HTTPException(
            status_code=404,
            detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found.", "retryable": False},
        )

    # Determine which question we're answering
    qid = body.question_id or _current_question_id(claim)
    if not qid:
        # No more questions
        if ready_for_review(claim):
            claim.status = ClaimStatus.READY_FOR_REVIEW
        claim.updated_at = _now()
        store[claim.id] = claim
        return _claim_response(claim, claim.language.value)

    # Run through the LangGraph workflow
    graph = get_claim_graph()
    config = {"configurable": {"thread_id": claim_id}}

    turn_state = {
        "claim_id": claim_id,
        "language": claim.language.value,
        "last_message": body.message,
        "last_input_type": body.input_type,
        "current_question_id": qid,
        "clarification_count": 0,
        "max_clarifications": 3,
        "next_question_id": None,
        "missing_fields": [],
        "validation_issues": [],
        "completeness_score": 0,
        "ready_for_review": False,
        "pending_clarification": None,
        "clarification_message": None,
        "assistant_message": None,
        "finished": False,
    }

    result = graph.invoke(turn_state, config=config)

    # Reload claim (graph nodes updated it in the store)
    claim = store.get(claim_id)
    assistant_msg = result.get("assistant_message") if isinstance(result, dict) else None

    return _claim_response(claim, claim.language.value, assistant_msg)


@router.post("/{claim_id}/validate")
async def validate_claim_endpoint(claim_id: str):
    claim = store.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found.", "retryable": False})
    return {
        "missing_fields": missing_mandatory(claim),
        "validation_issues": validate_claim(claim),
        "completeness_score": completeness_score(claim),
        "ready_for_review": ready_for_review(claim),
    }