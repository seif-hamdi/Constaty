"""Upload and analysis endpoints — Phase 4 & 5: multimodal input and damage."""
from __future__ import annotations
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.schemas.claim import EvidenceRef, DetectedDamage, DamageZone, DamageType, Severity
from app.repositories.claims import store
from app.services import storage, transcription, document_extraction, damage_analysis

router = APIRouter(prefix="/claims", tags=["uploads"])


@router.post("/{claim_id}/audio")
async def upload_audio(
    claim_id: str,
    file: UploadFile = File(...),
    language: str = Form("fr"),
):
    """Upload audio for transcription."""
    claim = store.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found.", "retryable": False})

    meta = await storage.save_upload(claim_id, file, prefix="audio")
    result = transcription.transcribe(meta["path"], language)

    # Store evidence
    ev = EvidenceRef(id=meta["id"], type="audio", url=meta["url"], metadata={"transcript": result.get("transcript", "")})
    claim.evidence.append(ev)
    store[claim_id] = claim

    return {
        "transcript": result.get("transcript", ""),
        "detected_language": result.get("detected_language", language),
        "confidence": result.get("confidence", 0.0),
        "error": result.get("error"),
        "evidence_id": meta["id"],
    }


@router.post("/{claim_id}/evidence")
async def upload_evidence(
    claim_id: str,
    file: UploadFile = File(...),
    type: str = Form("damage_photo"),
    vehicle: str = Form(""),
):
    """Upload a document, damage photo, or scene photo."""
    claim = store.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found.", "retryable": False})

    meta = await storage.save_upload(claim_id, file, prefix=type)

    ev = EvidenceRef(
        id=meta["id"],
        type=type,
        url=meta["url"],
        vehicle=vehicle or None,
        metadata={"filename": meta["filename"], "mime_type": meta["mime_type"]},
    )
    claim.evidence.append(ev)
    store[claim_id] = claim

    return {
        "evidence_id": meta["id"],
        "url": meta["url"],
        "type": type,
        "vehicle": vehicle,
    }


@router.post("/{claim_id}/documents/extract")
async def extract_document(
    claim_id: str,
    file: UploadFile = File(...),
    doc_type: str = Form("auto"),
):
    """Upload and extract structured fields from a document."""
    claim = store.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found.", "retryable": False})

    meta = await storage.save_upload(claim_id, file, prefix="doc")
    result = document_extraction.extract(meta["path"], doc_type)

    ev = EvidenceRef(
        id=meta["id"],
        type="document",
        url=meta["url"],
        metadata={"document_type": result.get("document_type"), "extraction_confidence": result.get("confidence")},
    )
    claim.evidence.append(ev)
    store[claim_id] = claim

    return {
        "extracted_fields": result.get("extracted_fields", {}),
        "document_type": result.get("document_type", "unknown"),
        "confidence": result.get("confidence", 0.0),
        "issues": result.get("issues", []),
        "needs_confirmation": True,
        "evidence_id": meta["id"],
    }


@router.post("/{claim_id}/damage/analyze")
async def analyze_damage(
    claim_id: str,
    file: UploadFile = File(...),
    vehicle: str = Form("A"),
):
    """Upload and analyze a damage photograph."""
    claim = store.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found.", "retryable": False})

    meta = await storage.save_upload(claim_id, file, prefix="damage")
    result = damage_analysis.analyze(meta["path"], vehicle)

    # Store evidence
    ev = EvidenceRef(
        id=meta["id"],
        type="damage_photo",
        url=meta["url"],
        vehicle=vehicle,
        metadata={"analysis_confidence": result.get("overall_confidence")},
    )
    claim.evidence.append(ev)

    # Store detected damage in claim
    for dmg in result.get("damages", []):
        try:
            dd = DetectedDamage(
                zone=DamageZone(dmg.get("zone", "unknown")),
                part=dmg.get("part"),
                damage_type=DamageType(dmg.get("damage_type", "unknown")) if dmg.get("damage_type") else None,
                severity=Severity(dmg.get("severity", "unknown")) if dmg.get("severity") else None,
                confidence=dmg.get("confidence", 0.0),
                evidence_ids=[meta["id"]],
                confirmed_by_user=False,
                requires_more_photos=result.get("additional_images_required", False),
                requires_physical_inspection=result.get("requires_physical_inspection", False),
            )
            claim.detected_damage.append(dd)
        except (ValueError, KeyError):
            pass

    store[claim_id] = claim

    return {
        "damages": result.get("damages", []),
        "image_quality": result.get("image_quality", "unknown"),
        "additional_images_required": result.get("additional_images_required", False),
        "requires_physical_inspection": result.get("requires_physical_inspection", False),
        "overall_confidence": result.get("overall_confidence", 0.0),
        "error": result.get("error"),
        "evidence_id": meta["id"],
    }