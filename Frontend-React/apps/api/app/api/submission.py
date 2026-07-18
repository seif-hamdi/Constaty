"""Submission and sinistre endpoints — Phase 6 & 7."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.claim import ClaimStatus
from app.repositories.claims import store
from app.services.claim_validation import missing_mandatory, validate_claim, completeness_score, ready_for_review
from app.services.pdf_generator import generate_constat_pdf
from app.services.sinistre_service import create_sinistre, get_sinistre, list_sinistres

router = APIRouter(tags=["submission"])


@router.post("/claims/{claim_id}/preview")
async def generate_preview(claim_id: str):
    """Generate the filled constat PDF preview."""
    claim = store.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found.", "retryable": False})

    pdf_path = generate_constat_pdf(claim)
    pdf_filename = pdf_path.split("\\")[-1].split("/")[-1]
    claim.constat_pdf_url = f"/storage/generated/{pdf_filename}"
    store[claim_id] = claim

    return {"constat_pdf_url": claim.constat_pdf_url}


@router.post("/claims/{claim_id}/submit")
async def submit_claim(claim_id: str):
    """Submit the claim and create a sinistre package."""
    claim = store.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found.", "retryable": False})

    # Check minimum readiness
    missing = missing_mandatory(claim)
    is_ready = ready_for_review(claim)

    # Submit regardless — but flag if not fully ready
    sinistre = create_sinistre(claim)
    store[claim_id] = claim  # claim status updated to SUBMITTED

    return {
        "sinistre_id": sinistre.sinistre_id,
        "claim_id": claim.id,
        "status": claim.status.value,
        "constat_pdf_url": claim.constat_pdf_url,
        "submitted_at": sinistre.submitted_at.isoformat() if sinistre.submitted_at else None,
        "completeness_score": sinistre.completeness.score,
        "missing_fields_count": len(sinistre.completeness.missing_fields),
        "sinistre": sinistre.model_dump(mode="json"),
    }


@router.get("/sinistres")
async def list_all_sinistres():
    """List all sinistres — for insurer integration."""
    return {"sinistres": [s.model_dump(mode="json") for s in list_sinistres()]}


@router.get("/sinistres/{sinistre_id}")
async def get_sinistre_by_id(sinistre_id: str):
    """Get a specific sinistre package — for insurer integration."""
    s = get_sinistre(sinistre_id)
    if not s:
        raise HTTPException(status_code=404, detail={"code": "SINISTRE_NOT_FOUND", "message": "Sinistre not found.", "retryable": False})
    return s.model_dump(mode="json")