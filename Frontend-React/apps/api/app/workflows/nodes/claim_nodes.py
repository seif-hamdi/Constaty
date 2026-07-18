"""LangGraph nodes for the claim collection workflow.

Each node receives the GraphState, performs its task, and returns
a partial state update. The graph controls the flow between nodes.
"""
from __future__ import annotations
import datetime

from app.schemas.claim import Claim, ClaimStatus, YesNo
from app.repositories.claims import store
from app.workflows.claim_state import GraphState
from app.workflows.question_catalogue import (
    QUESTION_MAP, QUESTION_ORDER,
    first_question_id, next_question_id,
    to_question,
)
from app.services.claim_validation import (
    get_field, set_field, missing_mandatory,
    validate_claim, completeness_score, ready_for_review,
)


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


# ── Node: normalize_input ──

def normalize_input(state: GraphState) -> dict:
    """Prepare the user input for processing. In Phase 3, text is already normalized.
    Voice/document/image normalization arrives in Phase 4."""
    return {
        "assistant_message": None,
        "finished": False,
    }


# ── Node: extract_and_merge ──

def extract_and_merge(state: GraphState) -> dict:
    """Extract field updates from the user message and merge into the Claim."""
    claim = store.get(state["claim_id"])
    if not claim:
        return {"finished": True, "assistant_message": "Claim not found."}

    qid = state.get("current_question_id", "")
    message = state.get("last_message", "").strip()

    if not qid or qid not in QUESTION_MAP or not message:
        # No answer to process — just find the next question
        return {}

    q = QUESTION_MAP[qid]
    path = q["field_path"]
    input_type = state.get("last_input_type", "text")

    # Parse and set the field
    if q["type"] == "yes_no":
        v = message.strip().lower()
        if v in ("oui", "yes", "نعم", "o"):
            set_field(claim, path, YesNo.OUI)
        elif v in ("non", "no", "لا", "n"):
            set_field(claim, path, YesNo.NON)
    elif q["type"] == "date":
        normalized = message
        if "/" in message:
            parts = message.split("/")
            if len(parts) == 3:
                normalized = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        set_field(claim, path, normalized)
    elif q["type"] == "time":
        set_field(claim, path, message)
    else:
        set_field(claim, path, message)

    # Record provenance
    claim.field_sources[path] = input_type
    claim.field_confidences[path] = 0.90
    claim.field_confirmations[path] = True
    claim.updated_at = _now()
    store[claim.id] = claim

    return {}


# ── Node: validate ──

def validate(state: GraphState) -> dict:
    """Run validation checks on the current claim."""
    claim = store.get(state["claim_id"])
    if not claim:
        return {"finished": True}

    missing = missing_mandatory(claim)
    issues = validate_claim(claim)
    score = completeness_score(claim)
    is_ready = ready_for_review(claim)

    # Update claim status
    if is_ready:
        claim.status = ClaimStatus.READY_FOR_REVIEW
    elif missing:
        claim.status = ClaimStatus.COLLECTING
    claim.updated_at = _now()
    store[claim.id] = claim

    return {
        "missing_fields": missing,
        "validation_issues": issues,
        "completeness_score": score,
        "ready_for_review": is_ready,
    }


# ── Node: choose_next ──

def choose_next(state: GraphState) -> dict:
    """Determine the next question to ask, or signal readiness for review.

    Priority:
    1. If ready_for_review → finished
    2. Find first unanswered mandatory question
    3. If none → finished (ready for review even with warnings)
    """
    if state.get("ready_for_review"):
        return {"next_question_id": None, "finished": True}

    claim = store.get(state["claim_id"])
    if not claim:
        return {"next_question_id": None, "finished": True}

    # Find first unanswered question
    for qid in QUESTION_ORDER:
        q = QUESTION_MAP[qid]
        val = get_field(claim, q["field_path"])
        if val is None or (isinstance(val, str) and val.strip() == ""):
            return {"next_question_id": qid, "finished": False}

    # All questions answered
    return {"next_question_id": None, "finished": True}


# ── Node: prepare_response ──

def prepare_response(state: GraphState) -> dict:
    """Build the assistant message for the next question or review."""
    if state.get("finished"):
        return {
            "assistant_message": "Toutes les questions obligatoires sont complétées. Vous pouvez passer à la vérification.",
        }

    qid = state.get("next_question_id")
    if qid and qid in QUESTION_MAP:
        lang = state.get("language", "fr")
        q = QUESTION_MAP[qid]
        prompt = q["prompt_translations"].get(lang, q["prompt"])
        return {"assistant_message": prompt}

    return {"assistant_message": None}