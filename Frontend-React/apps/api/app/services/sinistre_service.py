"""Sinistre creation — transforms a submitted claim into a SinistrePackage
for the insurer-facing platform (Part 2).
"""
from __future__ import annotations
import uuid
import datetime
from pathlib import Path

from app.schemas.claim import Claim, ClaimStatus
from app.schemas.sinistre import (
    SinistrePackage, CompletenessInfo, ConsistencyInfo, AssessmentStatus,
)
from app.services.claim_validation import (
    missing_mandatory, validate_claim, completeness_score,
)
from app.services.pdf_generator import generate_constat_pdf


# In-memory sinistre store (Phase 1; replace with Supabase later)
sinistre_store: dict[str, SinistrePackage] = {}


def create_sinistre(claim: Claim) -> SinistrePackage:
    """Create a SinistrePackage from a submitted claim."""
    # Generate the PDF
    pdf_path = generate_constat_pdf(claim)
    pdf_filename = Path(pdf_path).name

    # Build completeness
    missing = missing_mandatory(claim)
    score = completeness_score(claim)
    uncertain = [
        path for path, conf in claim.field_confidences.items()
        if conf < 0.7 and path not in missing
    ]

    # Build consistency issues
    issues = validate_claim(claim)
    consistency_issues = [
        {"code": i["code"], "severity": i["severity"], "message": i["message"], "field_path": i.get("field_path")}
        for i in issues if i["severity"] != "blocking"
    ]

    sinistre_id = f"sin_{uuid.uuid4().hex[:10]}"
    now = datetime.datetime.now(datetime.timezone.utc)

    # Mark claim as submitted
    claim.status = ClaimStatus.SUBMITTED
    claim.submitted_at = now
    claim.constat_pdf_url = f"/storage/generated/{pdf_filename}"

    package = SinistrePackage(
        schema_version="1.0",
        sinistre_id=sinistre_id,
        claim_id=claim.id,
        submitted_at=now,
        claim=claim.model_dump(mode="json"),
        constat_pdf_url=claim.constat_pdf_url,
        evidence=[e.model_dump(mode="json") for e in claim.evidence],
        completeness=CompletenessInfo(
            score=score,
            missing_fields=missing,
            uncertain_fields=uncertain,
        ),
        consistency=ConsistencyInfo(
            score=None,
            issues=consistency_issues,
        ),
        damage_assessment=None,
        cost_estimate=None,
        assessment_status=AssessmentStatus.PENDING,
        expert_review=None,
    )

    sinistre_store[sinistre_id] = package
    return package


def get_sinistre(sinistre_id: str) -> SinistrePackage | None:
    return sinistre_store.get(sinistre_id)


def list_sinistres() -> list[SinistrePackage]:
    return list(sinistre_store.values())